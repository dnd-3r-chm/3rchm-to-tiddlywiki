#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = r"E:\dnd3r_full\0 核心三宝书\DMG城主指南\所有DMG表格\表2-1：机动性.htm"
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")
print("len", len(text))
print("has <body>", "<body" in text.lower())
print("has </body>", "</body>" in text.lower())
print(text[:2000])
