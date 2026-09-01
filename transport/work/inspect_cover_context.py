#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(P.ROOT, "0 核心三宝书", "DMG城主指南", "封面.htm")
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")

m = re.search(r"<img[^>]*>", text, re.I | re.S)
if m:
    start = max(0, m.start() - 500)
    end = min(len(text), m.end() + 500)
    print(text[start:end])
