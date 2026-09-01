#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 建议、地下城主2 从 简介 移到 第一章：担任地下城主。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

TOC = r"E:\dnd3r_full\transport\wiki\tiddlers\总目录.tid"

with open(TOC, encoding="utf-8") as f:
    text = f.read()

# 从简介中移除这两行
lines_to_remove = [
    '<div style="margin-left:1.5em;">[[建议|[DMG] 建议]]</div>',
    '<div style="margin-left:1.5em;">[[地下城主2|[DMG] 地下城主2]]</div>',
]
for line in lines_to_remove:
    if line not in text:
        print("NOT FOUND:", line)
    text = text.replace(line + "\n", "", 1)

# 插入到第一章 summary 之后
anchor = '<details style="margin-left:1.0em;"><summary>[[第一章：担任地下城主|[DMG] 第一章：担任地下城主]]</summary>\n'
if anchor not in text:
    print("ANCHOR NOT FOUND")
else:
    insert = "".join(line + "\n" for line in lines_to_remove)
    text = text.replace(anchor, anchor + insert, 1)

with open(TOC, "w", encoding="utf-8") as f:
    f.write(text)
print("done")
