# D&D 3R CHM → TiddlyWiki 迁移上下文

> 本文件用于在新窗口/新会话中快速恢复当前项目状态。
> 工作目录：`E:\dnd3r_full`

## 0. 给接手 AI 的快速上手

1. **先完整读本文件**——工程状态与全部约定的权威来源（持续维护，永远最新）。
2. 若在 DSH 环境继续，可检索记忆库获取技术经验（`memory_project dnd3r_full`，含 lesson/fact：TiddlyWiki 5.4.1 的坑与模式——data-tags 去括号、specificity 前缀、全角替换 title 同步、虚拟 source、合并参考 hhc 等）。
3. 关键铁律（详见 5/6/8 节）：
   - 手动调整节点以用户为准；**合并节点必须参考 hhc**（子节点范围与顺序），其他手动调整不对照 hhc
   - 手动调整后必须三步同步：SKIP_TITLES（目录隐藏被删节点）+ SKIP_SOURCES（防重转覆盖，**含手动调整过的父节点源**）+ 重跑 `generate_toc.py` + 更新本文件
   - 手动新建无源节点：`MANUAL_CHILDREN` 注入目录 + 虚拟 source（指向不存在的 .htm）
   - **不要用 `convert_book.py` 全量重转已手动调整过的文件**
4. 启动：`tiddlywiki transport/wiki --listen port=8080`（服务保持关闭，由用户手动启动）
5. 待办：下一批搬运 `1 核心补充书籍/`（三宝书已全部完成）

## 1. 项目目标

将 `E:\dnd3r_full`（CHM 解压目录）中的内容逐步搬运到 TiddlyWiki：

- 使用 **Node.js 版 TiddlyWiki 5.4.1**
- 最终 wiki 位于 `transport/wiki/`
- 按书/分类逐步搬运，不一次全量转换
- 右侧边栏提供类似 CHM 的可折叠目录

## 2. 当前进度

已完成搬运：

- 根目录页面：3 个
  - `前言`
  - `如何使用大不全`
  - `译者名录`
- `10 附录/`：33 个 HTML 页面（含 `html教学`、`武器附魔测评`、`职业心得`）
- `0 核心三宝书/PHB玩家手册`：117 个页面（**全本已排版完成**，含 `11法术/法术描述` 手工重排，见 5.5b）
- `0 核心三宝书/DMG城主指南`：806 个页面
- `0 核心三宝书/MM怪物图鉴`：400 个页面（含 192 张图片，已清理 class="page"/class="title"）

尚未搬运：

- 其他核心补充书籍、完美系列、世设等（建议下一批从 `1 核心补充书籍/` 开始）

当前 wiki Tiddler 数量 **1293 个**：内容页 1280 + 系统/导航/样式 13；另有图片 Tiddler 200 个（194 jpg + 6 png，均配 `.meta`）。
三宝书 Tiddler 明细：DMG 727（源 806，差额为手动合并）、MM 400、PHB 117。

## 3. 目录结构

```text
E:\dnd3r_full\transport\
├── contexts.md                  # 本文件
├── 搬运计划.md                  # 详细搬运计划
├── work/                        # 中间产物与脚本
│   ├── inventory.csv            # 源文件清单
│   ├── hhc_mapping.csv          # Contents.hhc 解析结果
│   ├── final_mapping.csv        # 源文件 -> 唯一 Tiddler 标题/标签映射
│   ├── convert_pilot.py
│   ├── convert_book.py          # 按目录/书批量转换
│   ├── convert_root.py          # 根目录页面转换（含内联样式）
│   ├── clean_spell_tids.py      # PHB 法术描述重排版（手工清洗，对齐 A.tid；已在 convert_book SKIP_SOURCE_PREFIXES 防覆盖）
│   ├── clean_dmg_classes.py     # DMG 多余 class 清理
│   ├── generate_toc.py          # 生成总目录/侧边栏目录
│   ├── gen_styles.py            # 生成「标题配色」样式 Tiddler（每本书标题字色）
│   ├── fix_wiki_links.py        # 修复 TiddlyWiki 链接参数写反
│   └── ...其他辅助脚本
├── wiki/                        # Node.js TiddlyWiki
│   ├── tiddlywiki.info
│   └── tiddlers/                # 所有 .tid 与图片，按源目录存放
└── logs/
    ├── 转换日志.log             # convert_book.py 落盘日志（UTF-8，追加写入）
    └── link-report.csv          # 全库正文链接校验结果（_verify_links.py 生成）
```

## 4. 常用命令

### 启动 TiddlyWiki

```bash
tiddlywiki transport/wiki --listen port=8080
```

访问：`http://127.0.0.1:8080/`

### 转换一本书/目录

```bash
python transport/work/convert_book.py "0 核心三宝书\DMG城主指南"
python transport/work/convert_book.py "0 核心三宝书\PHB玩家手册"
python transport/work/convert_book.py "10 附录"
```

### 转换根目录

```bash
python transport/work/convert_root.py
```

### 重新生成侧边栏目录

```bash
python transport/work/generate_toc.py
```

### 生成标题配色样式（每本书标题字色）

```bash
python transport/work/gen_styles.py
```

### 清理 Word/旧 HTML

