# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR = re.compile(r"<br\s*/?>", re.I)
total = 0
files_with = []
for dp, _, ns in os.walk(BASE):
    if os.path.basename(dp).startswith("_bak_"):
        continue
    for nm in ns:
        if not nm.lower().endswith(".tid"):
            continue
        t = open(os.path.join(dp, nm), encoding="utf-8").read()
        c = len(BR.findall(t))
        if c:
            total += c
            files_with.append((os.path.relpath(os.path.join(dp, nm), BASE), c))
print("总 br (排除备份):", total)
for r, c in files_with[:20]:
    print("  ", r, c)
if len(files_with) > 20:
    print("  ...", len(files_with), "files")
