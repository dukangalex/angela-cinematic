# 示例：十二秒（中文版）

莱特兄弟首飞的 74 秒解说纪录片，与英文示例同题材、同结构，
台词、画面文字、逐词触发点全部中文化——本仓中文适配的验收示例。

- `script.json`：中文台词本（19 句，5 个 take）
- `scene.py`：画面编排，展示文字与 W() 触发词均为中文
- `fonts/`：站酷黄油体（cond 槽）＋马善政体（hand 槽），OFL 许可
- `photos.json` / `map.json`：素材与地图清单（照片走 Commons，逐张记许可证）

## 跑起来

```bash
E=../../engine
python3 $E/fetch_commons.py get --project .
python3 $E/make_map.py --project . && python3 $E/prep_assets.py --project .
# 配音：按 docs/DEPLOYMENT.md 的声线配置逐句合成云扬 takes，
# 一 take 一 WAV 放进 audio/takes/（句间留 ≥0.6 秒静音）
python3 $E/split_takes.py --project . && python3 $E/build_narration.py --project .
python3 $E/render.py --project . --size 1280x720 --out out/draft.mp4 --audio audio/narration.m4a
```

两份历史文件（1899 年的信、1903 年的《纽约时报》社论）在画面里
保留英文原件——那是文物照片本身，不是漏译。
