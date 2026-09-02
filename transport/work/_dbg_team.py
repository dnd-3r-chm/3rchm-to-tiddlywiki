# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
f = r"DMG2城主指南2\团队之魂.tid"
t = open(os.path.join(BASE, f), encoding="utf-8").read()
BR = re.compile(r"<br\s*/?>", re.I)
P = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
print("总 br:", len(BR.findall(t)))
print("p 块内 br:", sum(len(BR.findall(m.group(0))) for m in P.finditer(t)))
print("样本:")
for m in list(BR.finditer(t))[:3]:
    print(repr(t[max(0,m.start()-50):m.end()+30]))
