#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把已转换 tiddler 中的全角引号/括号替换为半角（一次性补齐现有内容，与转换管道规则一致）。

与 convert_pilot.normalize_fullwidth_punct 使用同一映射：
    “ ” -> " "    （ ） -> ( )
跳过 $__ 前缀的系统/手动维护文件（$:/tags/SideBar、$:/DefaultTiddlers 等）。
"""
import _paths as P
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI_TIDDLERS = P.WIKI_TIDDLERS
MAP = {"\u201c": '"', "\u201d": '"', "\uff08": "(", "\uff09": ")"}


def main():
    total_files = 0
    total_repl = 0
    by_file = []
    for dirpath, _, names in os.walk(WIKI_TIDDLERS):
        for name in names:
            if not name.lower().endswith(".tid"):
                continue
            # 跳过系统/手动维护 tiddler（$__ 前缀，任何脚本不得覆盖）
            if name.startswith("$__"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            count = sum(content.count(ch) for ch in MAP)
            if count == 0:
                continue
            new = content.translate(str.maketrans(MAP))
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            rel = os.path.relpath(path, WIKI_TIDDLERS)
            total_files += 1
            total_repl += count
            by_file.append((rel, count))
    print(f"files changed: {total_files}, replacements: {total_repl}")
    for rel, n in sorted(by_file, key=lambda x: -x[1])[:30]:
        print(f"  {n:5d}  {rel}")


if __name__ == "__main__":
    main()
