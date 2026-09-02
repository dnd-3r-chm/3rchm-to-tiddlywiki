# -*- coding: utf-8 -*-
"""扫描 2 万物万法万律：排除 DND3R-FEEDBACK 区块后，对源文件做噪音分类。
修正：feedback 区块的 style 含 margin:/font-family: 等，会误判为 Word 噪音，需先剔除。
"""
import os, re

ROOT = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki"
BASE = os.path.join(ROOT, "2 万物万法万律")
FEEDBACK = re.compile(
    r"<!--\s*DND3R-FEEDBACK-BEGIN\s*-->.*?<!--\s*DND3R-FEEDBACK-END\s*-->", re.S | re.I
)
# 真正的 Word 噪音标记（排除 feedback 后）
WORD_MARKS = re.compile(
    r"mso-|WinCHM|<o:p|o:p>|FONT\s+face|SPAN\s+style|class=p\b|"
    r"xml:namespace|EndFragment|StartFragment|<!--\[if|v:\w+|<table",
    re.I,
)
TABLE = re.compile(r"<table", re.I)
BR = re.compile(r"<br\s*/?>", re.I)
BOOKS = ["MIC万物大全", "RC万律大全", "SpC万法大全"]

for book in BOOKS:
    d = os.path.join(BASE, book)
    clean, wordy = [], []
    tbl = br = 0
    for dp, _, ns in os.walk(d):
        for n in sorted(ns):
            if not n.lower().endswith(".htm"):
                continue
            p = os.path.join(dp, n)
            try:
                t = open(p, encoding="gb18030", errors="replace").read()
            except Exception:
                t = open(p, encoding="utf-8", errors="replace").read()
            t2 = FEEDBACK.sub("", t)
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            if WORD_MARKS.search(t2):
                wordy.append(rel)
            else:
                clean.append(rel)
            if TABLE.search(t2):
                tbl += 1
            if BR.search(t2):
                br += 1
    print(f"===== {book} =====")
    print(f"  Word噪音源 {len(wordy)} | 干净源 {len(clean)} | 合计 {len(wordy)+len(clean)}")
    print(f"  含 <table> 的页面 {tbl} | 含 <br> 的页面 {br}")
    if wordy:
        print("  -- Word噪音源 --")
        for f in wordy:
            print("     ", f)
    if clean:
        print("  -- 干净源 --")
        for f in clean:
            print("     ", f)
    print()
