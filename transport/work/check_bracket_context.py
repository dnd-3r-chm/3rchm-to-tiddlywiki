# -*- coding: utf-8 -*-
"""只读：统计「中文+[内容]」方括号的前文，用于区分语义。

3R 规范：学派[描述符] 用方括号(应保留)；技能子项 知识(地下城) 应用圆括号。
"""
import os
import re
from collections import Counter

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
PAT = re.compile(r"(.{0,4})(?<=[\u4e00-\u9fff])\[([^\[\]]{1,20})\]")

pre = Counter()
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        for m in PAT.finditer(s):
            pre[m.group(1)] += 1

print("方括号前 1-4 字（按出现频次，前 40）：")
for k, v in pre.most_common(40):
    print("  %-10s %d" % (repr(k), v))
