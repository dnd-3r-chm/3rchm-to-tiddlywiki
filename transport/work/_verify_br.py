# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR_RE = re.compile(r"<br\s*/?>", re.I)
P_BLOCK_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
EMPTY_P_RE = re.compile(r"<p>\s*</p>", re.I)

p_br = 0
td_br = 0
empty_p = 0
for dp, _, ns in os.walk(BASE):
    if os.path.basename(dp).startswith("_bak_"):
        continue
    for nm in ns:
        if not nm.lower().endswith(".tid"):
            continue
        t = open(os.path.join(dp, nm), encoding="utf-8").read()
        for m in P_BLOCK_RE.finditer(t):
            p_br += len(BR_RE.findall(m.group(0)))
            empty_p += len(EMPTY_P_RE.findall(m.group(0)))
        # 表内 br
        for tm in re.finditer(r"<td[^>]*>.*?</td>", t, re.S | re.I):
            td_br += len(BR_RE.findall(tm.group(0)))
print("残留 <p> 段落内 <br>:", p_br)
print("残留空 <p></p>:", empty_p)
print("表格单元格内 <br> (预期保留):", td_br)
