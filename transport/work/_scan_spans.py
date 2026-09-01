# -*- coding: utf-8 -*-
"""统计「所有DMG表格」中 表X-X 节点的 <span> 标签分布，清理前评估。

按 span 的属性分为两类：
  * CLASS 型：class="note-ref"/"price"/"note-label"... —— 全局样式表无定义，失效
  * STYLE 型：style="font-weight:600;"... —— 内联样式，真实生效，删除会改变外观

用法：
    python _scan_spans.py
"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = r"E:\dnd3r_full\transport\wiki\tiddlers\0 核心三宝书\DMG城主指南\所有DMG表格"

# 文件名格式 表X-X（X 为一位或多位数字），如 表2-1、表3-25
NAME_RE = re.compile(r"^表\d+-\d+")

SPAN_RE = re.compile(r"<span([^>]*)>(.*?)</span>", re.S)


def split_body(content):
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "":
            return "\n".join(lines[i + 1:])
    return content


def main():
    files = {}
    for dp, _, ns in os.walk(BASE):
        for n in sorted(ns):
            if not n.lower().endswith(".tid"):
                continue
            stem = os.path.splitext(n)[0]
            if not NAME_RE.match(stem):
                continue
            files[os.path.join(dp, n)] = stem

    kind_counter = collections.Counter()   # (kind, attr摘要) -> 数量
    by_file = collections.Counter()
    samples = {}
    total = 0

    for path, stem in files.items():
        with open(path, encoding="utf-8") as f:
            content = f.read()
        body = split_body(content)
        rel = os.path.relpath(path, BASE)
        for m in SPAN_RE.finditer(body):
            attrs, inner = m.group(1).strip(), m.group(2)
            total += 1
            by_file[rel] += 1
            if "style=" in attrs:
                kind = "STYLE"
            elif "class=" in attrs:
                kind = "CLASS"
            else:
                kind = "PLAIN"
            key = (kind, attrs if len(attrs) < 90 else attrs[:87] + "...")
            kind_counter[key] += 1
            samples.setdefault(key, (rel, inner.strip()[:40]))

    print(f"匹配「表X-X」的文件: {len(files)} 个")
    print(f"span 总计: {total}\n")

    print("按类型 / 属性：")
    for (kind, attrs), c in kind_counter.most_common():
        rel, s = samples[(kind, attrs)]
        print(f"  [{kind}] {c:4d}  <span{attrs}>")
        print(f"          样例: {s}   ({rel})")

    print(f"\n按文件（{len(by_file)} 个有 span）：")
    for f, c in by_file.most_common():
        print(f"  {c:4d}  {f}")


if __name__ == "__main__":
    main()
