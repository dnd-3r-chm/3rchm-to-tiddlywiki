# -*- coding: utf-8 -*-
"""检查 SKIP_SOURCES 中是否已含手动调整过（合并/拆分）的父节点源文件。"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

src = open(r"E:\dnd3r_full\transport\work\convert_book.py", encoding="utf-8").read()
start = src.index("SKIP_SOURCES")
end = src.index("}", start)
block = src[start:end]
entries = set(re.findall(r'r"([^"]+)"', block))

parents = [
    "DM是什么？.htm", "游戏风格.htm", "简介.htm", "跑团.htm", "保持游戏平衡.htm",
    "改变规则.htm", "布置舞台.htm", "处理玩家人物的行动.htm", "更多移动规则.htm", "战斗.htm",
]
for p in parents:
    hit = [e for e in entries if e.replace("\\", "/").endswith(p)]
    print(("IN     " if hit else "MISSING") + " " + p)
