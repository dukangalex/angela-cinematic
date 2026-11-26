# angela-cinematic

纯代码绘制的解说纪录片引擎：没有拍摄、没有生成式视频，
每一帧都由 Python＋Skia 按旁白的时间轴画出来——连续运镜扫过一面
「设计世界」，大字、印章、计数器、荧光笔标注逐词对齐旁白落点。

**中文优先**：本仓的第一受众是中文人群。引擎的逐词对齐、台词切分、
字幕分块都已改成文字体系无关的计量（见下方「中文适配」），
中文示例与英文示例同为一等公民。

## 管线

```
script.json（台词本）
  → make_beats.py      节拍表（先审后渲）
  → 配音 takes          任意 TTS 或真人录音，一 take 一文件
  → split_takes.py     按静音切句、量语速
  → build_narration.py 旁白轨 + timing.json
  → scene.py           画面编排（镜头、元素、逐词触发全写在这里）
  → render.py          逐帧渲染出片
  → build_sfx.py / mix_soundtrack.py / burn_captions.py（收尾：音效、混音、字幕）
```

图片素材只从 Wikimedia Commons 取，逐张记录许可证（fetch_commons.py）。

## 快速开始

```bash
pip install -r requirements.txt        # 另需 ffmpeg/ffprobe 在 PATH
python3 engine/check_setup.py          # 自检（含系统库提示）
# 英文示例（莱特兄弟，89 秒）
cp -r examples/wright-en my-film && cd my-film
python3 ../engine/fetch_commons.py get --project .
python3 ../engine/make_map.py --project . && python3 ../engine/prep_assets.py --project .
# 配音：把每 take 的 WAV 放进 audio/takes/（或用 tts_say.py 的草稿声）
python3 ../engine/split_takes.py --project . && python3 ../engine/build_narration.py --project .
python3 ../engine/render.py --project . --size 1280x720 --out out/draft.mp4 --audio audio/narration.m4a
```

中文示例在 `examples/wright-zh/`，同题材同结构，
script 与 scene 已全中文化，字体已随仓附带（见其 README）。

## 中文适配（本仓相对上游的改动）

上游引擎有三处写死了拉丁字母假设，中文喂进去会崩或全错位，本仓逐一替换：

1. **逐词对齐**（engine.py 的 `W()`）：原按 `[a-z]` 数字母占比，
   中文一行字母数为 0，所有触发点塌到行首。改为按全部文字字符
   （`str.isalnum()`，汉字计 1）占比，英文行为不变。
2. **台词切分**（split_takes.py）：原权重只数 A–Z，中文行权重为 0
   直接除零崩溃。改为同一通用计量，并给中文标点（，。、；。！？）
   配上与英文逗号、句号相当的停顿当量。
3. **字幕分块**（captions.py）：原按空格分词，中文整句成一词。
   改为脚本无关的切分（拉丁词成词、其余逐字），中文块长按字数放宽，
   断句标点补全中文标点，词间空格只出现在拉丁词之间。

## 风格预设

`styles/` 收录 11 种风格口径（证据墙＋绘图仪、白板、粉笔、火柴人、
等距、伪 3D、信息图、地图之旅、产品、涂鸦），写 scene 前先选一份。

## 部署配置

声线、代理、字体、渲染机器这类环境选择不写死在引擎里，
统一写在 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)，换机器改配置即可。

## 来源与许可

本仓是自有化整合：引擎源自 Moh4696/cinematic-skill（MIT），
风格体系按 motalim-ai/motion-starter-kit（MIT）的公开说明在本引擎中
重新表达。细目与致谢见 [CREDITS.md](CREDITS.md)，
上游许可证原文在 `licenses/`。
