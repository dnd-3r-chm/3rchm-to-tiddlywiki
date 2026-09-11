# -*- coding: utf-8 -*-
"""其它常见全角 ASCII 符号 -> 半角（全库，含 PHB；2026-09-07）。

转：＃ ＄ ％ ＊ ＋ － ／ ＝ ＠ ＾ ＿ ｜ ～ ＼
不转：，；：？！(中文标点)  ＆(走 &amp; 实体)  ＜＞(会破坏 HTML)  ．(已按语境处理完)
"""
import os, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_symbols_" + TS)

TRANS = {
    "\uff03": "#", "\uff04": "$", "\uff05": "%", "\uff0a": "*",
    "\uff0b": "+", "\uff0d": "-", "\uff0f": "/", "\uff1d": "=",
    "\uff20": "@", "\uff3c": "\\", "\uff3e": "^", "\uff3f": "_",
    "\uff5c": "|", "\uff5e": "~",
    # 全角 ＜＞ 走实体(与 ＆->&amp; 同理)；半角 <> 是 HTML 标签，绝不能碰
    "\uff1c": "&lt;", "\uff1e": "&gt;",
    # 全角方括号(2026-09-07，PHB 残留 20 处)
    "\uff3b": "[", "\uff3d": "]",
}
TABLE = str.maketrans(TRANS)

total = 0
files = 0
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        n = sum(s.count(k) for k in TRANS)
        if n == 0:
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
            fh.write(s.translate(TABLE))
        files += 1
        total += n
        print("fixed: %s (%d 处)" % (rel, n))
print("files:", files, "replaced:", total)
