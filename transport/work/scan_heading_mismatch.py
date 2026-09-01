#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

root = r"E:\dnd3r_full\transport\wiki\tiddlers"
hits = []
for dirpath, _, names in os.walk(root):
    for name in names:
        if not name.lower().endswith(".tid"):
            continue
        path = os.path.join(dirpath, name)
        text = open(path, encoding="utf-8").read()
        # 简单检测 <hN ...> 与 </hM> 不匹配（非贪婪，跨行）
        for m in re.finditer(r"<h([1-6])[^>]*>.*?</h([1-6])>", text, re.S | re.I):
            if m.group(1) != m.group(2):
                hits.append((path, m.group(0)[:80]))
                break

print("mismatched heading files:", len(hits))
for p, snippet in hits[:30]:
    print(p, "=>", snippet)
