# -*- coding: utf-8 -*-
"""修复全角句点 ．(U+FF0E)：数字之间 -> .，其余(中文句末) -> 。(中文句号)。

语境判定取原串相邻字符，不消费上下文，故连续 ．． 也能逐处正确处理。
跳过 0 核心三宝书\\PHB玩家手册（用户要求），仅备份受影响文件，输出全部替换明细。
"""
import os, re, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_period_" + TS)
SKIP = "0 核心三宝书\\PHB玩家手册\\"


def decide(s, i, j):
    """数字+数字(3．5 小数)或 数字+中文(1．选择 编号列表) -> .；其余(中文句末) -> 。"""
    prev = s[i - 1] if i > 0 else ""
    nxt = s[j] if j < len(s) else ""
    if prev.isdigit() and (nxt.isdigit() or "\u4e00" <= nxt <= "\u9fff"):
        return "."
    return "\u3002"


def repl(m):
    return decide(m.string, m.start(), m.end())


total = 0
files = 0
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        if rel.startswith(SKIP):
            continue
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        # 跳过系统 tiddler
        title_line = ""
        for line in s.split("\n", 5):
            if line.startswith("title:"):
                title_line = line
                break
        if "$:/" in title_line:
            continue
        if "\uff0e" not in s:
            continue
        details = []
        for m in re.finditer(r"\uff0e", s):
            i, j = m.start(), m.end()
            prev = s[i - 1] if i > 0 else ""
            nxt = s[j] if j < len(s) else ""
            details.append("%s\uff0e%s  =>  %s" % (prev, nxt, decide(s, i, j)))
        new = re.sub(r"\uff0e", repl, s)
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)
        files += 1
        total += len(details)
        print("fixed: %s (%d 处)" % (rel, len(details)))
        for d in details:
            print("    ", d)
print("files:", files, "total:", total)
