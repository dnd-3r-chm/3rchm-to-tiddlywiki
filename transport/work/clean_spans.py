# -*- coding: utf-8 -*-
"""清理「所有DMG表格」中 表X-X 节点内的 <span> 标签（用户规则，2026-08-31）。

采用 unwrap：去掉 <span> 标签本身，保留其内部的文字/内容。
（span 内文字都是有意义的：价格、注释号、补充说明，不能连内容一起删。）

span 分三类，性质不同：
  * CLASS 型（66 处）：class="price"/"note-ref"/"note-label"/"ref-table"/
    "sub-cat"/"note" —— 全局样式表 cascading_stylesheet.css 未定义，属失效属性，
    清理后渲染结果不变。
  * STYLE 型（29 处）：style="font-weight:600;" 等内联样式 —— **真实生效**，
    清理会改变外观（注释号不再加粗、表头补充说明不再淡化），需用户确认。
  * PLAIN 型（3 处）：裸 <span>，无属性，清理无影响。

用法（参数为 ASCII 代号，勿传中文——PowerShell 会破坏命令行中文）：
    python clean_spans.py --kind class --dry     # 预览 CLASS 型
    python clean_spans.py --kind class           # 清理 CLASS 型（默认）
    python clean_spans.py --kind style --dry     # 预览 STYLE 型
    python clean_spans.py --kind all             # 清理全部
"""
import _paths as P
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = P.DMG_TABLES
BACKUP_DIR = os.path.join(P.WORK, "backup_spans_20260831")

# 文件名格式 表X-X（X 为一位或多位数字）
NAME_RE = re.compile(r"^表\d+-\d+")

SPAN_RE = re.compile(r"<span([^>]*)>(.*?)</span>", re.S)

KINDS = ("class", "style", "plain", "all")


def split_tid(content):
    """返回 (头部, 正文)。头部字段区不参与替换。"""
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "":
            return "\n".join(lines[:i + 1]), "\n".join(lines[i + 1:])
    return content, ""


def span_kind(attrs):
    if "style=" in attrs:
        return "style"
    if "class=" in attrs:
        return "class"
    return "plain"


def process(body, kind):
    """unwrap 指定类型的 span，返回 (新正文, 处理数量)。"""
    count = 0

    def repl(m):
        nonlocal count
        attrs, inner = m.group(1), m.group(2)
        if kind != "all" and span_kind(attrs) != kind:
            return m.group(0)
        count += 1
        return inner

    new_body = SPAN_RE.sub(repl, body)
    return new_body, count


def main():
    kind = "class"
    dry = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--kind" and i + 1 < len(args):
            kind = args[i + 1].lower()
            if kind not in KINDS:
                print(f"未知 kind: {kind}，可选: {', '.join(KINDS)}")
                return 1
        elif args[i] == "--dry":
            dry = True
        i += 1

    targets = []
    for dp, _, ns in os.walk(BASE):
        for n in sorted(ns):
            if not n.lower().endswith(".tid"):
                continue
            if NAME_RE.match(os.path.splitext(n)[0]):
                targets.append(os.path.join(dp, n))

    print(f"kind={kind}{' (预览)' if dry else ''}  候选文件 {len(targets)} 个")

    changed = 0
    total = 0
    for path in targets:
        rel_dir = os.path.relpath(os.path.dirname(path), BASE)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        head, body = split_tid(content)
        if not body:
            continue
        new_body, count = process(body, kind)
        if count == 0:
            continue

        total += count
        changed += 1
        rel = os.path.relpath(path, BASE)

        if dry:
            print(f"[DRY] {count:3d} 处  {rel}")
            continue

        # 备份（保持相对目录结构）
        bak = os.path.join(BACKUP_DIR, rel)
        os.makedirs(os.path.dirname(bak), exist_ok=True)
        if not os.path.exists(bak):
            shutil.copy2(path, bak)

        with open(path, "w", encoding="utf-8") as f:
            f.write(head + new_body)
        print(f"[OK ] {count:3d} 处  {rel}")

    tag = "(预览)" if dry else ""
    print(f"\n{tag}kind={kind}  修改文件 {changed} 个，unwrap span {total} 处")
    if not dry and changed:
        print(f"备份目录: {BACKUP_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
