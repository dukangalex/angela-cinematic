# 部署配置（DEPLOYMENT）

引擎本体保持环境中立：声线、代理、字体、机器参数都属于部署配置，
写在这里，换环境只改这一页，不要改引擎代码。

## 声线

| 用途 | 声线 | 通道 | 语速 |
|---|---|---|---|
| 中文正式配音 | zh-CN-YunyangNeural（云扬） | Edge TTS | +30% |
| 英文正式配音 | en-US-AndrewNeural（Andrew） | Edge TTS | +30% |
| 草稿定时声 | espeak-ng（本机） | tts_say.py 自带 | 默认 |

- takes 的约定：一条 take 一个 WAV，放 `audio/takes/<take 名>.wav`，
  take 内各句之间留 ≥0.6 秒静音，split_takes 按静音切句。
- 逐句合成再拼 take（而不是整 take 一次合成）能保证切句点干净。

## 代理

- Edge TTS 走 WebSocket，**必须走真隧道型代理**（自有节点出口）。
  经 TLS 中间人代理时握手会被打断（实测 Invalid connection header）。
- 本机部署：专用节点 sing-box 客户端在 `~/workspace/proxy-node/`
  （mixed 入口 127.0.0.1:18080），edge-tts 用 `--proxy http://127.0.0.1:18080`。
- Wikimedia Commons、字体与地图数据的下载走普通 HTTPS 代理即可。

## 字体

项目内 `fonts/` 两槽：`cond.ttf`（展示大字）、`hand.ttf`（手写标注）。

| 语言 | cond 槽 | hand 槽 | 许可证 |
|---|---|---|---|
| 英文默认 | Bebas Neue | Homemade Apple | OFL / Apache-2.0 |
| 中文默认 | 站酷黄油体 ZCOOL QingKe HuangYou | 马善政 Ma Shan Zheng | 均 OFL |

- 中文字体已随 `examples/wright-zh/fonts/` 附带，含 LICENSES.txt。
- 换字体只换这两个文件，引擎不感知字体名。

## 渲染机器

- 纯 CPU 逐帧渲染：720p 约 0.8–0.9 帧/秒/工人（1.5 核共享云机实测，
  89 秒片约 19 分钟）；普通笔记本 1080p 约 6 分钟（上游口径）。
- 内存按分辨率自动定工人，见 check_setup.py 输出。
- 渲染产物默认近无损、体积大，交付前用 ffmpeg 转一版
  CRF 26 左右的分发版（89 秒 720p 约 36 MB）。
