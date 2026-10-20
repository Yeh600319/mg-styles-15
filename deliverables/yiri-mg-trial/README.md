# 异日观察室 2026-10-20 · MG 风格试做（两支 10 秒）

| 文件 | 风格 | 源码 |
|---|---|---|
| `yiri-collage-10s.mp4` + `yiri-collage-10s-contact.jpg` | 06 拼贴剪贴 | `demos/yiri-collage/` |
| `yiri-lineart-10s.mp4` + `yiri-lineart-10s-contact.jpg` | 02 一笔线稿 | `demos/yiri-lineart/` |

规格（两支相同）：1920×1080，30 fps，10.000 s（300 帧），H.264 + AAC 48 kHz 立体声；响度 −14.0 / −14.1 LUFS，峰值 −1.2 / −1.3 dBFS。

重新渲染（仓库根目录）：
```bash
export MG_CHROME=<chromium 路径> MG_GPU_ARGS="--no-sandbox"
python3 demos/yiri-collage/audio.py && node harness/render.mjs demos/yiri-collage --workers 4
node demos/yiri-lineart/tools/timing.mjs && python3 demos/yiri-lineart/audio.py && node harness/render.mjs demos/yiri-lineart --workers 4 --mb 3
```

自评（rubric.md 七项，第 1 轮 → 修改后）
| | 风格 | 概念 | 动效 | 设计/字 | 质感 | 声音 | 技术 |
|---|---|---|---|---|---|---|---|
| 拼贴 | 7 → 7.5 | 6 → 6.5 | 6.5 → 7 | 6.5 → 7 | 7 | 7 | 8.5 |
| 线稿 | 7 → 7.5 | 6.5 → 7 | 6.5 → 7 | 6 → 7 | 6.5 → 7 | 7 | 8.5 |
