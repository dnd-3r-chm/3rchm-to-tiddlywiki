#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理法术描述目录中残留的 Word/旧 HTML 标签，参考 A.tid 的简洁风格。"""
import _paths as P
import html
import os
import re
import sys
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

TARGET_DIR = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "PHB玩家手册", "11法术", "法术描述")

ALLOWED_BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}
ALLOWED_INLINE_TAGS = {"b", "strong", "i", "em", "u", "br", "a", "img"}


class WordCleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.current_block = None  # {"type": str, "parts": []}

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        if tag in ALLOWED_BLOCK_TAGS:
            self._end_block()
            self.current_block = {"type": tag, "parts": []}
        elif tag in ALLOWED_INLINE_TAGS and self.current_block is not None:
            if tag == "br":
                self.current_block["parts"].append("<br>")
            elif tag == "a":
                href = attrs.get("href", "")
                if href:
                    self.current_block["parts"].append(f'<a href="{html.escape(href, quote=True)}">')
                else:
                    self.current_block["parts"].append("<a>")
            elif tag == "img":
                src = attrs.get("src", "")
                if src:
                    self.current_block["parts"].append(f'<img src="{html.escape(src, quote=True)}">')
                else:
                    self.current_block["parts"].append("<img>")
            else:
                self.current_block["parts"].append(f"<{tag}>")
        # span/font/o:p/div 等旧标签直接忽略

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ALLOWED_BLOCK_TAGS:
            self._end_block()
        elif tag in ALLOWED_INLINE_TAGS and self.current_block is not None:
            if tag in ("a", "b", "strong", "i", "em", "u"):
                self.current_block["parts"].append(f"</{tag}>")

    def handle_data(self, data):
        if self.current_block is not None:
            self.current_block["parts"].append(data)

    def _end_block(self):
        if self.current_block is None:
            return
        raw = "".join(self.current_block["parts"])
        # 折叠空白
        text = re.sub(r"\s+", " ", raw).strip()
        if text:
            self.blocks.append(self._maybe_heading(self.current_block["type"], text))
        self.current_block = None

    def _maybe_heading(self, block_type, text):
        # 去掉内部标签后判断纯文本
        plain = re.sub(r"<[^>]+>", "", text)
        # 统一英文括号格式：中文名 (English Name)
        normalized = re.sub(r"[（(]\s*", " (", plain)
        normalized = re.sub(r"\s*[)）]", ")", normalized)

        # 把“中文名（English Name）”或“中文名 (English Name)”段落转成 h5
        if re.search(r"[\u4e00-\u9fff]", normalized):
            m = re.match(
                r"^(.+?)\s*\(\s*([A-Za-z][A-Za-z0-9 ,.'’&/\-:()]*?)\s*\)\s*$",
                normalized,
            )
            if m:
                return f"<h5>{normalized}</h5>"

        # h5 也去掉内部多余的 b/span 等
        if block_type == "h5":
            return f"<h5>{normalized}</h5>"

        return f"<{block_type}>{text}</{block_type}>"


def clean_body(body):
    parser = WordCleaner()
    parser.feed(body)
    parser.close()
    return "\n".join(parser.blocks)


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # 分离 .tid 头部和正文
    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        print("SKIP (no body):", path)
        return
    header, body = parts
    new_body = clean_body(body)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n\n" + new_body + "\n")
    print("CLEANED:", os.path.basename(path), f"({len(body)} -> {len(new_body)})")


def main():
    files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(".tid")]
    # 先处理除 A.tid 外的文件；A.tid 作为参照也处理一遍（应基本不变）
    for name in sorted(files):
        process_file(os.path.join(TARGET_DIR, name))
    print("done.")


if __name__ == "__main__":
    main()
