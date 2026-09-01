#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = r"E:\dnd3r_full\10 附录\出版书籍顺序.htm"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")
print("length:", len(text))
print(text[:6000])
