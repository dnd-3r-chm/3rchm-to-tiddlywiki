# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR = re.compile(r"<br\s*/?>", re.I)
P_BLOCK = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
LI_BLOCK = re.compile(r"<li\b[^>]*>.*?</li>", re.S | re.I)
TD_BLOCK = re.compile(r"<td[^>]*>.*?</td>", re.S | re.I)
EMPTY_P = re.compile(r"<p>\s*</p>", re.I)

p_br = li_br = td_br = empty = 0
for dp, _, ns in os.walk(BASE):
    if "_bak_" in dp:
        continue
    for nm in ns:
        if not nm.lower().endswith(".tid"):
            continue
        t = open(os.path.join(dp, nm), encoding="utf-8").read()
        for m in P_BLOCK.finditer(t):
            p_br += len(BR.findall(m.group(0)))
            empty += len(EMPTY_P.findall(m.group(0)))
        for m in LI_BLOCK.finditer(t):
            li_br += len(BR.findall(m.group(0)))
        for m in TD_BLOCK.finditer(t):
            td_br += len(BR.findall(m.group(0)))
print("P标签内残留 <br> (应为0):", p_br)
print("空 <p></p> (应为0):", empty)
print("LI标签内 <br> (保留):", li_br)
print("表格单元格内 <br> (保留):", td_br)
