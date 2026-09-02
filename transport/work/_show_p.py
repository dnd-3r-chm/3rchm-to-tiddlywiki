# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    # 找含连续空行的文件
    found = 0
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        if "\n\n\n" in t:
            print("###", os.path.relpath(p, ROOT))
            # 打印连续空行附近
            idx = t.find("\n\n\n")
            print(repr(t[max(0, idx-60): idx+60]))
            found += 1
            if found >= 5:
                break
    print(f"--- {book} 含连续空行文件数(前5展示):", found)
