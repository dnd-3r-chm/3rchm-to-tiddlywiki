#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「标题配色」样式 Tiddler：为每本书单独定义页面标题字色。

规则（生成顺序即 CSS 级联顺序，后者覆盖前者）：
1. 默认：所有页面 h1-h6 标题用 DEFAULT_COLOR（未单独指定颜色的书）
2. 按书覆盖：BOOK_COLORS 中列出的书（书标签名 -> 色值）覆盖默认色，
   选择器按 data-tags 精确匹配 [[书标签]]（页面 frame 的 data-tags 是原始 tags 文本）
3. 根目录页面特例：标题以 ROOT_TITLE_PREFIX 开头的页面（前言/译者名录/如何使用大不全等），
   h1/h2 用 ROOT_H1_H2_COLOR，h3-h6 用 ROOT_H3_H6_COLOR

注意：h2 一律用 `h2:not(.tc-title)`——页面大标题条（<h2 class="tc-title">）
保持 TiddlyWiki 原色，不受配色规则影响。

改色流程：编辑下方常量/字典 -> 重跑本脚本 -> wiki 页面刷新即生效（无需重启）。
样式 tiddler 为脚本生成物，重跑会覆盖，请勿手动编辑。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"E:\dnd3r_full"
OUT = os.path.join(ROOT, "transport", "wiki", "tiddlers", "标题配色.tid")

DEFAULT_COLOR = "maroon"  # 未指定颜色的书，页面标题默认色
# 根目录页面标题（2026-08-30 起不再带「龙与地下城3版扩展规则大全 - 」前缀，精确匹配）
ROOT_TITLES = ["前言", "译者名录", "如何使用大不全"]
ROOT_H1_H2_COLOR = "DarkSlateGray"  # 根目录页面 h1/h2 色
ROOT_H3_H6_COLOR = "teal"  # 根目录页面 h3-h6 色

# 每本书的标题字色：书标签名 -> 色值。未列出的书用 DEFAULT_COLOR。
# 两种写法：
#   简单：BOOK_COLORS = {"PHB玩家手册": "#c0392b"}             # 该书 h1-h6 全部同色
#   分组：BOOK_COLORS = {"DMG城主指南": {"h1h2": "navy", "h3h6": "steelblue"}}
#         键支持 "h1h2" / "h3h6"（可只给其中一组，另一组回落到默认色）
BOOK_COLORS = {
    "DMG城主指南": {"h1h2": "navy", "h3h6": "steelblue"},
}

# 分组键 -> 标题选择器（h2 排除 tc-title）
COLOR_GROUPS = {
    "h1h2": ["h1", "h2:not(.tc-title)"],
    "h3h6": ["h3", "h4", "h5", "h6"],
}

# 作用域前缀：必须用 (0,2,1)+ 的选择器——
# cascading_stylesheet.css.tid 有 .tc-tiddler-body hN { color: maroon }（(0,1,1)），
# 且它在合并后的样式表里排在标题配色之后，同 specificity 时后者胜，会把所有标题压成 maroon。
FRAME = ".tc-tiddler-frame.tc-tiddler-view-frame"

# data-tags 匹配说明（已实证）：
# ViewTemplate 的 data-tags={{!!tags}} 会把 tags 文本按 wiki 语法渲染，链接化的标签
# 会去掉 [[ ]]（如 [[DMG城主指南]] -> DMG城主指南）；数字开头的标签（如 [[0 核心三宝书]]）
# 不被 wikilink 解析，保留括号。因此按书选择器用不带括号的 `*=` 子串匹配标签名。
def book_selector(tag, head):
    return f'{FRAME}[data-tags*="{tag}"] {head}'


def build_css():
    lines = []
    lines.append("/* 标题配色 —— 由 transport/work/gen_styles.py 生成，请勿手动编辑；改色改脚本后重跑。 */")
    lines.append("")
    lines.append("/* 1) 默认：未指定颜色的页面，h1-h6 标题（h2.tc-title 页面大标题条除外） */")
    lines.append(f"{FRAME} {', '.join(COLOR_GROUPS['h1h2'] + COLOR_GROUPS['h3h6'])}".replace(", ", f", {FRAME} ") + f" {{ color: {DEFAULT_COLOR}; }}")
    lines.append("")
    lines.append("/* 2) 按书覆盖（未列出 = 默认 maroon） */")
    if not BOOK_COLORS:
        lines.append("/* （暂无指定，全部使用默认色） */")
    for tag, color in BOOK_COLORS.items():
        if isinstance(color, str):
            heads = COLOR_GROUPS["h1h2"] + COLOR_GROUPS["h3h6"]
            sel = ", ".join(book_selector(tag, h) for h in heads)
            lines.append(f"/* {tag} */")
            lines.append(f"{sel} {{ color: {color}; }}")
        else:
            for group, heads in COLOR_GROUPS.items():
                if group in color:
                    sel = ", ".join(book_selector(tag, h) for h in heads)
                    lines.append(f"/* {tag} {group} */")
                    lines.append(f"{sel} {{ color: {color[group]}; }}")
    lines.append("")
    lines.append("/* 3) 根目录页面（前言/译者名录/如何使用大不全）：h1/h2 与 h3-h6 分开配色 */")
    h12_sel = ", ".join(f'{FRAME}[data-tiddler-title="{t}"] h1, {FRAME}[data-tiddler-title="{t}"] h2:not(.tc-title)' for t in ROOT_TITLES)
    h36_sel = ", ".join(f'{FRAME}[data-tiddler-title="{t}"] {h}' for t in ROOT_TITLES for h in COLOR_GROUPS["h3h6"])
    lines.append(f"{h12_sel} {{ color: {ROOT_H1_H2_COLOR}; }}")
    lines.append(f"{h36_sel} {{ color: {ROOT_H3_H6_COLOR}; }}")
    lines.append("")
    return "\n".join(lines)


def main():
    body = build_css()
    content = f"""title: 标题配色
tags: $:/tags/Stylesheet
type: text/css

{body}
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] 标题配色.tid -> {OUT}")
    print(body)


if __name__ == "__main__":
    main()
