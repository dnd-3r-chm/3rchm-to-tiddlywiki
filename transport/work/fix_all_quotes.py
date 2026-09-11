# -*- coding: utf-8 -*-
# 将 wiki/tiddlers 下所有用户 .tid 的弯引号/全角引号统一为半角直引号，幂等。
# 跳过系统 tiddler(title 以 $:/ 开头)，仅备份受影响文件。
import os, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_quotes_" + TS)

MAP = {
    '\u201c': '"', '\u201d': '"',
    '\u2018': "'", '\u2019': "'",
    '\uff02': '"', '\uff07': "'",
}

count = 0
baks = 0
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
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
        if not any(k in s for k in MAP):
            continue
        rel = os.path.relpath(p, SRC)
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        baks += 1
        t = s
        for k, v in MAP.items():
            if k in t:
                t = t.replace(k, v)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
        count += 1
        print("fixed:", rel)
print("backed up:", baks, "fixed:", count)
