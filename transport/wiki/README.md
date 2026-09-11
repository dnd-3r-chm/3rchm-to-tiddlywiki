# D&D 3R TiddlyWiki（Node.js 版）

D&D 3R CHM「大不全」迁移到 TiddlyWiki 的产物目录。

> **工程状态与全部约定的权威来源是 [`../contexts.md`](../contexts.md)。**
> 接手工作或新开会话时，请先完整阅读该文件。本文件只说明本 wiki 目录的用法。

## 启动

在仓库根目录（`E:\dnd3r_full`）执行：

```bash
tiddlywiki transport/wiki --listen port=8080
```

访问 <http://127.0.0.1:8080/>。

服务默认保持关闭，由用户手动启动；修改内容后脚本不会自动拉起服务。

## 目录说明

```text
wiki/
├── tiddlywiki.info          # TiddlyWiki 配置（语言 zh-Hans）
└── tiddlers/                # 所有 .tid 与图片，按源目录存放
    ├── 0 核心三宝书/         # PHB玩家手册 / DMG城主指南 / MM怪物图鉴
    ├── 10 附录/              # html教学 / 武器附魔测评 / 职业心得
    ├── *.tid                # 根目录页面（前言、译者名录、如何使用大不全）
    ├── $__*.tid             # 系统/导航配置（手动维护）
    ├── 总目录.tid
    ├── CHM目录侧边栏.tid
    ├── cascading_stylesheet.css.tid
    └── 标题配色.tid
```

- 内容页 `.tid` 由 `transport/work/convert_book.py` / `convert_root.py` **直接写入本目录**，
  按源文件相对路径分目录存放，**无需手工复制**。
- 图片为二进制 Tiddler，每张图片旁必须有同名 `.meta`，将标题锁定为相对路径。

## 当前内容

全部 0~11 系列均已搬运完毕（截至 2026-09-09，`11 其他资源/` 龙晶 38 篇收官）。
内容 Tiddler（含图片 `.meta`）合计约 **4788 个**，精确数量以 [`../contexts.md`](../contexts.md) §2「当前进度」为准。

> 详细的逐书 Tiddler 数 / 图片数、手动合并说明见 [`../contexts.md`](../contexts.md) §2「当前进度」与 §7「手动调整记录」。
> 本文件只说明 wiki 目录用法，不重复进度日志。

## 注意事项

- 以下文件为**手动维护，任何脚本不得覆盖**：
  - `$__tags_SideBar.tid`（侧边栏标签页顺序）
  - `$__DefaultTiddlers.tid`（默认首页）
- `标题配色.tid` 由 `work/gen_styles.py` 生成，**勿手动编辑**；改色请改脚本常量后重跑。
- 重跑 `generate_toc.py` 只更新 `总目录` 与 `CHM目录侧边栏`，不会改动手动维护文件。

## 迁移进度与工作流

见 [`../contexts.md`](../contexts.md) §2「当前进度」、§5「关键约定」，
以及 [`../搬运计划.md`](../搬运计划.md)。
