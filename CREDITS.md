# 来源与致谢（CREDITS）

angela-cinematic 是 dukangalex 名下的自有化整合项目：
自有命名、自有文档、与上游脱钩独立维护。整合的两处来源如下，
许可证义务照原文履行，推广性内容不收录。

## 引擎：cinematic-skill

- 作者：Moh4696（https://github.com/Moh4696/cinematic-skill）
- 许可：MIT，原文见 `licenses/cinematic-skill-MIT.txt`
- 收录范围：`engine/` 全部脚本（Skia 逐帧渲染引擎与管线工具）、
  `examples/wright-en` 示例、纹理与字体获取方式
- 本仓改动：中文适配三处（见 README「中文适配」）、部署配置外置

## 风格体系：motion-starter-kit

- 作者：motalim-ai（https://github.com/motalim-ai/motion-starter-kit）
- 许可：MIT（原文见上游仓库）
- 收录范围：仅其 `styles/` 的 10 种风格之**设计说明**
  （plotter、whiteboard、chalkboard、stickman、isometric、fake3d、
  infographic、map-journey、product、doodle）
- 本仓处理：按公开说明把每种风格的配色、底面、镜头与文字口径
  **在本引擎里重新写成预设**（`styles/*.md`），未搬用其
  Remotion/React 代码与媒体文件

## 字体

- Bebas Neue（SIL OFL 1.1）、Homemade Apple（Apache-2.0）——英文默认
- 站酷黄油体 ZCOOL QingKe HuangYou（SIL OFL 1.1）——中文展示体
- 马善政 Ma Shan Zheng（SIL OFL 1.1）——中文手写标注体

## 素材

- 示例照片来自 Wikimedia Commons，逐张许可证记录在各示例的
  `photos.json` 与项目内 `assets/prep/photos/meta.json`
