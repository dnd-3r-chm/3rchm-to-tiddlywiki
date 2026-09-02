# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

def show(book, rx, n=6, label=""):
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
            print("   ", repr(body[max(0,i-30):i+50]))
            cnt += 1
            if cnt >= n:
                return

tag_space = re.compile(r"<p\s+>|<p\s+\w")   # 误报源：<p align 合法
tag_space_real = re.compile(r"<p\s+>")        # 真·<p > 空属性
tag_inner_nl = re.compile(r"<p[^>]*>\s*\n")   # p 开始后换行

print("=== 三宝书 tag_space (看是否真 <p >) ===")
show("0 核心三宝书", tag_space_real, 6, "<p >")
print("\n=== 补充书 tag_space_real <p > ===")
show("1 核心补充书籍", tag_space_real, 6, "<p >")
print("\n=== 附录 tag_space_real <p > ===")
show("10 附录", tag_space_real, 6, "<p >")
print("\n=== 补充书 tag_inner_nl 真实样本 ===")
show("1 核心补充书籍", tag_inner_nl, 6, "p内换行")
print("\n=== 三宝书 tag_inner_nl 真实样本 ===")
show("0 核心三宝书", tag_inner_nl, 3, "p内换行")
