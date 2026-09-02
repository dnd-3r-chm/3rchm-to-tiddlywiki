# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR = re.compile(r"<br\s*/?>", re.I)
P_BLOCK = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
resid = []
for dp, _, ns in os.walk(BASE):
    if os.path.basename(dp).startswith("_bak_"):
        continue
    for nm in ns:
        if not nm.lower().endswith(".tid"):
            continue
        t = open(os.path.join(dp, nm), encoding="utf-8").read()
        c = sum(len(BR.findall(m.group(0))) for m in P_BLOCK.finditer(t))
        if c:
            resid.append((os.path.relpath(os.path.join(dp, nm), BASE), c))
print("P块内 br 残留文件数:", len(resid))
for r, c in resid[:25]:
    print("  ", r, c)
