# -*- coding: utf-8 -*-
"""全库标题重命名：旧格式 -> 新格式 具体标题 (缩写-书名) / 具体标题 (所属内容)。

- title 行：按旧 final_mapping -> 新 final_mapping（源路径 join）映射替换
- 内容链接目标：[[显示|旧目标]] -> [[显示|新目标]]、[[旧目标]] -> [[新目标]]（显示名不变）
- 跳过 $__ 系统文件与 总目录.tid/CHM目录侧边栏.tid（重跑 generate_toc.py 覆盖）
"""
import _paths as P
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = P.WIKI_TIDDLERS
OLD_CSV = os.path.join(P.WORK, "final_mapping.csv.old-title-format")
NEW_CSV = os.path.join(P.WORK, "final_mapping.csv")


def load(path):
    m = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m[r["源文件相对路径"]] = r["Tiddler标题"]
    return m


old_map = load(OLD_CSV)
new_map = load(NEW_CSV)
rename = {}
for src, old_t in old_map.items():
    new_t = new_map.get(src)
    if new_t and new_t != old_t:
        rename[old_t] = new_t
print("rename entries:", len(rename))

# 校验映射无歧义（一个旧标题 -> 多个新标题 或反之）
from collections import Counter
c1 = Counter(rename.values())
multi = {t: n for t, n in c1.items() if n > 1}
if multi:
    print("WARN multi-target:", multi)

LINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]+))?\]\]")


def replace_links(text):
    def repl(m):
        display = m.group(1)
        target = m.group(2)
        if target and target in rename:
            return f"[[{display}|{rename[target]}]]"
        if not target and display in rename:
            return f"[[{rename[display]}]]"
        return m.group(0)
    return LINK_RE.sub(repl, text)


files_changed = 0
title_changed = 0
for dirpath, _, names in os.walk(WIKI):
    for name in names:
        if not name.lower().endswith(".tid"):
            continue
        if name.startswith("$__"):
            continue
        if name in ("总目录.tid", "CHM目录侧边栏.tid"):
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        orig = content
        # title 行（仅第一处）
        m = re.match(r"^(title:\s*)(.+)$", content, re.M)
        if m and m.group(2).strip() in rename:
            content = content[:m.start()] + m.group(1) + rename[m.group(2).strip()] + content[m.end():]
            title_changed += 1
        # 链接目标
        content = replace_links(content)
        if content != orig:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            files_changed += 1

print(f"files changed: {files_changed}, title lines changed: {title_changed}")
