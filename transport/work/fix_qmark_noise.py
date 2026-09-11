# -*- coding: utf-8 -*-
"""清理解码失败产生的 '?' 噪音。

成因：源 htm 主体为 gb18030，但混入了 UTF-8 编码的空格/符号（多为 Word 的
<span style='mso-spacerun:yes'> 排版占位），3 字节字符按 gb18030 解码时逐字节
失败被替换为 '?'，于是正文出现 '???'，链接显示文本出现 '??'，图片标签后出现 '?'。

处理（均属无语义的排版占位，可安全删除）：
  1. 连续 2+ 个半角 '?' 及其后空白 -> 删除
  2. ]] 之后紧跟的孤立 '?'（如 [img[...]]?）-> 删除该 '?'
"""
import datetime
import os
import re
import shutil

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_qmark_" + TS)

PAT_MULTI = re.compile(r"\?{2,}[ \t]*")   # ??? / ?? 及后跟空白
PAT_AFTER_BR = re.compile(r"(\]\])\?")    # [img[...]]? / [[...]]?

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
        if not (PAT_MULTI.search(s) or PAT_AFTER_BR.search(s)):
            continue
        new, n1 = PAT_MULTI.subn("", s)
        new, n2 = PAT_AFTER_BR.subn(r"\1", new)
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)
        total_files += 1
        total_hits += n1 + n2
        print("fixed: %s (%d 处)" % (rel, n1 + n2))
print("文件 %d  修复 %d 处" % (total_files, total_hits))
print("备份 ->", BAK)
