# -*- coding: utf-8 -*-
"""统计 .tid 正文中的 class="g" / "l" / "w" 分布，供清理前评估。

只统计正文（跳过 .tid 头部字段），按书籍分类汇总，
并列出每种 class 出现在哪些标签上（tr/td/div/span...）。
"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = r"E:\dnd3r_full\transport\wiki\tiddlers"

# 精确匹配 class 属性值中恰好为 g / l / w（单值），以及多值中的 g/l/w
CLASS_RE = re.compile(r'class\s*=\s*"([^"]*)"', re.I)
TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b", re.I)

TARGETS = {"g", "l", "w"}


def split_body(content):
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "":
            return "\n".join(lines[i + 1:])
    return content


def main():
    # 书籍 -> 计数
    by_book = collections.Counter()
    # (标签, class) -> 计数
    by_tag = collections.Counter()
    # 文件级明细
    files = collections.defaultdict(collections.Counter)
    total = 0

    for dp, _, ns in os.walk(WIKI):
        for n in ns:
            if not n.lower().endswith(".tid") or n.startswith("$__"):
                continue
            path = os.path.join(dp, n)
            rel = os.path.relpath(path, WIKI)
            if rel in ("总目录.tid", "CHM目录侧边栏.tid"):
                continue
            with open(path, encoding="utf-8") as f:
                content = f.read()
            body = split_body(content)

            book = rel.split(os.sep)[0] if os.sep in rel else "(根目录)"
            if book.startswith("0 核心三宝书"):
                parts = rel.split(os.sep)
                book = parts[1] if len(parts) > 1 else book

            for m in CLASS_RE.finditer(body):
                vals = m.group(1).split()
                hit = TARGETS & {v.lower() for v in vals}
                if not hit:
                    continue
                # 回找该属性所属标签：从属性位置往前取最近的 <tag
                seg = body[:m.start()]
                tag_m = None
                for tm in TAG_RE.finditer(seg):
                    if not tm.group(1):  # 开标签
                        tag_m = tm
                tag = (tag_m.group(2).lower() if tag_m else "?")
                for c in sorted(hit):
                    by_book[book] += 1
                    by_tag[(tag, c)] += 1
                    files[rel][c] += 1
                    total += 1

    print(f"总计命中: {total}")
    print("\n按书籍:")
    for b, c in by_book.most_common():
        print(f"  {c:5d}  {b}")

    print("\n按 (标签, class):")
    for (t, c), n in by_tag.most_common():
        print(f"  {n:5d}  <{t}> class=\"{c}\"")

    print(f"\n涉及文件数: {len(files)}")
    print("\n明细（每个文件各类计数）:")
    for f in sorted(files):
        print(f"  {dict(files[f])}  {f}")


if __name__ == "__main__":
    main()
