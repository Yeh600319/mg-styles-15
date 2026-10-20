"""yiri-lineart soundtrack: felt piano + soft strings in E major, a pen-on-paper whisper whose loudness follows the pen-tip
speed (timing.json, dumped from the page by tools/timing.mjs), a chime on the line-to-fill, a soft snap on the break-out.
All synthesised with lib/audio (mgaudio) and its CC0 samples.  Run: python3 demos/yiri-lineart/audio.py -> out/audio.wav"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib', 'audio'))
import numpy as np
import mgaudio as mg
from mgaudio import sfx, synth, fm, samples, filters

D = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(D, 'cues.json')))
TM = json.load(open(os.path.join(D, 'timing.json')))
os.makedirs(os.path.join(D, 'out'), exist_ok=True)
SR = 48000
PC = C['pieces']; CAR, FRAME, ESC = PC['car'][0], PC['frame'][0], PC['escape'][0]
FILL, BREAK, TEXT, MAST = C['fill'][0], C['break'], C['text'], C['masthead']

m = mg.Mix(duration=10.0, bpm=72)
m.group('music').level = -20
EQ_WARM = lambda a: filters.eq(a, [('pk', 300, -3, 1.0)])

CH = [  # (start, end, voicing): Emaj9 → C#m9 → Amaj9 → B6/9 (held, unresolved through the hesitation) → Emaj9 on the text
    (0.0, CAR, [52, 59, 63, 66, 68]),
    (CAR, FRAME, [49, 56, 59, 63, 64]),
    (FRAME, FILL, [45, 57, 61, 64, 68, 71]),
    (FILL, TEXT, [47, 54, 59, 61, 66, 68]),
    (TEXT, 10.0, [40, 52, 59, 63, 66, 71]),
]

# ---- felt piano: a low E under the first stroke, a rising line as the figure is drawn, chords on each new piece
piano = samples.inst('piano')
piano.items = [i for i in piano.items if os.path.exists(os.path.join(samples.ROOT, i['file']))]   # index.json lists a few files the repo does not ship
pn = m.track('piano', level=-20, sends={'hall': -8}, hp=70, lp=5200, fx=[EQ_WARM])
def note(t, n, vel=0.4, dur=2.4): pn.add(piano.play(n, dur=dur, vel=vel, release=0.8), max(0.0, t))
note(0.0, 28, 0.48, 2.0); note(0.0, 40, 0.34, 2.0)
for t, n in [(0.55, 68), (1.25, 71), (1.95, 73), (2.65, 76)]: note(t, n, 0.36)          # G#4 B4 C#5 E5 as she appears
note(CAR, 37, 0.34, 3.0); note(CAR, 64, 0.3, 2.4); note(CAR + 0.9, 71, 0.3, 2.0)
note(FRAME, 33, 0.36, 3.0); note(FRAME, 45, 0.28, 3.0)
for i, n in enumerate([61, 64, 68, 73]): note(FRAME + 0.36 * (i + 1), n, 0.26 + 0.04 * i, 1.8)   # one note per frame corner
for n, v in [(35, 0.42), (47, 0.36), (66, 0.3), (71, 0.3)]: note(FILL, n, v, 2.6)               # the fill: B6/9, open
for n, v in [(28, 0.5), (40, 0.46), (59, 0.36), (63, 0.34), (68, 0.36), (75, 0.32)]: note(TEXT, n, v, 2.6)   # resolve on the question
note(MAST, 83, 0.26, 1.6)

# ---- strings + air (no swell on frame 0; the film opens on the ink)
st = m.track('strings', level=-23, sends={'hall': -6}, hp=160, fx=[EQ_WARM])
for a, b, v in CH:
    st.add(synth.pad([n + 12 for n in v[1:4]] + [v[0]], (b - a) + 0.6, 0.7, 'strings', attack=0.5, release=0.8, seed=int(a * 10)), a)
st.automate('gain', [(0, -22), (0.8, -14), (CAR, -9), (FRAME, -5), (FILL, 0), (BREAK, -1), (TEXT, -3), (9.2, -6), (10, -14)])
st.automate('lpf', [(0, 1400), (FRAME, 3600), (FILL, 8000), (10, 5000)])
air = m.track('air', level=-28, sends={'hall': -4}, fx=[EQ_WARM])
for a, b, v in CH:
    air.add(synth.pad(v, (b - a) + 0.8, 0.6, 'air', attack=0.6, release=0.9, seed=7 + int(a)), max(0.0, a - 0.05))
air.automate('gain', [(0, -40), (0.3, -28), (1.0, 0), (10, 0)])
m.track('sub', level=-27).add(synth.bass('E1', 2.2, 0.7, 'sub'), TEXT)
# a held breath while the pen hesitates at the corner, the music returns on the break; master tail from 9.3 s
m.group('music').automate('gain', [(0, 0), (6.75, 0), (6.95, -7), (BREAK - 0.02, -7), (BREAK + 0.06, 0), (9.3, 0), (9.75, -6), (10, -18)])

# ---- pen whisper: band-passed paper noise, loudness from the pen-tip speed (same timing as the picture)
n = 10 * SR
rng = np.random.default_rng(3)
noise = rng.standard_normal(n).astype(np.float32)
noise = np.asarray(filters.bpf(noise, 1200, 5200), dtype=np.float32) + 0.35 * np.asarray(filters.hpf(noise, 6000), dtype=np.float32)
sp = np.array(TM['speed'], dtype=np.float32)
env = np.interp(np.arange(n) / SR, np.arange(len(sp)) / TM['hz'], np.sqrt(np.clip(sp / 1400.0, 0, 1.6)))
env[int(ESC * SR) + int(0.5 * SR):] *= np.linspace(1, 0, n - int(ESC * SR) - int(0.5 * SR)) ** 2   # the pen leaves the page
grain = 1 + 0.35 * np.asarray(filters.lpf(rng.standard_normal(n).astype(np.float32), 30), dtype=np.float32) * 6   # paper tooth
w = noise * env * np.clip(grain, 0.3, 2.0)
pen = mg.Sound(np.stack([w, w * 0.92 + 0.08 * np.roll(w, 37)], axis=1) / (np.abs(w).max() + 1e-9) * 0.5)
m.track('pen', level=-27, group='sfx', sends={'room': -14}).add(pen, 0.0)
m.sfx(sfx.pen('pencil', dur=0.12, seed=2), at=0.0, gain=-6)                                   # the nib touches down on frame 0

# ---- punctuation
ce = m.track('celesta', level=-15, sends={'hall': -7, 'delay': -16}, group='sfx')
ce.add(fm.bell(80, 1.4, 0.4, 'celesta'), 2.65)                                                 # her head closes
ce.add(fm.bell(83, 1.4, 0.4, 'celesta'), FRAME - 0.05)                                         # the car is done
m.sfx(sfx.chime(('B5', 'D#6', 'F#6', 'B6'), step=0.08, kind='celesta'), at=FILL, gain=-3)      # line → fill
m.sfx(sfx.shimmer_hit('B5'), at=C['car_fill'][0], gain=-9)
m.sfx(sfx.click('wood'), at=BREAK, gain=-3, pan=0.2)                                           # the snap: the line refuses to close
m.sfx(sfx.pen('pencil', dur=0.18, seed=5), at=BREAK, gain=-4, pan=0.2)
s = sfx.whoosh(0.7, 'air', direction=1, seed=6); m.sfx(s, at=BREAK + 0.45, gain=-8, pan=0.6)   # out of the frame
m.sfx(fm.bell(87, 1.6, 0.35, 'celesta').loud(-20), at=MAST, gain=-6)

res = m.export(os.path.join(D, 'out', 'audio.wav'), spectrogram=os.path.join(D, 'out', 'audio_spec.png'))
print({k: res[k] for k in ('duration', 'lufs', 'true_peak', 'stereo_corr', 'warnings') if k in res})
