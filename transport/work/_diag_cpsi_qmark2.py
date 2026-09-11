# -*- coding: utf-8 -*-
"""诊断：定位源 htm 解码后 ??? 的上下文（连续3字节解码失败的位置）。"""
import os
import re

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki"
src = os.path.join(BASE, "3 完美系列", "CPsi完美灵能", "1.基础", "圣念者.htm")
raw = open(src, "rb").read()
text = raw.decode("gb18030", errors="replace")

hits = list(re.finditer(r"\?{2,}", text))
print("??? 类乱码出现次数:", len(hits))
for m in hits[:8]:
    print("\n---- 位置 %d ----" % m.start())
    print("上下文:", repr(text[max(0, m.start() - 80) : m.end() + 40]))

# 同时尝试 utf-8 解码，看这些字节是否本应是 utf-8
print("\n\n===== 尝试 utf-8 解码对比 =====")
try:
    u8 = raw.decode("utf-8")
    print("整个文件 utf-8 解码成功")
except UnicodeDecodeError as e:
    print("utf-8 解码失败位置:", e.start, e.reason)
    seg = raw[max(0, e.start - 20) : e.start + 20]
    print("失败处字节:", seg)
    print("gbk视角:", seg.decode("gb18030", errors="replace"))