```bash
python transport/work/clean_spell_tids.py
python transport/work/clean_dmg_classes.py                # 缺省 DMG
python transport/work/clean_dmg_classes.py "E:\...\MM怪物图鉴"  # 可传其他书籍目录
```

### 修复链接参数写反

```bash
python transport/work/fix_wiki_links.py
```

## 5. 关键约定

### 5.1 Tiddler 存放

- `.tid` 文件按源文件相对路径存放在 `wiki/tiddlers/` 下。
- 例如：`0 核心三宝书/PHB玩家手册/2种族/人类.htm`
  → `wiki/tiddlers/0 核心三宝书/PHB玩家手册/2种族/人类.tid`

### 5.2 标题格式（2026-08-30 起为新格式）

- 书内节点：`具体标题 (书目缩写-书名)`，例如 `简介 (DMG-城主指南)`、`红龙 (MM-怪物图鉴)`
- 无缩写节点：`具体标题 (所属内容)`，例如 `版本历史 (附录)`（**所属内容为 10 附录时不写序号**）、`开始之前 (html教学)`
- 根目录节点：`标题`（2026-08-30 起不再加「龙与地下城3版扩展规则大全 - 」前缀，如 `前言`）
- 重名消歧后缀插在标题部分（括号后缀之前），如 `厄兰(厄兰) (XPH-扩展灵能手册)`
- 旧格式 `[缩写] 标题` 已于 2026-08-30 全库重命名（1315 文件/1314 标题，链接同步无断链；旧 final_mapping 备份 `final_mapping.csv.old-title-format`，重命名工具 `work/rename_titles.py`）
- 规则实现在 `work/build_mapping.py` 的 `build_title()`

### 5.3 标签

- **只保留两级标签**：书目分类（一级目录）+ 书名/模块（二级目录），不细分到章节。
- 例如：
  ```
  0 核心三宝书\MM怪物图鉴\第一章：怪物\D\真龙\红龙.htm
      -> [[0 核心三宝书]] [[MM怪物图鉴]]
  10 附录\html教学\开始之前.htm
      -> [[10 附录]] [[html教学]]
  10 附录\版本历史.htm（分类下直接文件）
      -> [[10 附录]]
  前言.htm（根目录页面）
      -> 无标签
  ```
- 标签规则定义在 `work/build_mapping.py` 的 `path_to_tags()`（只取前两级目录）。
- 批量重打标签：`python transport/work/retag_tids.py`（幂等，按 final_mapping.csv 的标签列更新所有含 source 的 .tid）。

### 5.4 图片

- 图片作为二进制 Tiddler 放入 `wiki/tiddlers/` 对应子目录。
- 每个图片旁必须有 `.meta` 文件，将标题设为相对路径，例如：
  ```text
  title: 0 核心三宝书/DMG城主指南/封面.jpg
  type: image/jpeg
  ```

### 5.5 HTML 清洗规则

- 以 `·` 开头的 `<p>` 段落转换为 `<ul><li>`（用户规则，2026-08-30；存量已替换 6 文件/23 处，连续多个合并为一个 ul，工具 `bullet_p_to_ul.py`；转换管道 `clean_html()` 已加同规则）
- `<strong>` 替换为 `<b>`（用户规则，2026-08-30；存量已全库替换 151 文件/3084 标签，工具 `strong_to_b.py`；转换管道 `clean_html()` 已加同规则）
- 全角引号 `“”` 替换为半角 `""`、全角括号 `（）` 替换为半角 `()`（用户规则，2026-09 起对后续迁移生效；实现于 `convert_pilot.py` 的 `normalize_fullwidth_punct()`，在 `clean_html()` 末尾调用；不处理其他全角标点与单引号）
- **现有内容已批量补齐**（`clean_fullwidth_punct.py`，1007 文件/46428 处，跳过 `$__` 系统与手动维护文件）；标题含全角字符的 43 个页面 title 同步变化，链接两侧同步替换无断链；`hhc_mapping.csv`/`final_mapping.csv` 标题类列已同步替换（备份 `.fullwidth-backup`），`build_mapping.py` 输出前也做替换（防重建恢复全角）；`generate_toc.py` 重跑生成的目录为半角，与现有内容一致
- 表格节点（文件名 `表X-X`）内的 `<span>` 采用 **unwrap**（去标签留文字），按属性分两类处理（用户规则，2026-08-31）：
  - **CLASS 型已全部清理（66 处 / 12 文件）**：`class="price"`(41)、`note-ref`(16)、`ref-table`(3)、`note-label`(3)、`sub-cat`(2)、`note`(1)，以及裸 `<span>`(3)。全局样式表无定义，属失效属性，清理后渲染不变。工具 `work/clean_spans.py --kind class`
  - STYLE 型已清理（29 处 / 12 文件，用户确认 2026-09-01）：`font-weight:600`(18，注释号加粗)、`font-weight:400;color:#555`(5，表头补充淡化)、`font-weight:400;font-size:12px`(4)、`font-weight:400;color:#555;font-size:.7rem`(2) 等。**全部 12 个文件的 span 已归零**，视觉层次消失，待用户手动调整（计划改用全局 CSS 统一控制）
