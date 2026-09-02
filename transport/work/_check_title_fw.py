# -*- coding: utf-8 -*-
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    fw = "[（）]"
    bad = []
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        t = open(p, encoding="utf-8").read()
        if re.search(fw, t):
            bad.append(os.path.relpath(p, ROOT))
    print(book, "含全角（）文件数:", len(bad))
    for r in bad[:10]:
        print("   ", r)
