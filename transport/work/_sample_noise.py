# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

def show(book, k, rx, n=2):
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
            print(f"[{book}] {k}: {os.path.relpath(p, TID)}")
            i = m.start()
            print("   ", repr(body[max(0,i-40):i+50]))
            cnt += 1
            if cnt >= n:
                break

word_fragment = re.compile(r"StartFragment|EndFragment|&nbsp;|<o:p>|<o:P>|class=\"?Mso|mso-|xml:namespace|<u1:p>|<u1:P>|<!--", re.I)
span_font_style = re.compile(r"</?span[\s>]|</?font[\s>]|style=", re.I)
tag_attr_nl = re.compile(r"<\w+\s*\n\s*\w+\s*=")
tag_space = re.compile(r"<p\s+>|<p\s+\w")
fullwidth = re.compile(r"[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]")

print("=== 三宝书 word_fragment 抽样 ===")
show("0 核心三宝书", "word_fragment", word_fragment, 3)
print("\n=== 三宝书 span_font_style 抽样 ===")
show("0 核心三宝书", "span_font_style", span_font_style, 3)
print("\n=== 补充书 tag_attr_nl 抽样 ===")
show("1 核心补充书籍", "tag_attr_nl", tag_attr_nl, 3)
print("\n=== 补充书 tag_space 抽样 ===")
show("1 核心补充书籍", "tag_space", tag_space, 3)
print("\n=== 补充书 fullwidth 抽样 ===")
show("1 核心补充书籍", "fullwidth", fullwidth, 3)
print("\n=== 附录 word_fragment 抽样 ===")
show("10 附录", "word_fragment", word_fragment, 3)
