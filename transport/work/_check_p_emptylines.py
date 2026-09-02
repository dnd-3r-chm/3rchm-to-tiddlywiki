# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]:
    d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", book)
    # 在 p 标签内部含空行 / 标签尖括号内多空格
    pat_inner = re.compile(r"<p[^>]*>\s*\n\s*\n")  # p 开始后紧接着空行
    pat_tagspace = re.compile(r"<p\s+>|<p\s+[^>]*\s+>")  # 尖括号内多余空格
    n_inner = n_tag = n_files = 0
    sample = []
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        a = len(pat_inner.findall(t)); b = len(pat_tagspace.findall(t))
        if a or b:
            n_files += 1
            n_inner += a; n_tag += b
            if len(sample) < 3:
                m = pat_inner.search(t)
                if m:
                    s = t[max(0, m.start()-30): m.end()+80]
                    sample.append((os.path.relpath(p, ROOT), repr(s)))
    print(f"=== {book} === 文件数:{n_files}  标签内空行处:{n_inner}  尖括号内空格处:{n_tag}")
    for r, s in sample:
        print("  ", r, s)
