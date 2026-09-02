# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 精确：单个 <p...>...</p> 内部（不含嵌套 </p> 前）是否含 \n
P = re.compile(r"<p[^>]*>((?:[^<\n]|<(?!/(?:p|/p))[^>]*>)*)</p>", re.I)
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    bad = 0
    bad_samples = []
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        for m in P.finditer(t):
            if "\n" in m.group(1):
                bad += 1
                if len(bad_samples) < 3:
                    bad_samples.append((os.path.relpath(p, ROOT), repr(m.group(0)[:80])))
    print(f"{book}: p标签内部含换行数={bad}")
    for r, s in bad_samples:
        print("   ", r, s)
