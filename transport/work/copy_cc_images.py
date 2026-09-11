# -*- coding: utf-8 -*-
"""复制 CC完美斗士 的插图/封面二进制资源到 wiki（convert_book 不复制图片）。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

SRC = os.path.join(P.ROOT, "3 完美系列", "CC完美斗士")
DST = os.path.join(P.WIKI_TIDDLERS, "3 完美系列", "CC完美斗士")

EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp")
copied = 0
for root, dirs, fs in os.walk(SRC):
    for x in fs:
        if x.lower().endswith(EXT):
            s = os.path.join(root, x)
            rel = os.path.relpath(s, SRC)
            d = os.path.join(DST, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            copied += 1
            print("copied:", rel)
print(f"共复制 {copied} 个图片文件")
