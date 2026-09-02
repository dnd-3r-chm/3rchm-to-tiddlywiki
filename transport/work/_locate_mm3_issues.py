# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
book = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM3怪物图鉴3")
fw = "[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]"
dbl = re.compile(r"\n\s*\n\s*\n")
for p in glob.glob(os.path.join(book, "**", "*.tid"), recursive=True):
    if os.sep + "插图" + os.sep in p:
        continue
    t = open(p, encoding="utf-8").read()
    if re.search(fw, t) or dbl.search(t):
        print("FILE:", os.path.relpath(p, ROOT))
        m = re.search(fw, t)
        if m:
            i = m.start()
            print("  全角ASCII:", repr(t[max(0,i-20):i+20]))
        dd = dbl.search(t)
        if dd:
            i = dd.start()
            print("  连续空行:", repr(t[max(0,i-30):i+30]))
