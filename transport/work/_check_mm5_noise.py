# -*- coding: utf-8 -*-
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
book = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM5怪物图鉴5")
pat = re.compile(r"(?i)(StartFragment|EndFragment|&nbsp;|<o:p>|<o:P>|class=\"?Mso|mso-)")
bad = 0
for p in glob.glob(os.path.join(book, "**", "*.tid"), recursive=True):
    t = open(p, encoding="utf-8").read()
    for m in pat.finditer(t):
        bad += 1
        print(os.path.relpath(p, ROOT), "->", m.group()[:30])
print("残留 Word 噪音总数:", bad)
