"""yiri-collage soundtrack: dusty 90 bpm boom-bap (lofi recipe, sampled piano, vinyl) + paper / rubber-stamp sound design
locked to cues.json. All synthesised with lib/audio (mgaudio) and its CC0 samples; no external recordings.
Run: python3 demos/yiri-collage/audio.py  -> out/audio.wav (+ out/audio_spec.png)"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib', 'audio'))
import numpy as np
import mgaudio as mg
from mgaudio import recipes, sfx, fm, drums, samples
from mgaudio.core import Sound

D = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(D, 'cues.json')))
os.makedirs(os.path.join(D, 'out'), exist_ok=True)

m = recipes.lofi(bpm=90, key='F', drop=C['drop'], build=C['build'], outro=C['outro'], keys='piano', flavor='boombap', vinyl=True)
f = m.form
print('form', f.summary(), 'tracks', list(m.tracks))

def start_at(s, t):                                  # place a sound so its START (not its sync point) is at t
    return t + getattr(s, 'sync', 0.0)

def slap(t, gain=0.0, pan=0.0, seed=0, body=-8.0):   # paper slapped onto the page: paper hit + soft thud for weight
    m.sfx(sfx.sticker_slap(seed=seed), at=t, gain=gain, pan=pan)
    m.sfx(sfx.impact('thud', size=0.6, seed=seed), at=t, gain=body + gain, pan=pan)

# --- structure: the bed ducks under the "talking" car, a dead beat before the stamp, a lighter bed on the end card
m.mute(C['gap'][0], C['gap'][1] - C['gap'][0])
m.group('music').automate('gain', [(2.1, 0), (2.17, -3), (3.1, -3), (3.17, 0), (7.6, 0), (7.67, -2), (10, -2)])

# --- act 1: the photo slides in and is slapped down, taped, captioned
s = sfx.paper('slide', dur=0.34, seed=1); m.sfx(s, at=start_at(s, 0.0), gain=-2, pan=-0.5)
slap(C['slap_mother'], gain=2, pan=-0.35, seed=2, body=-5)
for i, t in enumerate(C['tapes']):
    s = sfx.tape_rip(dur=0.18, up=bool(i % 2), seed=10 + i); m.sfx(s, at=start_at(s, t - 0.12), gain=-5, pan=-0.4 + 0.5 * i)
slap(C['chip1936'], gain=-4, pan=-0.5, seed=3)
s = sfx.paper('slide', dur=0.36, seed=4); m.sfx(s, at=start_at(s, C['ad_in']), gain=-3, pan=0.6)
slap(C['slap_ad'], gain=1, pan=0.4, seed=5, body=-5)
slap(C['chip1960'], gain=-4, pan=0.6, seed=6)

# --- the car talks: a little klaxon voice on each lid flap + a paper slap for each speech scrap
horn = m.track('horn', level=-24, sends={'plate': -12}, lp=2600, group='sfx')
for i, (t, n, d) in enumerate(zip(C['hood'], ['A4', 'C5', 'F4'], [0.16, 0.16, 0.3])):
    horn.add(fm.brass(n, d, 0.85), t)
    horn.add(fm.brass(mg.theory.midi(n) + 4, d, 0.5), t)      # a major-third "two-tone" horn
    slap(t, gain=-4 + i, pan=0.25 - 0.15 * i, seed=20 + i, body=-11)
# the lemon pops out (comic cork pop + slide whistle on its arc) and lands with a soft paper thump
m.sfx(sfx.cork_pop(), at=C['lemon_pop'], gain=1, pan=0.3)
s = sfx.slide_whistle(up=False, dur=0.32, seed=7); m.sfx(s, at=start_at(s, C['lemon_pop'] + 0.02), gain=-6, pan=0.1)
slap(C['lemon_land'], gain=-3, pan=0.0, seed=8)

# --- build: the red band rips in (scraps swept off), the ink band slides, the giant stamp arrives and winds up
s = sfx.whoosh(0.3, 'cloth', direction=-1, seed=9); m.sfx(s, at=C['band_red'] + 0.06, gain=-2, pan=0.4)
m.sfx(sfx.tape_rip(dur=0.3, seed=11), at=C['band_red'], gain=-2, pan=0.5)
s = sfx.paper('slide', dur=0.3, seed=12); m.sfx(s, at=start_at(s, C['band_ink'] - 0.06), gain=-5, pan=-0.6)
s = sfx.whoosh(0.4, 'heavy', direction=1, seed=13); m.sfx(s, at=C['stamp_in'] + 0.1, gain=-3, pan=0.5)
for i in range(5):                                             # wood creaks / ticks while it rises (16ths)
    m.sfx(sfx.tick('wood').pitch(i * 1.5), at=C['windup'][0] + i / 6, gain=-10 + i * 1.5, pan=0.4)
m.sfx(sfx.reverse_cymbal(dur=0.9), at=C['gap'][0], gain=-4)   # swells into the silence

# --- HERO: the rubber stamp slams (rubber stamp + body thump + sub drop), paper confetti
m.sfx(sfx.stamp('rubber', seed=14), at=C['hero'], gain=3, pan=0.3)
m.sfx(sfx.impact('punch', seed=15), at=C['hero'], gain=-1, verb=-12)
_n = int(0.5 * 48000); _t = np.arange(_n) / 48000; _f = 58 * (34 / 58) ** (_t / 0.5)
m.sfx(Sound(np.sin(2 * np.pi * np.cumsum(_f) / 48000) * np.minimum(1, _t / 0.004) * np.exp(-_t * 3.0) * 0.7), at=C['hero'], gain=-5)
m.sfx(sfx.paper('crumple', dur=0.35, seed=16), at=C['hero'] + 0.03, gain=-5, pan=0.2)
s = sfx.whoosh(0.3, 'air', direction=1, seed=17); m.sfx(s, at=start_at(s, C['lift']), gain=-7, pan=0.5)
# pencil scribbles + the manicules slap in
m.sfx(sfx.pen('pencil', dur=0.4, seed=18), at=C['manicules'][0] - 1 / 6, gain=-7, pan=0.4)
slap(C['manicules'][0], gain=-4, pan=-0.7, seed=19)
slap(C['manicules'][1], gain=-4, pan=0.7, seed=30)
m.sfx(sfx.pen('pencil', dur=0.3, seed=31), at=C['manicules'][1], gain=-8, pan=-0.1)

# --- act 3: the new page slides over and slaps; four title scraps on 16ths (glock in key), the masthead taped down
s = sfx.paper('flip', dur=0.4, seed=32); m.sfx(s, at=start_at(s, C['sheet_in']), gain=-2, pan=-0.3)
slap(C['sheet_slap'], gain=2, pan=0.0, seed=33, body=-4)
ch = f.chord_at(C['title'][0]); top = sorted(ch)[-4:]
glock = m.track('glock', level=-26, sends={'plate': -10}, group='sfx')
for i, t in enumerate(C['title']):
    slap(t, gain=-2 + i * 0.6, pan=[-0.3, 0.3, -0.3, 0.3][i], seed=40 + i, body=-10)
    glock.add(fm.bell(top[i % len(top)] + 12, 0.5, 0.65, 'glock'), t)
m.sfx(sfx.tape_rip(dur=0.25, seed=45), at=C['masthead'] - 0.05, gain=-4)
slap(C['masthead'], gain=-1, seed=46, body=-7)
m.sfx(samples.hit('woodblock', vel=0.5), at=C['masthead'] + 2 / 3, gain=-12)

res = m.export(os.path.join(D, 'out', 'audio.wav'), spectrogram=os.path.join(D, 'out', 'audio_spec.png'))
print({k: res[k] for k in ('duration', 'lufs', 'true_peak', 'stereo_corr', 'warnings') if k in res})
