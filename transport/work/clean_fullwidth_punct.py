#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把已转换 tiddler 中的全角 ASCII 归一半角（一次性补齐现有内容，与转换管道规则一致）。

用户规则（2026-09-02 扩展）：tid 正文内不得出现全角英文字母 A-Za-z、数字 0-9、
括号 （）、弯引号 ""''。本脚本与 convert_pilot.normalize_fullwidth_punct 使用同一映射，
对全库已转换 tid 回溯补齐。
跳过 $__ 前缀的系统/手动维护文件（$:/tags/SideBar、$:/DefaultTiddlers 等）。

用法：
    python clean_fullwidth_punct.py          # 干跑，打印受影响文件与替换数
    python clean_fullwidth_punct.py --apply  # 实际写入
"""
import _paths as P
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI_TIDDLERS = P.WIKI_TIDDLERS
MAP = {
    # 弯引号 -> 直引号
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    # 全角括号
    "\uff08": "(", "\uff09": ")",
}
# 全角字母 A-Z / a-z
for i in range(26):
    MAP[chr(0xFF21 + i)] = chr(0x41 + i)
    MAP[chr(0xFF41 + i)] = chr(0x61 + i)
# 全角数字 ０-９
for i in range(10):
    MAP[chr(0xFF10 + i)] = chr(0x30 + i)


def main():
    apply = "--apply" in sys.argv
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
            rel = os.path.relpath(path, WIKI_TIDDLERS)
            if apply:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
            total_files += 1
            total_repl += count
            by_file.append((rel, count))
    print(f"files changed: {total_files}, replacements: {total_repl}"
          + ("" if apply else "  （干跑，未写入，加 --apply 执行）"))
    for rel, n in sorted(by_file, key=lambda x: -x[1])[:40]:
        print(f"  {n:5d}  {rel}")


if __name__ == "__main__":
    main()
