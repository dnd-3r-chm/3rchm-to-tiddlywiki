# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

# 各类噪音正则（正文部分，即第6行起）
checks = {
    "word_fragment": re.compile(r"StartFragment|EndFragment|&nbsp;|<o:p>|<o:P>|class=\"?Mso|mso-|xml:namespace|<u1:p>|<u1:P>|<!--", re.I),
    "span_font_style": re.compile(r"</?span[\s>]|</?font[\s>]|style=", re.I),
    "tag_inner_nl": re.compile(r"<p[^>]*>\s*\n"),          # p 标签开始后换行（标签内空行）
    "tag_attr_nl": re.compile(r"<\w+\s*\n\s*\w+\s*="),     # 标签属性被换行断开，如 <p \n align=
    "tag_space": re.compile(r"<p\s+>|<p\s+\w"),            # 尖括号内空格（部分）
    "empty_p": re.compile(r"<p(?:\s[^>]*)?>\s*(?:&nbsp;|\s)*</p>", re.I),
    "fullwidth": re.compile(r"[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]"),
    "double_nl": re.compile(r"\n\s*\n\s*\n"),             # 连续空行块
    "stray_o_p": re.compile(r"<o:p>|</o:p>|<o:P>|</o:P>", re.I),
}

books = []
for name in sorted(os.listdir(TID)):
    b = os.path.join(TID, name)
    if os.path.isdir(b) and not name.startswith("."):
        books.append(name)

summary = {}
for book in books:
    bd = os.path.join(TID, book)
    per_file = {k: [] for k in checks}
    n = 0
    for p in glob.glob(os.path.join(bd, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        n += 1
        t = open(p, encoding="utf-8").read()
        # 只查正文（跳过5行头）
        parts = t.split("\n")
        body = "\n".join(parts[5:]) if len(parts) > 5 else ""
        for k, rx in checks.items():
            if rx.search(body):
                per_file[k].append(os.path.relpath(p, TID))
    total_files = {k: len(v) for k, v in per_file.items()}
    summary[book] = (n, total_files)

print("书名 | tid数 | 各类噪音命中文件数")
for book, (n, tf) in summary.items():
    print(f"\n### {book}  (tid={n})")
    for k, cnt in tf.items():
        if cnt:
            print(f"   {k}: {cnt}")
