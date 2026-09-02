# -*- coding: utf-8 -*-
import os
import _clean_all_noise as cn
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM5怪物图鉴5", "封面.tid")
t = open(p, encoding="utf-8").read()
lines = t.split("\n")
body = "\n".join(lines[5:])
print("== 清理后 ==")
print(cn.normalize(body))
