# -*- coding: utf-8 -*-
import os, re

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/XPH扩展灵能手册/7装备"
for f in sorted(os.listdir(D)):
    if not f.endswith(".tid") or f == "武器.tid":
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read()
    rs = len(re.findall(r"rowspan", t, re.I))
    cs = len(re.findall(r"colspan", t, re.I))
    if rs or cs:
        print(f"{f}: rowspan={rs} colspan={cs}")
print("扫描完成")
