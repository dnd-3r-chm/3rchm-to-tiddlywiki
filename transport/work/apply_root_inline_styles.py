#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根节点内联样式处理：h1-h6 字色改由全局「标题配色」规则（gen_styles.py）控制，
本脚本只负责 table/td 的布局内联样式，并在处理时剥离 h1-h6 上残留的 color 声明。"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FILES = [
    r"E:\dnd3r_full\transport\wiki\tiddlers\前言.tid",
    r"E:\dnd3r_full\transport\wiki\tiddlers\如何使用大不全.tid",
    r"E:\dnd3r_full\transport\wiki\tiddlers\译者名录.tid",
]

# 只保留布局样式；字色（h1/h2 DarkSlateGray、h3-h6 teal）已移入 gen_styles.py 的全局规则
STYLES = {
    "table": "width:100%;border-color:transparent",
    "td": "width:16.67%;border-color:transparent",
}

COLOR_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]  # 需要剥离 color 声明的标签


def strip_color_from_style(style):
    """移除 style 中的 color 声明，保留其余声明。"""
    decls = []
    for part in style.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            prop = part.split(":", 1)[0].strip().lower()
            if prop == "color":
                continue
        decls.append(part)
    return "; ".join(decls)


def strip_tag_colors(body, tags):
    """剥离指定标签 style 属性中的 color 声明；style 变空则删除整个属性。"""
    for tag in tags:
        pattern = re.compile(rf"<{tag}\b[^>]*>", re.I)

        def repl(m):
            tag_str = m.group(0)
            m2 = re.search(r"style\s*=\s*([\"'])(.*?)\1", tag_str, re.I | re.S)
            if not m2:
                return tag_str
            quote = m2.group(1)
            new_style = strip_color_from_style(m2.group(2))
            if not new_style:
                return tag_str[:m2.start()] + tag_str[m2.end():]
            return tag_str[:m2.start()] + f"style={quote}{new_style}{quote}" + tag_str[m2.end():]

        body = pattern.sub(repl, body)
    return body


def merge_style(old, new):
    decls = {}
    for part in old.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            prop, val = part.split(":", 1)
            decls[prop.strip().lower()] = val.strip()
    for part in new.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            prop, val = part.split(":", 1)
            decls[prop.strip().lower()] = val.strip()
    return "; ".join(f"{k}: {v}" for k, v in decls.items())


def add_style_to_tag(tag, style):
    # 处理双引号或单引号的 style 属性
    m = re.search(r"style\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
    if m:
        quote = m.group(1)
        old = m.group(2)
        new = merge_style(old, style)
        return tag[:m.start()] + f'style={quote}{new}{quote}' + tag[m.end():]
    # 没有 style 属性时，在 > 前插入
    if tag.endswith("/>"):
        return tag[:-2] + f' style="{style}" />'
    return tag[:-1] + f' style="{style}"' + tag[-1]


def process_body(body):
    # 1. 移除我们之前添加的 <style> 块
    body = re.sub(r"<style>.*?</style>", "", body, flags=re.S | re.I)
    # 2. 剥离 h1-h6 上残留的 color 声明（字色由全局「标题配色」规则控制）
    body = strip_tag_colors(body, COLOR_TAGS)
    # 3. 给 table/td 添加布局内联样式
    for tag_name, style in STYLES.items():
        pattern = re.compile(rf"<{tag_name}\b[^>]*>", re.I)
        body = pattern.sub(lambda m: add_style_to_tag(m.group(0), style), body)
    return body


def main():
    for path in FILES:
        if not os.path.exists(path):
            print("MISSING:", path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("\n\n", 1)
        if len(parts) != 2:
            print("SKIP:", path)
            continue
        header, body = parts
        new_body = process_body(body)
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + "\n\n" + new_body + "\n")
        print("PROCESSED:", path)


if __name__ == "__main__":
    main()
