# -*- coding: utf-8 -*-
import os, re

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/XPH扩展灵能手册/7装备"
for f in ["灵物.tid", "灵能石.tid", "使用物品.tid", "灵冠.tid"]:
    p = os.path.join(D, f)
    t = open(p, encoding="utf-8").read()
    m = re.search(r"<table.*?</table>", t, re.S | re.I)
    print("==== " + f + " ====")
    print(m.group(0)[:800])
    print()
