# -*- coding: utf-8 -*-
# 在 CC 表格的块级标签(table/thead/tbody/tr/caption)之间插入换行，
# 修复 </tr><tr> 粘连问题。不动 <td>/<th> 内部。
import os, re, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers\3 完美系列\CC完美斗士")
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "cc_tables_" + ts)

block = r"(?:table|thead|tbody|tr|caption)"
open_ = r"(<%s[^>]*>)" % block
close_ = r"(</%s>)" % block

def fix(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    text = re.sub(close_ + r"\s*" + open_, r"\1" + nl + r"\2", text)
    text = re.sub(open_ + r"\s*" + open_, r"\1" + nl + r"\2", text)
    text = re.sub(close_ + r"\s*" + close_, r"\1" + nl + r"\2", text)
    return text

shutil.copytree(SRC, BAK)
print("backup ->", BAK)

count = 0
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            orig = fh.read()
        new = fix(orig)
        if new != orig:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            rel = os.path.relpath(p, SRC)
            count += 1
            print("fixed: %s  lines %d -> %d" % (rel, orig.count("\n") + 1, new.count("\n") + 1))
print("total fixed files:", count)
