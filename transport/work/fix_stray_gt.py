# -*- coding: utf-8 -*-
"""修复 clean_*._td() bug 产生的多余 '>'。

bug：return f"<td {' '.join(kept)}>".rstrip() + ">" —— 标签已完整却再多拼一个 '>'，
产出 <td colspan=2>>，多余的 '>' 变成正文文本（如 ">>40尺(8格)>>"）。

本脚本仅删除「带 colspan/rowspan 的 <td> 开标签之后紧邻的多余 >」，
不影响正常的 <td>内容 结构，也不触碰 </td> 或其它标签。
"""
import datetime
import os
import re
import shutil

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_straygt_" + TS)

# 仅匹配：含 colspan/rowspan 的 td 开标签，其后紧邻的一个或多个多余 >
PAT = re.compile(r"(<td\b[^>]*?\b(?:colspan|rowspan)\b[^>]*>)>+", re.I)

total_files = 0
total_hits = 0
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        if not PAT.search(s):
            continue
        new, n = PAT.subn(r"\1", s)
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)
        total_files += 1
        total_hits += n
        print("fixed: %s (%d 处)" % (rel, n))
print("文件 %d  修复 %d 处" % (total_files, total_hits))
print("备份 ->", BAK)