- 表格行内格式 `class="g"`/`"l"`/`"w"` 一律清除（用户规则，2026-08-31；源表格页内联 `<style>` 定义的斑马纹 `.g`/`.w` 与首列标签 `.l`，因 `<style>` 被剥离且全局样式表无定义而失效；存量已清理 DMG 7 文件/156 处，工具 `work/clean_table_classes.py`，转换管道 `clean_html()` 已加 `strip_table_classes()`）。多值 class 只剔除目标值（如 `class="l bold"` → `class="bold"`）
- **同类残留（未清理，待用户决定）**：DMG 仍有 291+ 处其他失效 class，主要是 `a`/`c`/`dc`（列样式）、`sub`/`note`（副标题/注释）、`bold`，以及 MM 的 277 处 g/l/w（223 个 `<div class="w">` + 骷髅/火蜥蜴的 54 个 `class="l"`）。清理方式：扩展 `clean_table_classes.py` 的 `TARGETS` 后执行 `--scope mm`（全库则不带参数）
- 移除 `<script>`、`<style>`（根目录节点除外，根目录使用内联样式）
- HTML 标签名统一小写
- 自动补全 `<li>` 闭合标签
- 自动修复标题闭合不匹配，如 `<h5>...</h6>` → `</h5>`
- 旧式 `div + button + onclick` 折叠块统一转换为：
  ```html
  <details>
    <summary style="...按钮样式...">标题</summary>
    ...内容...
  </details>
  ```

### 5.5b 法术描述重排版（PHB，2026-09-01）

- 目录 `0 核心三宝书/PHB玩家手册/11法术/法术描述` 下为按首字母归类的法术节点（A、B、C…Z）。
- 原始 CHM 内容含大量 Word/HTML 噪音（`<div style='layout-grid...'>`、`<p style='text-indent...'>`、嵌套 `<b><span style=...>>`、`<o:p>`、`&nbsp;` 等），风格与已干净的 `A.tid`（参照格式）不一致。
- 已用 `work/clean_spell_tids.py`（重写版）对除 `A.tid`（参照）、`法术描述.tid`（已干净）外的 **22 个节点**做手工重排版，统一对齐 `A.tid`：
  - 剥离 `style=`/`class=`/`<span>`/`<div>`/`<o:p>`/`<font>` 等标签（残留 0 处）
  - `中文名(English Name)` 段落 → `<h5>中文名 (English Name)</h5>`（半角括号，中文后补空格）
  - 字段行规整为 `<p><b>字段：</b>值</p>`（等级/法术成分/施法时间/距离/目标/影响区域/持续时间/豁免检定/法术抗力等），含把 `<b>字段</b>：值` 前移为 `<b>字段：</b>值`
  - 学派括号统一：全角 `〔〕`→`[]`、全角 `（）`→半角 `()`，中文与 `(` 间补空格
  - 合并相邻斜体/加粗边界：`</i><i>`、`</b><b>`（如 `<i>奥术材料</i><i>成分：</i>` → `<i>奥术材料成分：</i>`）
  - 严格保留 `.tid` 头部 4 行 metadata（title/tags/source/type），只对正文清洗
  - 运行前已备份整目录至 `法术描述_backup_20260901_174546`
