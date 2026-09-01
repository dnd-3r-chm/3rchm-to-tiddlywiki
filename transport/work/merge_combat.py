# -*- coding: utf-8 -*-
"""合并目录下 hhc 子节点到父节点 tiddler（格式参考 DMG 简介.tid）。

用法：
    python merge_combat.py <父节点目录> <父节点祖先路径(hhc)> <父节点.tid文件名>
示例：
    python merge_combat.py "E:\\...\\第二章\\战斗中的生物体型大小" \
        "核心三宝书 / [DMG] 城主指南 / 第二章：运用规则 / 战斗中的生物体型大小" \
        "战斗中的生物体型大小.tid"

- 顺序 = hhc_mapping.csv 中 祖先路径匹配的行序
- 文件名按源文件 basename 取（可能有全角括号等），不依赖 hhc 标题
- 父节点自身内容保留开头；子节点标题 h1->h2 降级；<p>&nbsp;</p> 分隔；闭标签随开标签降级
- 不合并：目录下非 hhc 子节点的文件（平级节点）
"""
import _paths as P
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 4:
    print("usage: python merge_combat.py <DIR> <PARENT_ANCESTOR> <PARENT_TID>")
    sys.exit(1)

DIR = sys.argv[1]
PARENT_ANCESTOR = sys.argv[2]
PARENT_TID = sys.argv[3]
HHC_CSV = os.path.join(P.WORK, "hhc_mapping.csv")


def read_body(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    return parts[1] if len(parts) == 2 else content


def demote_headings(body):
    def repl_open(m):
        level = int(m.group(1))
        return f"<h{min(level + 1, 6)}{m.group(2)}"

    def repl_close(m):
        level = int(m.group(1))
        return f"</h{min(level + 1, 6)}>"

    body = re.sub(r"<h([1-6])([ >])", repl_open, body)
    body = re.sub(r"</h([1-6])>", repl_close, body)
    return body


def main():
    with open(HHC_CSV, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["祖先路径"] == PARENT_ANCESTOR]
    print("hhc children:", len(rows))

    parent_path = os.path.join(DIR, PARENT_TID)
    chunks = [read_body(parent_path).strip()]
    deleted = []
    missing = []
    for r in rows:
        name = os.path.splitext(os.path.basename(r["源文件相对路径"]))[0]
        path = os.path.join(DIR, name + ".tid")
        if not os.path.exists(path):
            missing.append(name)
            continue
        body = demote_headings(read_body(path).strip())
        chunks.append("<p>&nbsp;</p>\n" + body)
        deleted.append(path)

    if missing:
        print("MISSING:", missing)
        return

    with open(parent_path, encoding="utf-8") as f:
        head = f.read().split("\n\n", 1)[0]
    merged = "\n\n".join(chunks) + "\n"
    with open(parent_path, "w", encoding="utf-8") as f:
        f.write(head + "\n\n" + merged)
    print(f"[OK] 战斗.tid merged, len={len(merged)}, deleted={len(deleted)}")

    for p in deleted:
        os.remove(p)
    print("deleted all child tids")


if __name__ == "__main__":
    main()
