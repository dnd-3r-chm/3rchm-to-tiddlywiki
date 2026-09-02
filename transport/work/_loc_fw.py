# -*- coding: utf-8 -*-
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "PHB2玩家手册2", "职业", "魔剑客.tid")
t = open(p, encoding="utf-8").read()
for ch in t:
    o = ord(ch)
    if 0xFF00 <= o <= 0xFFEF or ch in "“”‘’＂＇":
        print(hex(o), repr(ch))
