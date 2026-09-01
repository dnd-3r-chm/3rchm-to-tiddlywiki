# -*- coding: utf-8 -*-
"""把以 · 开头的 <p> 段落转换为 <ul><li>（用户规则 2026-08-30）。

- <p>· 内容</p> / <p class="list-item">· 内容</p> -> <li>内容</li>
- 连续的多个转换后合并进同一个 <ul>；单个的包 <ul>...</ul>
- 仅处理内容以 ·（或 •）开头的 p，其余 p 不动
"""
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = P.WIKI_TIDDLERS

# 匹配以 · 开头的整个 <p>...</p>（p 内不含嵌套 p）
P_RE = re.compile(r"<p[^>]*>\s*[·•]\s*(?:(?!</p>).)*?</p>", re.S)


def convert(text):
    matches = list(P_RE.finditer(text))
    if not matches:
        return text
    # 分组：相邻 match 之间只有空白则并为一组
    groups = []
    for m in matches:
        if groups and not text[groups[-1][-1].end():m.start()].strip():
            groups[-1].append(m)
        else:
            groups.append([m])
    # 从后往前替换
    for g in reversed(groups):
        items = []
        for m in g:
            inner = m.group(0)
            inner = re.sub(r"^<p[^>]*>\s*[·•]\s*", "<li>", inner)
            inner = re.sub(r"</p>$", "</li>", inner)
            items.append(inner.strip())
        ul = "<ul>\n" + "\n".join(items) + "\n</ul>"
        text = text[:g[0].start()] + ul + text[g[-1].end():]
    return text


files_changed = 0
groups_total = 0
for dp, _, ns in os.walk(WIKI):
    for n in ns:
        if not n.lower().endswith(".tid") or n.startswith("$__"):
            continue
        path = os.path.join(dp, n)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        orig = content
        content = convert(content)
        if content != orig:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            files_changed += 1
            groups_total += len(P_RE.findall(orig)) and 0  # placeholder
            # 统计原 ·p 数量
            groups_total += len(P_RE.findall(orig))

print(f"files changed: {files_changed}, bullet paragraphs converted: {groups_total}")
