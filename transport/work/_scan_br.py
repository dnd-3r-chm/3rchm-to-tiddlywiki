# -*- coding: utf-8 -*-
import os, re

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR_RE = re.compile(r"<br\s*/?>", re.I)

def walk(d):
    for dp, _, ns in os.walk(d):
        for n in sorted(ns):
            if not n.lower().endswith(".tid"):
                continue
            p = os.path.join(dp, n)
            t = open(p, encoding="utf-8").read()
            cnt = len(BR_RE.findall(t))
            if cnt == 0:
                continue
            rel = os.path.relpath(p, BASE)
            # 分类：在 table 内 vs 在 table 外
            in_tbl = 0
            out_tbl = 0
            for m in BR_RE.finditer(t):
                seg = t[max(0, m.start()-200):m.start()]
                if re.search(r"<table[^>]*>", seg) and not re.search(r"</table>", seg):
                    in_tbl += 1
                else:
                    out_tbl += 1
            print(f"{rel}  总{cnt}  表内{in_tbl}  表外{out_tbl}")

walk(BASE)
