# -*- coding: utf-8 -*-
"""诊断：查源 htm 中 ??? 乱码位置的原始字节（判断能否还原）。"""
import os

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki"
src = os.path.join(BASE, "3 完美系列", "CPsi完美灵能", "1.基础", "圣念者.htm")
raw = open(src, "rb").read()
print("文件大小:", len(raw))

for kw in ["属性", "种族", "阵营", "背景", "阵　"]:
    b = kw.encode("gb18030")
    idx = raw.find(b)
    if idx < 0:
        print("\n[%s] 未找到" % kw)
        continue
    print("\n[%s] 偏移 %d" % (kw, idx))
    print("  原始字节:", raw[max(0, idx - 30) : idx + len(b) + 10])
    try:
        print("  gb18030:", raw[max(0, idx - 30) : idx + len(b) + 10].decode("gb18030"))
    except Exception as e:
        print("  gb18030解码失败:", e)
