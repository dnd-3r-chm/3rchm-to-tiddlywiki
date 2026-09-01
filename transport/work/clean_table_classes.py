# -*- coding: utf-8 -*-
"""清理 .tid 正文中的表格行内格式 class="g" / "l" / "w"。

背景
----
CHM 源表格页自带内联 <style>，定义了：
    .l{font-weight:600;background:#f0f0f0;text-align:center}   # 首列标签
    .g td{background:#f7f7f7}                                  # 斑马纹奇数行
    .w td{background:#fff}                                     # 斑马纹偶数行
    .w{max-width:1100px;background:#fff;...}                   # 表格外层容器

转换管道 clean_html() 会剥离 <style>，而全局 cascading_stylesheet.css 未定义
这些类，因此它们在 wiki 中已是**死属性**：删除后渲染结果不变，纯属清理。

用法
----
    python clean_table_classes.py                 # 全库（默认）
    python clean_table_classes.py --scope dmg     # 仅 DMG城主指南
    python clean_table_classes.py --scope mm      # 仅 MM怪物图鉴
    python clean_table_classes.py --dry           # 只预览不写入

注意：命令行参数请用上面的 ASCII 代号，**不要传中文**
（PowerShell 会破坏命令行中的中文字符）。
"""
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = P.WIKI_TIDDLERS

# 要清理的 class 值（精确匹配单个 class 值，不影响 noindent/page 等其他类）
TARGETS = {"g", "l", "w"}

# ASCII 代号 -> 中文子路径，避免命令行传中文
SCOPES = {
    "all": None,
    "dmg": os.path.join("0 核心三宝书", "DMG城主指南"),
    "mm": os.path.join("0 核心三宝书", "MM怪物图鉴"),
}

# 匹配 class="..." 或 class='...'，连同前导空白一起捕获
CLASS_ATTR = re.compile(r"""[ \t]+class[ \t]*=[ \t]*(["'])(.*?)\1""", re.I)

# 跳过目录/导航类 Tiddler 与系统文件
SKIP_NAMES = {"总目录.tid", "CHM目录侧边栏.tid"}


def split_tid(content):
    """返回 (头部, 正文)。头部字段区不参与替换。"""
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "":
            return "\n".join(lines[:i + 1]), "\n".join(lines[i + 1:])
    return content, ""


def strip_classes(body):
    """移除正文中的 g / l / w 类；若某元素仅剩这些类则整个 class 属性删除。"""

    def repl(m):
        quote = m.group(1)
        vals = m.group(2).split()
        kept = [v for v in vals if v.lower() not in TARGETS]
        if not kept:
            return ""  # 连同前导空白一并删除，避免出现多余空格
        return f' class={quote}{" ".join(kept)}{quote}'

    new_body, n = CLASS_ATTR.subn(repl, body)
    # 统计实际被移除的 class 个数（按值计）
    removed = 0
    for m in CLASS_ATTR.finditer(body):
        removed += sum(1 for v in m.group(2).split() if v.lower() in TARGETS)
    return new_body, removed


def main():
    scope = "all"
    dry = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1].lower()
        elif args[i] == "--dry":
            dry = True
        i += 1

    if scope not in SCOPES:
        print(f"未知 scope: {scope}，可选: {', '.join(SCOPES)}")
        return 1

    sub = SCOPES[scope]
    base = os.path.join(WIKI, sub) if sub else WIKI
    if not os.path.isdir(base):
        print("目录不存在:", base)
        return 1

    changed_files = 0
    total_removed = 0

    for dp, _, ns in os.walk(base):
        for n in sorted(ns):
            if not n.lower().endswith(".tid") or n.startswith("$__"):
                continue
            if n in SKIP_NAMES:
                continue
            path = os.path.join(dp, n)
            rel = os.path.relpath(path, WIKI)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            head, body = split_tid(content)
            if not body:
                continue
            new_body, removed = strip_classes(body)
            if removed == 0:
                continue

            total_removed += removed
            changed_files += 1
            if dry:
                print(f"[DRY] {removed:3d} 处  {rel}")
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(head + new_body)
            print(f"[OK ] {removed:3d} 处  {rel}")

    tag = "(预览)" if dry else ""
    print(f"\n{tag}scope={scope}  修改文件 {changed_files} 个，移除 class {total_removed} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
