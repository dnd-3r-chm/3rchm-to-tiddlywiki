#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新排版 译者名录1.1.tid，使其格式接近 前言.tid。"""
import _paths as P
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clean_spell_tids as cst

TARGET = os.path.join(P.WIKI_TIDDLERS, "译者名录1.1.tid")


def inner_text(block):
    return re.sub(r"<[^>]+>", "", block).strip()


def is_short_heading(block):
    text = inner_text(block)
    if not text:
        return False
    # 短段落视为标题；姓名列表通常很长
    if len(text) <= 15:
        # 排除明显是普通短句的（以句号/省略号结尾）
        if text.endswith(("。", "……", "！", "？")):
            return False
        return True
    return False


def reformat_body(body):
    cleaned = cst.clean_body(body)
    blocks = []
    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue
        # 去掉分隔虚线
        if re.fullmatch(r"<p>[-—–—\s]+</p>", line):
            continue
        # h5/h6 统一改回 p
        line = re.sub(r"<h5[^>]*>(.*?)</h5>", r"<p>\1</p>", line, flags=re.S | re.I)
        line = re.sub(r"<h6[^>]*>(.*?)</h6>", r"<p>\1</p>", line, flags=re.S | re.I)
        # 短标题转 h3
        if is_short_heading(line):
            text = inner_text(line)
            # 去掉可能残留的 <b> 标签
            text = re.sub(r"<[^>]+>", "", text).strip()
            line = f"<h3>{text}</h3>"
        blocks.append(line)

    # 顶部加主标题
    return "<h1>译者名录</h1>\n\n" + "\n\n".join(blocks)


def main():
    with open(TARGET, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        print("no body")
        return
    header, body = parts
    new_body = reformat_body(body)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(header + "\n\n" + new_body + "\n")
    print("reformatted.")


if __name__ == "__main__":
    main()
