#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理书籍 Tiddler 中不需要的 <div class="page"> 和 class="title" 行内格式。

用法：
    python clean_dmg_classes.py [目标目录]
目标目录缺省为 DMG城主指南；可传入其他书籍目录，如 MM怪物图鉴。
"""
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_DIR = P.DMG_TIDDLERS
TARGET_DIR = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR


def remove_page_div(text):
    """移除最外层 <div class="page"> 的开始和结束标签，保留内部内容。"""
    m = re.search(r'<div\s+class="page"[^>]*>', text, re.I)
    if not m:
        return text, 0
    start = m.start()
    inner_start = m.end()
    depth = 1
    # 从 open_tag 后面开始扫描 div 标签
    tag_re = re.compile(r"<(/?)div\b[^>]*>", re.I)
    for tm in tag_re.finditer(text, inner_start):
        if tm.group(1) == "/":
            depth -= 1
            if depth == 0:
                inner_end = tm.start()
                end = tm.end()
                return text[:start] + text[inner_start:inner_end] + text[end:], 1
        else:
            depth += 1
    # 没有匹配的闭合 </div> 时，至少移除开标签
    return text[:start] + text[inner_start:], 1


def clean_title_formatting(text):
    # 删除空的 title-square span
    text = re.sub(r'<span\s+class="title-square"\s*>\s*</span>', "", text, flags=re.I)
    text = re.sub(r"<span\s+class='title-square'\s*>\s*</span>", "", text, flags=re.I)
    # 删除不需要的 class 属性
    for cls in ("title", "subtitle", "num-list", "abb-table"):
        text = re.sub(rf'\s+class="{cls}"', "", text, flags=re.I)
        text = re.sub(rf"\s+class='{cls}'", "", text, flags=re.I)
    return text


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content, removed = remove_page_div(content)
    new_content = clean_title_formatting(new_content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("CLEANED:", os.path.relpath(path, TARGET_DIR), f"(removed page div: {removed})")
    else:
        print("NOCHANGE:", os.path.relpath(path, TARGET_DIR))


def main():
    files = []
    for dirpath, _, names in os.walk(TARGET_DIR):
        for name in names:
            if name.lower().endswith(".tid"):
                files.append(os.path.join(dirpath, name))
    print("total tids:", len(files))
    for path in sorted(files):
        process_file(path)
    print("done.")


if __name__ == "__main__":
    main()
