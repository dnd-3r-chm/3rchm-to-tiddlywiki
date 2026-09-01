#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = r"E:\dnd3r_full\0 核心三宝书\PHB玩家手册\2种族\人类.htm"
raw = open(path, "rb").read()
print("size:", len(raw))
print("first bytes:", raw[:100])

m = re.search(rb"charset=[\"']?([\w-]+)", raw[:2000], re.I)
print("charset meta:", m.group(1).decode("ascii", errors="replace") if m else None)

for enc in ("gb18030", "utf-8"):
    try:
        text = raw.decode(enc)
        print("decode ok:", enc)
        break
    except UnicodeDecodeError as e:
        print("decode fail:", enc, e)

print(text[:1500])
