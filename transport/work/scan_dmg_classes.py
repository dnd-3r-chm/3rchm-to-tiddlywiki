#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

root = r"E:\dnd3r_full\transport\wiki\tiddlers\0 核心三宝书\DMG城主指南"
page_hits = []
title_hits = []
for dirpath, _, names in os.walk(root):
    for name in names:
        if not name.lower().endswith(".tid"):
            continue
        path = os.path.join(dirpath, name)
        text = open(path, encoding="utf-8").read()
        if 'class="page"' in text:
            page_hits.append(path)
        if 'class="title"' in text:
            title_hits.append(path)

print("class=page count:", len(page_hits))
print("class=title count:", len(title_hits))
print("page examples:", page_hits[:5])
print("title examples:", title_hits[:5])
