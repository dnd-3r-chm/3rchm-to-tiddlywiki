#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys

sys.path.insert(0, r"E:\dnd3r_full\transport\work")
sys.stdout.reconfigure(encoding="utf-8")

import clean_dmg_classes as c

# 读取转换后的 tid（目前已被清空），但用源 body 测试
src_path = r"E:\dnd3r_full\0 核心三宝书\DMG城主指南\所有DMG表格\表3-5：宝藏.htm"
raw = open(src_path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")
opens = [m for m in re.finditer(r"<body[^>]*>", text, re.I)]
start_m = opens[-1]
start = start_m.end()
close_m = re.search(r"</body>", text[start:], re.I)
body = text[start:start + close_m.start()] if close_m else text[start:]

print("body len:", len(body))
new, removed = c.remove_page_div(body)
print("removed:", removed)
print("new len:", len(new))
print("new head:", new[:500])
print("new tail:", new[-200:])
