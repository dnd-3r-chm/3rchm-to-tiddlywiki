# -*- coding: utf-8 -*-
import os, re

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR_RE = re.compile(r"<br\s*/?>", re.I)

samples = [
    ("DMG2城主指南2\\数据资料格式.tid", 0),
    ("DMG2城主指南2\\新物品\\新增魔法物品.tid", 0),
    ("PHB2玩家手册2\\专长\\一般专长.tid", 0),
    ("MM3怪物图鉴3\\挑战等级表.tid", 0),
    ("XPH扩展灵能手册\\6显能\\心灵术士_狂念者异能.tid", 0),
]
for rel, _ in samples:
    p = os.path.join(BASE, rel)
    t = open(p, encoding="utf-8").read()
    print("==== " + rel + " ====")
    for m in list(BR_RE.finditer(t))[:4]:
        s = t[max(0, m.start()-60):m.end()+40]
        print(repr(s))
    print()
