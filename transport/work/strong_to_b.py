# -*- coding: utf-8 -*-
"""全库替换 <strong> -> <b>、</strong> -> </b>（用户规则 2026-08-30）。跳过 $__ 系统文件。"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = r"E:\dnd3r_full\transport\wiki\tiddlers"

files_changed = 0
tags_changed = 0
for dp, _, ns in os.walk(WIKI):
    for n in ns:
        if not n.lower().endswith(".tid") or n.startswith("$__"):
            continue
        path = os.path.join(dp, n)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        orig = content
        content, c1 = re.subn(r"<strong\b[^>]*>", "<b>", content)
        content, c2 = re.subn(r"</strong\s*>", "</b>", content)
        if content != orig:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            files_changed += 1
            tags_changed += c1 + c2

print(f"files changed: {files_changed}, tags replaced: {tags_changed}")
