# -*- coding: utf-8 -*-
"""扫描 wiki/tiddlers 下所有 .tid，统计非 ASCII 数字实体（&#xNNNN; / &#NNN;）的分布。

只读扫描，不修改任何文件。用于定位「中文被写成十六进制实体」的影响范围。
"""
import os
import re
from collections import defaultdict

ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki", "tiddlers"
)
# 数字字符引用：&#x1F600; 或 &#160;
ENT = re.compile(r"&#(?:x([0-9A-Fa-f]+)|(\d+));", re.I)


def scan():
    stat = defaultdict(lambda: {"files": 0, "ents": 0})
    total_files = 0
    total_ents = 0
    examples = []

    for dirpath, _dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if not fn.endswith(".tid"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    s = f.read()
            except Exception as e:  # pragma: no cover
                print("ERR", p, e)
                continue

            n = 0
            for m in ENT.finditer(s):
                code = int(m.group(1), 16) if m.group(1) else int(m.group(2))
                if code > 127:  # 只统计非 ASCII（中文/全角标点）
                    n += 1
            if n:
                total_files += 1
                total_ents += n
                rel = os.path.relpath(p, ROOT)
                parts = rel.split(os.sep)
                key = os.sep.join(parts[:2]) if len(parts) >= 2 else "(root)"
                stat[key]["files"] += 1
                stat[key]["ents"] += n
                if len(examples) < 20:
                    examples.append((rel, n))

    print("=== 受影响文件总数: %d   非 ASCII 实体总数: %d" % (total_files, total_ents))
    print("\n=== 按目录分布（前 2 层） ===")
    for k, v in sorted(stat.items(), key=lambda x: -x[1]["ents"]):
        print("%8d 实体 / %4d 文件  %s" % (v["ents"], v["files"], k))
    print("\n=== 示例（前 20） ===")
    for rel, n in examples:
        print("%6d  %s" % (n, rel))


if __name__ == "__main__":
    scan()
