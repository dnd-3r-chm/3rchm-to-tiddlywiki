# -*- coding: utf-8 -*-
"""合并 更多移动规则/ 目录下 9 个子节点到 更多移动规则.tid（格式参考 DMG 简介.tid）。

规则：
- 顺序按 hhc：移动与方格、移动与位置、度量与方格、斜向方格移动、防具与负重量、
  三维空间的移动、空中战术移动、逃逸与追赶、方格间的活动（标准度量与父同源，无独立内容，跳过）
- 父节点自身内容保留在开头；子节点内容整体标题降一级（h1->h2 ... h6 保持），节点间 <p>&nbsp;</p> 分隔
"""
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DIR = os.path.join(P.DMG_TIDDLERS, "第二章", "更多移动规则")
ORDER = ["移动与方格", "移动与位置", "度量与方格", "斜向方格移动",
         "防具与负重量", "三维空间的移动", "空中战术移动", "逃逸与追赶", "方格间的活动"]


def read_body(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    return parts[1] if len(parts) == 2 else content


def demote_headings(body):
    """h1->h2, h2->h3, ... h6 保持（参考简介.tid 的合并格式）；开闭标签一起降级。"""
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
    parent = read_body(os.path.join(DIR, "更多移动规则.tid")).strip()
    chunks = [parent]
    for name in ORDER:
        path = os.path.join(DIR, name + ".tid")
        if not os.path.exists(path):
            print("MISSING:", name)
            continue
        body = demote_headings(read_body(path).strip())
        chunks.append("<p>&nbsp;</p>\n" + body)
    merged = "\n\n".join(chunks) + "\n"

    # 重写父节点（保留原头部）
    parent_path = os.path.join(DIR, "更多移动规则.tid")
    with open(parent_path, encoding="utf-8") as f:
        head = f.read().split("\n\n", 1)[0]
    with open(parent_path, "w", encoding="utf-8") as f:
        f.write(head + "\n\n" + merged)
    print(f"[OK] 更多移动规则.tid 合并完成，长度 {len(merged)}")

    # 删除子节点
    for name in ORDER:
        p = os.path.join(DIR, name + ".tid")
        if os.path.exists(p):
            os.remove(p)
            print("deleted:", name + ".tid")


if __name__ == "__main__":
    main()
