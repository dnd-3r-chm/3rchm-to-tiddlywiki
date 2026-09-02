# -*- coding: utf-8 -*-
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    fw = "[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]"
    bad = 0
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if re.search(fw, open(p, encoding="utf-8").read()):
            bad += 1
    print(book, "全角ASCII违规文件数:", bad)
