#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TOC = r"E:\dnd3r_full\transport\wiki\tiddlers\总目录.tid"
with open(TOC, encoding="utf-8") as f:
    text = f.read()

old = '<details style="margin-left:1.0em;"><summary>[[简介|[DMG] 简介]]</summary>\n</details>'
new = '<div style="margin-left:1.0em;">[[简介|[DMG] 简介]]</div>'
if old in text:
    text = text.replace(old, new, 1)
    print("replaced")
else:
    print("old not found; trying regex")
    text, n = re.subn(
        r'<details style="margin-left:1\.0em;"><summary>\[\[简介\|\[DMG\] 简介\]\]</summary>\s*</details>',
        new,
        text,
        count=1,
    )
    print("regex replacements:", n)

with open(TOC, "w", encoding="utf-8") as f:
    f.write(text)