- **这是手工清洗成果，非管道自动产出**：`convert_book.py` 重转 PHB 会用原始 CHM 内容覆盖这些 `.tid`，破坏已清洗排版。
- PHB 全本已排版完成（含本目录），已在 `convert_book.py` 的 `SKIP_SOURCE_PREFIXES` 加入整本书前缀 `0 核心三宝书\PHB玩家手册\`，**后续搬运 PHB 整本自动跳过**（与 DMG 手动调整父节点同理）。**不要移除该跳过项，也不要用 `convert_book.py` 重转 PHB 任何页面。**

### 5.6 根目录节点样式

根目录节点不再使用内联字色（h1-h6 的 color 已移除，改由全局「标题配色」规则控制，见 5.8），
`apply_root_inline_styles.py` 只保留布局内联样式：

- `table`：`width:100%;border-color:transparent`
- `td`：`width:16.67%;border-color:transparent`

（源 HTML 自带的内容强调色如狮鹫注 maroon、版本号 teal 属于内容本身，保留不动）

### 5.7 全局样式

- 全局样式 Tiddler：`wiki/tiddlers/cascading_stylesheet.css.tid`
- 标签：`$:/tags/Stylesheet`
- 内容参考原 `cascading_stylesheet.css`
- `<th>` 与 `<td>` 相同边框/内边距格式，另加 `font-weight: bold`（用户规则 2026-08-30）

### 5.8 标题配色（每本书标题字色）

- 样式 Tiddler：`wiki/tiddlers/标题配色.tid`（title `标题配色`，type `text/css`，tag `$:/tags/Stylesheet`）
- 由 `work/gen_styles.py` 生成，**勿手动编辑**（重跑覆盖），改色改脚本中的常量/字典后重跑即可，wiki 刷新即生效
- 规则（CSS 级联顺序，后者覆盖前者）：
  1. 默认：所有页面 h1-h6 标题 `maroon`（未单独指定颜色的书）
  2. 按书覆盖：`gen_styles.py` 的 `BOOK_COLORS`，选择器 `[data-tags*="书标签"] h1-h6`（**不带 [[ ]] 括号**——已实证 ViewTemplate 的 `data-tags={{!!tags}}` 会把链接化的标签去括号，如 `[[DMG城主指南]]` 渲染为 `DMG城主指南`；数字开头的标签如 `[[0 核心三宝书]]` 才保留括号）；值支持两种写法：字符串（该书全级别同色）或 `{"h1h2": 色, "h3h6": 色}`（按级别分组，可只给一组）。当前已有：`DMG城主指南` h1/h2 `navy`、h3-h6 `steelblue`
  3. 根目录页面（精确匹配标题 `前言`/`译者名录`/`如何使用大不全`，gen_styles.py 的 `ROOT_TITLES`）：h1/h2 `DarkSlateGray`，h3-h6 `teal`
- 页面大标题条是 `<h2 class="tc-title">`，配色规则用 `h2:not(.tc-title)` **排除**，保持 TiddlyWiki 原色不受影响（用户要求）
- **specificity 坑（已修复）**：`cascading_stylesheet.css.tid` 里有 `.tc-tiddler-body h1-h6 { color: maroon }`（(0,1,1)），且它合并后排在标题配色之后——同 specificity 时后者胜，会把所有标题压成 maroon。因此标题配色**全部规则**必须用 `.tc-tiddler-frame.tc-tiddler-view-frame` 前缀（(0,2,1)+）的选择器（默认 (0,2,1)、按书/根页面 (0,3,1)），新增规则时不要降级

## 6. 侧边栏目录

- 由 `Contents.hhc` 生成。
- 关键 Tiddler：
  - `总目录`
  - `CHM目录侧边栏`（tag `$:/tags/SideBar`，caption `目录`）
  - `$:/tags/SideBar`（覆盖顺序，包含 `CHM目录侧边栏`）
- 使用 `<details>/<summary>` 实现展开/收起。
- 每级缩进 `0.5em`。
- 已移除“卷首资料”层级。
- `$:/tags/SideBar` 与 `$:/DefaultTiddlers` 为手动维护文件，`generate_toc.py` 不再写回（曾固定写回 SideBar list，已移除）。
- 已通过 `SKIP_TITLES` 跳过合并/删除节点：
  ```python
  {
      "为何改版 (DMG-城主指南)",
      "关于边栏 (DMG-城主指南)",
      "地下城主 (DMG-城主指南)",
      "如何使用本书 (DMG-城主指南)",
      "最后 (DMG-城主指南)",
      # 已合并入 "第一章：担任地下城主 (DMG-城主指南)"（源 DM是什么？.htm）
      "地下城主2 (DMG-城主指南)",
      "设计冒险任务 (DMG-城主指南)",
      "自创冒险任务 (DMG-城主指南)",
      "使用预设冒险任务 (DMG-城主指南)",
      "游戏教学 (DMG-城主指南)",
      "创造世界 (DMG-城主指南)",
      "裁判 (DMG-城主指南)",
      "运作游戏 (DMG-城主指南)",
      # 已合并入 "游戏风格 (DMG-城主指南)"
      "破门砍杀型 (DMG-城主指南)",
      "叙事扮演型 (DMG-城主指南)",
      "中间路线 (DMG-城主指南)",
      "其他风格 (DMG-城主指南)",
      # 已合并入 "简介 (DMG-城主指南)"
      "建议 (DMG-城主指南)",
      # 已合并入 "跑团 (DMG-城主指南)"（第一章\跑团.htm）
      "了解玩家 (DMG-城主指南)",
      "即席规则 (DMG-城主指南)",
      "协调玩家 (DMG-城主指南)",
      "游戏外思考 (DMG-城主指南)",
      "了解玩家人物 (DMG-城主指南)",
      "了解冒险任务与其他资料 (DMG-城主指南)",
      "熟悉规则 (DMG-城主指南)",
      # 已合并入 "保持游戏平衡 (DMG-城主指南)"（第一章\保持游戏平衡.htm）
      "处理不平衡的玩家人物 (DMG-城主指南)",
      # 已合并入 "改变规则 (DMG-城主指南)"（第一章\改变规则.htm）
      "改得让游戏顺畅 (DMG-城主指南)",
      "丰富游戏 (DMG-城主指南)",
      "犯错 (DMG-城主指南)",
      # 已合并入 "布置舞台 (DMG-城主指南)"（第一章\布置舞台.htm）
      "主持游戏所需的配备 (DMG-城主指南)",
      "前情提要 (DMG-城主指南)",
      "使用小模型 (DMG-城主指南)",
      "绘制地图 (DMG-城主指南)",
      "掌握节奏 (DMG-城主指南)",
      "查阅规则 (DMG-城主指南)",
      "发问 (DMG-城主指南)",
      "中场休息 (DMG-城主指南)",
      # 已合并入 "处理玩家人物的行动 (DMG-城主指南)"（第一章\处理玩家人物的行动.htm）
      "处理NPC的行动 (DMG-城主指南)",
      "人物被魔法控制 (DMG-城主指南)",
      "叙述动作 (DMG-城主指南)",
      "NPC的动作 (DMG-城主指南)",
      "让战斗有趣 (DMG-城主指南)",
      # 已合并入 "更多移动规则 (DMG-城主指南)"（第二章\更多移动规则\更多移动规则.htm）
      "移动与方格 (DMG-城主指南)",
      "移动与位置 (DMG-城主指南)",
      "度量与方格 (DMG-城主指南)",
      "斜向方格移动 (DMG-城主指南)",
      "防具与负重量 (DMG-城主指南)",
      "三维空间的移动 (DMG-城主指南)",
      "空中战术移动 (DMG-城主指南)",
      "逃逸与追赶 (DMG-城主指南)",
      "方格间的活动 (DMG-城主指南)",
      # 已合并入 "战斗 (DMG-城主指南)"（第二章\战斗\战斗.htm）
      "视线 (DMG-城主指南)",
      "遭遇开始 (DMG-城主指南)",
      "规则变化：每轮都掷先攻权 (DMG-城主指南)",
      "规则变化：聪慧的座骑 (DMG-城主指南)",
      "突袭轮 (DMG-城主指南)",
      "新加入的战斗者 (DMG-城主指南)",
      "推动游戏 (DMG-城主指南)",
      "同时行动 (DMG-城主指南)",
      "规则变化：失手时误中掩蔽物 (DMG-城主指南)",
      "战斗动作 (DMG-城主指南)",
      "判定未被定义过的新动作 (DMG-城主指南)",
      "战斗以外的战斗动作 (DMG-城主指南)",
      "规则变化：必然命中与防御检定 (DMG-城主指南)",
      "判定准备动作 (DMG-城主指南)",
      "幕后随谈：重击 (DMG-城主指南)",
      "重击 (DMG-城主指南)",
      "规则变化：依据体型定义巨创(MassiveDamage) (DMG-城主指南)",
      "规则变化：攻击特定部位 (DMG-城主指南)",
      "规则变化：等效武器 (DMG-城主指南)",
      "伤害(伤害)(0 核心三宝书\\DMG城主指南\\第二章\\战斗\\伤害.htm) (DMG-城主指南)",
      "武器大小的影响 (DMG-城主指南)",
      "投炸武器 (DMG-城主指南)",
      "规则变化：一击致死(InstantKill) (DMG-城主指南)",
      "区域型法术 (DMG-城主指南)",
      # 已合并入 "战斗中的生物体型大小 (DMG-城主指南)"（第二章\战斗\战斗中的生物体型大小.htm）
      "大生物 (DMG-城主指南)",
      "很小的生物 (DMG-城主指南)",
      "混合 (DMG-城主指南)",
      "挤过 (DMG-城主指南)",
      "站在狭窄之处 (DMG-城主指南)",
  }
  ```
- `SKIP_HHC_TITLES`（generate_toc.py）：按 hhc 标题跳过、无法用 SKIP_TITLES 的节点（Tiddler标题 与别的节点相同）。当前含：`标准度量`（与 更多移动规则 同源 更多移动规则.htm，无独立内容）
- `MANUAL_CHILDREN`（generate_toc.py）：手动新建节点（无 hhc 源文件）注入目录，父祖先路径 -> [(label, Tiddler标题)]。当前含：战斗 下 攻击（`攻击 (DMG-城主指南)`，从战斗.tid 拆出）
- 已将 `[DMG] 建议` 从“简介”移到“第一章：担任地下城主”（注：该节点现已合并回“简介”，见手动调整记录，目录由 `SKIP_TITLES` 跳过）。

## 7. 手动调整记录

- `译者名录1.1.tid` 已更名为 `译者名录.tid`，并重新排版，书名标题使用 `[缩写]书名` 格式。
- DMG `第一章/` 与 `简介/` 文件夹已手动调整：
  - `简介/` 下所有节点内容合并至 `简介.tid`
  - 已删除空节点：`为何改版.tid`、`关于边栏.tid`、`地下城主.tid`、`如何使用本书.tid`、`最后.tid`
  - 当前 `简介/` 只保留 `简介.tid`
- `简介.tid` 的标题层级调整已还原，改为通过 `cascading_stylesheet.css.tid` 控制。
- 默认首页：`$:/DefaultTiddlers` → `[[前言]]` + `[[总目录]]`（手动维护，脚本不写；已随根页面去前缀同步更新）
- 搜索最小长度：`$:/config/Search/MinLength` = `1`
- 语言：简体中文（`tiddlywiki.info` 中 `languages: ["zh-Hans"]`，`$:/language` 指向 `$:/languages/zh-Hans`）
- **手动维护文件（任何脚本不得覆盖）**：
  - `$:/tags/SideBar`（`$__tags_SideBar.tid`）：标签页顺序，目录已置顶
  - `$:/DefaultTiddlers`（`$__DefaultTiddlers.tid`）：默认首页
  - `generate_toc.py` 已移除对 `$:/tags/SideBar` 的写回逻辑，重跑只更新 `总目录` 与 `CHM目录侧边栏`
- MM `简介/简介.tid`、`简介/怪物种类.tid`、`魔鬼/劣魔.tid` 已清理 `class="page"`/`class="title"`（`clean_dmg_classes.py` 已泛化支持传入目标目录）
- 标签规则改为只保留两级（书目分类+书名），全部 1311 个内容页已重打标签（`retag_tids.py`），`final_mapping.csv` 已重建
- 8 个 DMG 节点（地下城主2/设计冒险任务/自创冒险任务/使用预设冒险任务/游戏教学/创造世界/裁判/运作游戏）已手动合并入 `DM是什么？.tid`（标题 `[DMG] 第一章：担任地下城主`）并删除；`generate_toc.py` 的 `SKIP_TITLES` 已加入这 8 个标题，`convert_book.py` 新增 `SKIP_SOURCES` 防止重转复活
- 4 个 DMG 节点（破门砍杀型/叙事扮演型/中间路线/其他风格）已手动合并入 `游戏风格.tid`（`[DMG] 游戏风格`）并删除，`SKIP_TITLES` 与 `SKIP_SOURCES` 已同步更新
- `[DMG] 建议` 已手动合并入 `简介.tid`（`[DMG] 简介`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，`postprocess_toc()` 中“建议移入第一章”的旧移动逻辑已清理
- 7 个 DMG 节点（了解玩家/即席规则/协调玩家/游戏外思考/了解玩家人物/了解冒险任务与其他资料/熟悉规则）已手动合并入 `跑团.tid`（`[DMG] 跑团`，源 `第一章\跑团.htm`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，目录已重生成（跑团节点仍为 details，保留其他子节点如保持游戏平衡）
- `处理不平衡的玩家人物.tid`（`[DMG] 处理不平衡的玩家人物`）已手动合并入 `保持游戏平衡.tid`（`[DMG] 保持游戏平衡`，源 `第一章\保持游戏平衡.htm`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，目录已重生成
- 3 个 DMG 节点（改得让游戏顺畅/丰富游戏/犯错）已手动合并入 `改变规则.tid`（`[DMG] 改变规则`，源 `第一章\改变规则.htm`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，目录已重生成（改变规则仍为 details，保留布置舞台等子节点）
- 8 个 DMG 节点（主持游戏所需的配备/前情提要/使用小模型/绘制地图/掌握节奏/查阅规则/发问/中场休息）已手动合并入 `布置舞台.tid`（`[DMG] 布置舞台`，源 `第一章\布置舞台.htm`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，目录已重生成（布置舞台与这些节点原为同级，均在改变规则下）
- 5 个 DMG 节点（处理NPC的行动/人物被魔法控制/叙述动作/NPC的动作/让战斗有趣）已手动合并入 `处理玩家人物的行动.tid`（`[DMG] 处理玩家人物的行动`，源 `第一章\处理玩家人物的行动.htm`）并删除；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，目录已重生成（与这些节点原为同级，均在改变规则下）
- 9 个 DMG 节点（移动与方格/移动与位置/度量与方格/斜向方格移动/防具与负重量/三维空间的移动/空中战术移动/逃逸与追赶/方格间的活动）已合并入 `更多移动规则.tid`（`更多移动规则 (DMG-城主指南)`，源 `第二章\更多移动规则\更多移动规则.htm`）并删除；格式参考 `简介.tid`（子节点 h1 降级 h2，`<p>&nbsp;</p>` 分隔，工具 `merge_move_rules.py`）；`SKIP_TITLES`/`SKIP_SOURCES` 已同步，`标准度量`（与父同源）经新增 `SKIP_HHC_TITLES` 跳过，目录已重生成（更多移动规则变叶子 div）
- 24 个 DMG 节点（视线/遭遇开始/突袭轮/战斗动作/重击/伤害/区域型法术 等，第二章战斗 全部 hhc 子节点）已合并入 `战斗.tid`（`战斗 (DMG-城主指南)`，源 `第二章\战斗\战斗.htm`）并删除；格式同简介.tid（工具 `merge_combat.py`，按 hhc 顺序、按源文件名取文件）；`SKIP_TITLES`（24 项，含消歧标题 `伤害(伤害)(...)`）/`SKIP_SOURCES` 已同步，目录已重生成（战斗变叶子 div）；`战斗中的生物体型大小` 及其子节点（大生物/很小的生物/混合/挤过/站在狭窄之处）为平级节点（源文件恰在战斗目录下），未合并
- 战斗.tid 手动拆分（用户操作，2026-08-30）：第 158 行起（`攻击检定` 小节至末尾，含重击/伤害/非致命伤害等）转移至新建 `攻击.tid`（`攻击 (DMG-城主指南)`，**虚拟 source** `第二章\战斗\攻击.htm`（源文件不存在，retag/校验自动跳过），与战斗.tid 同目录）；战斗.tid 保留前 157 行；`generate_toc.py` 新增 `MANUAL_CHILDREN` 机制注入目录（战斗 → 攻击），目录已重生成（战斗变回 details）
- 5 个 DMG 节点（大生物/很小的生物/混合/挤过/站在狭窄之处）已合并入 `战斗中的生物体型大小.tid`（`战斗中的生物体型大小 (DMG-城主指南)`，源 `第二章\战斗\战斗中的生物体型大小.htm`）并删除；格式同简介.tid（`merge_combat.py` 参数化复用）；`SKIP_TITLES`/`SKIP_SOURCES` 已同步（父节点源 `战斗中的生物体型大小.htm` 加入防覆盖清单），目录已重生成（父节点变叶子 div）
- 结构重组（2026-09，用户手动改总目录后同步数据源）：`改变规则`/`布置舞台`/`处理玩家人物的行动`/`决定结果` 4 个节点从「第一章：担任地下城主」及其下**移入 `跑团` 下平级**（hhc_mapping.csv/final_mapping.csv 的祖先路径已改，备份 `.restructure-backup`）；同时 `处理玩家人物的行动.tid` 的 title 被用户改名为 `[DMG] 处理玩家人物与NPC的行动`（final_mapping 的 Tiddler标题 已同步为带 `[DMG]` 前缀的完整标题）；跑团下现有：保持游戏平衡、改变规则、布置舞台、处理玩家人物与NPC的行动、决定结果
- **全库标题格式重命名（2026-08-30）**：用户拍板新格式 `具体标题 (书目缩写-书名)`（无缩写写所属内容，10 附录写 (附录)），如 `简介 (DMG-城主指南)`；根页面移除「龙与地下城3版扩展规则大全 - 」前缀（前言/译者名录/如何使用大不全，DefaultTiddlers/StoryList 已同步）；已改 build_mapping.py（build_title()/insert_disambig()）、重建 final_mapping.csv（备份 .old-title-format/.pre-rootfix）、全库 .tid 的 title 行与链接目标（rename_titles.py，0 断链）、generate_toc.py 的 SKIP_TITLES 42 项同步新格式，目录已重生成（label 仍显示简洁名如「简介」）
- `work/meow-review/` 存放 DSH 插件源码副本（meow-memory / meow-cachebilling，已热装配到 web profile，node_modules junction 指向此处，勿删）
- 已新增「标题配色」机制：`gen_styles.py` 生成 `标题配色.tid`（每本书可单独定义页面 h1-h6 标题字色，未指定默认 maroon；根目录页面 h1/h2 DarkSlateGray、h3-h6 teal），已有 `DMG城主指南` h1/h2 navy、h3-h6 steelblue
- **PHB 法术描述重排版（2026-09-01）**：`0 核心三宝书/PHB玩家手册/11法术/法术描述` 下 22 个单字母节点（B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U/V/W/Z）已用 `clean_spell_tids.py` 手工重排，对齐 `A.tid` 风格（详见 5.5b）。`A.tid`、`法术描述.tid` 已干净未改动。此目录为手工清洗成果，备份 `法术描述_backup_20260901_174546`。
- **PHB 全本排版完成（2026-09-01）**：法术描述重排后，PHB 玩家手册全本 117 页均已排版定稿。已在 `convert_book.py` 的 `SKIP_SOURCE_PREFIXES` 加入整本书前缀 `0 核心三宝书\PHB玩家手册\`，**后续搬运 PHB 整本自动跳过**。**PHB 全本排版至此完成，后续都应跳过。**
- **删除 10 附录 节点（2026-09-01）**：删除了 `10 附录/html教学/`（含 `开始之前.tid`、`标签与格式.tid` 及 `标签与格式/` 图片资源，标题 `开始之前 (html-教学)`、`标签与格式 (html-教学)`）与 `10 附录/如何使用大不全.tid`（标题 `(旧)如何使用大不全 (附录)`）。已按铁律三步同步：①删文件/目录 ②`generate_toc.py` 的 `SKIP_TITLES` 加入这三个标题（防重生成复活）③重跑 `generate_toc.py` 重新生成 `总目录.tid`/`CHM目录侧边栏.tid`（链接自动消失）。全库无其他页面引用这些节点，删除无遗留断链；根目录的 `如何使用大不全`（无后缀）保留。备份 `work/backup_del_appendix_20260901_182145`。
- **还原 `如何使用大不全` + 删除 `如何为扩展大全做出贡献`（2026-09-01）**：从备份 `work/backup_del_appendix_20260901_182145` 还原 `10 附录/如何使用大不全.tid`，标题改回 `如何使用大不全 (附录)`（原删除时加了 `(旧)` 前缀，现已去掉），出现在附录章节下（与版本历史/常见资源分类同级）。同时删除了 `10 附录/如何为扩展大全做出贡献.tid`（`如何为扩展大全做出贡献 (附录)`，内容仅 `还在编。`）。目录同步：①`generate_toc.py` 的 `SKIP_TITLES` 移除 `(旧)如何使用大不全 (附录)`、新增 `如何为扩展大全做出贡献 (附录)` ②`hhc_mapping.csv` 与 `final_mapping.csv` 将 `如何使用大不全` 的 `Tiddler标题` 改回 `如何使用大不全 (附录)`、祖先路径改回 `附录`（与版本历史同级）③重跑 `generate_toc.py` 重生成 `总目录.tid`/`CHM目录侧边栏.tid` ④修正 `总目录.tid` 根目录第 7 行死链（原指向无后缀 `如何使用大不全`，改为 `如何使用大不全 (附录)`）。
- **武器附魔测评 重排版 + 改名（2026-09-01）**：`10 附录/武器附魔测评/` 下 11 个节点（原文件名是随机哈希 `.tid`）统一重排为 `E-F` 参考格式——词条用 `<h5>中文名(ENGLISH) </h5>`，字段用 `<p><b>字段名：</b>值</p>`，开头保留 `<h2>段名</h2>`。`A.tid` 为旧格式（整段一个 `<p>` + `<br>` 分隔）单独解析；其余 9 个为中间格式（字段拆独立 `<p>`、词条名无 h5）；`E-F.tid` 已是目标格式仅改名不改动内容。同时把随机哈希文件名改为字母段名（`03510EA6...→A.tid`、`7B7FF8...→E-F.tid` 等共 11 个）。目录链接基于 **title**（如 `A (武器附魔测评)`），title 未变，故 `总目录.tid`/`CHM目录侧边栏.tid` 无需改动即同步有效。备份 `work/backup_reformat_weapon_20260901`。
- **10 附录 整目录排除在自动搬运外（2026-09-01，用户明确「10 附录/ 目录下的全都排除」）**：为防 `convert_book.py` 重转覆盖/复活今天的手工成果，已将 `convert_book.py` 的 `SKIP_SOURCE_PREFIXES` 改为整目录前缀 `"10 附录\\"`（覆盖 `10 附录\` 下一切源，含 `武器附魔测评`、`html教学`、已还原的 `如何使用大不全`、已删 tid 的 `如何为扩展大全做出贡献`、版本历史等全部 33 个源 htm）。同时保留 `SKIP_SOURCES` 中的 4 个精确项（`10 附录\如何使用大不全.htm`、`10 附录\如何为扩展大全做出贡献.htm`、`10 附录\html教学\开始之前.htm`、`10 附录\html教学\标签与格式.htm`，它们已被父前缀覆盖，留作明示）。已用 `_verify_skip.py` 验证：`10 附录\` 下全部 SKIP（含版本历史/任意子文件），根目录 `如何使用大不全.htm`（无 `10 附录\` 前缀，属根页面）PASS 未误伤，其他书籍 PASS。**不要再缩小该前缀、也不要用 `convert_book.py` 重转 `10 附录` 任何源**，如需调整其中节点应手工改对应 `.tid`。

## 8. 注意事项

- **手动调整节点规则（2026-08-30 用户拍板）**：以用户调整为准；**合并节点时仍需参考 hhc**（确定合并的子节点范围与顺序，如 merge_combat.py 按 hhc 祖先路径过滤）；其他手动调整（新建/拆分/改层级）不需要与 hhc 对照；**必须防自动导入覆盖**——被合并/删除节点的源文件**和**手动调整过（合并子节点/拆分内容）的父节点源文件都要加入 `convert_book.py` 的 `SKIP_SOURCES`（重转会覆盖手动版本）；新建无源节点用 `generate_toc.py` 的 `MANUAL_CHILDREN` 注入目录
- 不要用 `convert_book.py` 全量重转已手动调整过的文件，除非确认会保留手动修改。
- **不要重转 PHB 任何页面（2026-09-01 铁律）**：`0 核心三宝书/PHB玩家手册` 全本已排版完成（含 `11法术/法术描述` 手工重排），已加入 `convert_book.py` 的 `SKIP_SOURCE_PREFIXES` 整本书前缀 `0 核心三宝书\PHB玩家手册\`。**后续搬运（或任何重转操作）都必须让 PHB 整本被跳过，不得移除该跳过项、不得用 `convert_book.py` 重转 PHB 任何页面**，否则已定稿排版会被原始 CHM 噪音覆盖。如需调整 PHB 内某节点，应手工修改对应 `.tid` 或重跑 `clean_spell_tids.py`（它自动跳过 `A.tid`/`法术描述.tid`），而非重转源。
- **不要重转 10 附录 任何内容（2026-09-01 铁律，用户明确「整目录排除」）**：`convert_book.py` 的 `SKIP_SOURCE_PREFIXES` 已加入整目录前缀 `"10 附录\\"`，覆盖 `10 附录/` 下**全部**源（武器附魔测评/如何使用大不全/html教学/如何为扩展大全做出贡献/版本历史等 33 个 htm）。`SKIP_SOURCES` 仍保留 4 个精确项作明示（已被父前缀覆盖）。**不得缩小该前缀、不得移除跳过项、不得用 `convert_book.py` 重转 `10 附录` 任何源**，否则重排版被原始 CHM 覆盖、已删节点复活、已改文件名被哈希名覆盖。如需调整其中节点，应手工修改对应 `.tid`。
- **源文档几乎没有内部超链接**（2026-08-30 实测）：全库 `.tid` 正文仅 **2 处** `[[...]]`，`<a href>` 仅 **3 处**（且集中在 `html教学`、`版本历史` 等说明性页面）。正文交叉引用是「见22页表3-2」这类**页码文字**，并非链接。因此链接改写收益极低，页面导航主要依赖 `总目录`；**不要为追求互链而臆造链接**。重新校验：`python transport/work/_verify_links.py`（刷新 `logs/link-report.csv`）。
- `convert_book.py` 已接入落盘日志 `logs/转换日志.log`（记录 开始/完成、SKIP、MISSING、ERROR、OK）；单页异常只记录并跳过，不再中断整批。
- `generate_toc.py` 已内置 DMG 简介相关同步逻辑，可安全重新生成目录。
- 新窗口继续工作时，先读取本文件，再根据“当前进度”决定下一批搬运目标。
- 下一批建议：`1 核心补充书籍/`（三宝书已全部完成）

## 9. 运行状态

- TiddlyWiki 服务当前为**关闭状态**。
- 后续修改内容后，**不要自动启动服务**，由用户手动启动并刷新。
- 手动启动命令：
  ```bash
  tiddlywiki transport/wiki --listen port=8080
  ```
- 访问地址：
  ```text
  http://127.0.0.1:8080/
  ```
