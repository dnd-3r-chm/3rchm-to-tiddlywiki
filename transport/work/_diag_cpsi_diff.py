# -*- coding: utf-8 -*-
"""诊断：星质构装体.tid 经 clean_body 后纯文本为何增加（对比 normalize 基线）。"""
import difflib
import html as H
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import clean_cpsi as cc

path = os.path.join(
    P.WIKI_TIDDLERS, "3 完美系列", "CPsi完美灵能", "6怪物", "星质构装体.tid"
)
raw = open(path, encoding="utf-8").read()
header, body = cc.split_tid(raw)
nb = cc.normalize(body)
new = cc.clean_body(body)

tb = re.sub(r"\s+", "", cc.strip_tags(H.unescape(nb)))
ta = re.sub(r"\s+", "", cc.strip_tags(H.unescape(new)))
print("基线(仅 normalize) %d 字符 -> 清洗后 %d 字符，差 %d" % (len(tb), len(ta), len(ta) - len(tb)))

sm = difflib.SequenceMatcher(None, tb, ta, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    a = tb[i1:i2]
    b = ta[j1:j2]
    print("\n[%s]" % tag)
    print("  基线片段(%d): %s" % (len(a), a[:150]))
    print("  清洗片段(%d): %s" % (len(b), b[:150]))
