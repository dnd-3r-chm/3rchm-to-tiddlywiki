#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(P.ROOT, "0 核心三宝书", "PHB玩家手册", "11法术", "法术描述", "B.htm")
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")
print("length:", len(text))
print(text[:4000])
