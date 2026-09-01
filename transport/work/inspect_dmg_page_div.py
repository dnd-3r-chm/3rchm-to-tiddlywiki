#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(P.ROOT, "0 核心三宝书", "DMG城主指南", "所有DMG表格", "表3-5：宝藏.htm")
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")

# 提取最内层 body（同 extract_body）
opens = [m for m in re.finditer(r"<body[^>]*>", text, re.I)]
start_m = opens[-1]
start = start_m.end()
close_m = re.search(r"</body>", text[start:], re.I)
body = text[start:start+close_m.start()] if close_m else text[start:]
print("body length:", len(body))
print(body[:3000])
