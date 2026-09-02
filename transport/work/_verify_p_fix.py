# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    # p 标签内部含空行（\n 出现在 <p ...> 与 </p> 之间）
    inner_nl = re.compile(r"<p[^>]*>[\s\S]*?\n[\s\S]*?</p>", re.I)
    # 标签尖括号内多余空格 <p > <p  class= >
    tag_space = re.compile(r"<p\s+>|<p\s+[^>]*\s+>")
    # 两空行及以上（标签间空行）
    double_nl = re.compile(r"\n\s*\n\s*\n")
    f_inner = f_tag = f_dbl = 0
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        f_inner += len(inner_nl.findall(t))
        f_tag += len(tag_space.findall(t))
        f_dbl += len(double_nl.findall(t))
    print(f"{book}: p标签内换行={f_inner}  尖括号内空格={f_tag}  连续空行块={f_dbl}")
