# -*- coding: utf-8 -*-
"""全角 ＋(U+FF0B) -> 半角 +。

纯符号无语境歧义，直接替换。跳过 0 核心三宝书\\PHB玩家手册（已排版完成，仅统计不改），
仅备份受影响文件。
"""
import os, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_plus_" + TS)
SKIP = "0 核心三宝书\\PHB玩家手册\\"

total = 0
files = 0
phb_n = 0
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        if "\uff0b" not in s:
            continue
        n = s.count("\uff0b")
        if rel.startswith(SKIP):
            phb_n += n
            continue
        # 跳过系统 tiddler
        title_line = ""
        for line in s.split("\n", 5):
            if line.startswith("title:"):
                title_line = line
                break
        if "$:/" in title_line:
            continue
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s.replace("\uff0b", "+"))
        files += 1
        total += n
        print("fixed: %s (%d 处)" % (rel, n))
print("files:", files, "replaced:", total, "| PHB(跳过)内未处理:", phb_n)
