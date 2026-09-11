# -*- coding: utf-8 -*-
"""只读检查：统计 PHB玩家手册 下所有 .tid 中的全角 ASCII(U+FF01-FF5E) 残留。

不修改任何文件。区分「标准中文标点(应保留)」与「需转半角/实体的符号」。
"""
import os
import re
from collections import Counter

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
PHB = os.path.join(BASE, r"wiki\tiddlers\0 核心三宝书\PHB玩家手册")

PAT = re.compile(r"[\uff01-\uff5e]")
# 标准中文标点：全角形态是正确的，不应转半角
KEEP = set("\uff0c\uff1b\uff1a\uff1f\uff01")  # ， ； ： ？ ！

cnt = Counter()
file_hit = Counter()
for root, _, fs in os.walk(PHB):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        hit = set(PAT.findall(s))
        for ch in PAT.findall(s):
            cnt[ch] += 1
        for ch in hit:
            file_hit[ch] += 1

if not cnt:
    print("PHB 内无任何全角 ASCII 残留。")
else:
    print("字符  Unicode  ASCII对应  出现次数  涉及文件  分类")
    print("-" * 68)
    for ch, n in sorted(cnt.items(), key=lambda x: -x[1]):
        code = ord(ch)
        asc = chr(code - 0xFEE0)
        kind = "中文标点(保留)" if ch in KEEP else "需转半角/实体"
        print(
            " %s    U+%04X      %-4s      %6d   %6d   %s"
            % (ch, code, asc, n, file_hit[ch], kind)
        )
    print("-" * 68)
    todo = sum(n for ch, n in cnt.items() if ch not in KEEP)
    keep = sum(n for ch, n in cnt.items() if ch in KEEP)
    print("合计：需处理 %d 处，中文标点保留 %d 处" % (todo, keep))
