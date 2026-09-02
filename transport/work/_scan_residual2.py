# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

def show(book, rx, n=4, label=""):
    bd = os.path.join(TID, book)
    cnt = 0
    for p in glob.glob(os.path.join(bd, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        parts = t.split("\n")
        body = "\n".join(parts[5:]) if len(parts) > 5 else ""
        m = rx.search(body)
        if m:
            print(f"[{book}] {label}: {os.path.relpath(p, TID)}")
            i = m.start()
            print("   ", repr(body[max(0,i-35):i+45]))
            cnt += 1
            if cnt >= n:
                return

word_fragment = re.compile(r"StartFragment|EndFragment|&nbsp;|<o:p>|<o:P>|class=\"?Mso|mso-|xml:namespace|<u1:p>|<u1:P>", re.I)
comment = re.compile(r"<!--")
tag_space = re.compile(r"<p\s+>|<p\s+\w")
tag_inner_nl = re.compile(r"<p[^>]*>\s*\n")

print("=== 三宝书 word_fragment (实际看是否注释) ===")
show("0 核心三宝书", word_fragment, 4, "word_fragment")
print("\n=== 三宝书 comment <!-- ===")
show("0 核心三宝书", comment, 4, "comment")
print("\n=== 补充书 tag_space ===")
show("1 核心补充书籍", tag_space, 4, "tag_space")
print("\n=== 补充书 tag_inner_nl ===")
show("1 核心补充书籍", tag_inner_nl, 4, "tag_inner_nl")
print("\n=== 附录 tag_space ===")
show("10 附录", tag_space, 4, "tag_space")
