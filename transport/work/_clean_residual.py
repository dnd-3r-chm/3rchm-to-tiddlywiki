# -*- coding: utf-8 -*-
"""通用后处理：对 MM3/MM4/MM5 所有 tid 应用 normalize 去残留 span/style/lang，
并压掉 <p> 内部换行与尖括号内空格。不重排字段（干净 p 不受影响）。"""
import os, glob, re
import clean_mm3 as c

P_INNER = re.compile(r"(<p[^>]*>)([\s\S]*?)(</p>)", re.I)

def fix_p_inner(body):
    def r(m):
        pre, inner, post = m.group(1), m.group(2), m.group(3)
        # 尖括号内空格
        pre = re.sub(r"\s+>", ">", pre)
        inner = re.sub(r"\s*\n\s*", " ", inner).strip()
        return pre + inner + post
    return P_INNER.sub(r, body)

books = ["MM3怪物图鉴3", "MM4怪物图鉴4", "MM5怪物图鉴5"]
total = 0
for book in books:
    d = os.path.join(c.P.WIKI_TIDDLERS, "1 核心补充书籍", book)
    for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        raw = open(p, encoding="utf-8").read()
        lines = raw.split("\n")
        header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
        nb = c.normalize(body)
        nb = fix_p_inner(nb)
        # 全角括号 -> 半角（兜底全文，遵守 tid 内禁全角（）规则）
        nb = nb.replace("（", "(").replace("）", ")")
        # 压掉 body 开头多余空行（保留与 header 之间 1 空行）
        nb = nb.lstrip("\n")
        new_header = header.replace("（", "(").replace("）", ")")
        if nb != body or new_header != header:
            with open(p, "w", encoding="utf-8") as f:
                f.write(new_header + "\n" + nb)
            total += 1
print("处理后写入文件数:", total)
