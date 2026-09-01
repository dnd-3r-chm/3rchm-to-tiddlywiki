#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

root = r"E:\dnd3r_full\transport\wiki\tiddlers\0 核心三宝书\DMG城主指南"
classes = ["subtitle", "num-list", "abb-table"]
hits = {c: [] for c in classes}
for dirpath, _, names in os.walk(root):
    for name in names:
        if not name.lower().endswith(".tid"):
            continue
        path = os.path.join(dirpath, name)
        text = open(path, encoding="utf-8").read()
        for c in classes:
            if f'class="{c}"' in text or f"class='{c}'" in text:
                hits[c].append(path)

for c in classes:
    print(c, len(hits[c]))
    for p in hits[c][:3]:
        print("  ", p)
