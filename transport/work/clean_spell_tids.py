#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新排版「法术描述」目录下各单字母节点，使其风格与 A.tid 一致。

主要清理项：
1) 剥离 Word/CHM 残留标签：style/class/span/font/o:p/div 等
2) 将「中文名(English Name)」段落规整为 <h5> 标题（半角括号、中文后加空格）
3) 字段行（等级、法术成分、施法时间…）规整为 <p><b>字段：</b>值</p>
4) 学派行统一为半角括号/方括号
5) 折叠多余空白与换行

安全约定：严格保留 .tid 头部 4 行 metadata（title/tags/source/type）与空行，
只对正文 body 做清洗，绝不动头部。
"""
import _paths as P
import html
import os
import re
import sys
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

TARGET_DIR = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "PHB玩家手册", "11法术", "法术描述")

# 已干净的参照节点不重排，以免破坏手工/既有成果
SKIP_FILES = {"A.tid", "法术描述.tid"}

ALLOWED_BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li"}
ALLOWED_INLINE_TAGS = {"b", "strong", "i", "em", "u", "br", "a", "img"}

# 法术字段白名单（用于把 <b>字段</b>：值 -> <b>字段：</b>值）
FIELD_RE = re.compile(r"(<b>[^<]+?</b>)\s*[:：]")


def split_tid(content):
    """分离 .tid 头部(metadata)与正文。头部为开头到第一个空行(含)为止。"""
    # 头部固定为：title / tags / source / type 四行，其后一个空行
    m = re.match(
        r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)",
        content,
        re.DOTALL,
    )
    if m:
        header = m.group(1)
        body = content[m.end():]
        return header, body
    # 退化：按首个空行切
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


class WordCleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.current_block = None  # {"type": str, "parts": []}
        self.in_list = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        if tag in ("ul", "ol"):
            self._end_block()
            self.in_list = True
            return
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
        if tag in ("ul", "ol"):
            self._end_block()
            self.in_list = False
            return
        if tag in ALLOWED_BLOCK_TAGS:
            self._end_block()
        elif tag in ALLOWED_INLINE_TAGS and self.current_block is not None:
            if tag in ("a", "b", "strong", "i", "em", "u"):
                self.current_block["parts"].append(f"</{tag}>")

    def handle_data(self, data):
        if self.current_block is not None:
            self.current_block["parts"].append(data)
        elif data and not data.isspace():
            # 列表/块之间的游离文本（极少见），单独成块
            self.blocks.append(data.strip())

    def _end_block(self):
        if self.current_block is None:
            return
        raw = "".join(self.current_block["parts"])
        text = re.sub(r"\s+", " ", raw).strip()
        if text:
            self.blocks.append(self._maybe_heading(self.current_block["type"], text))
        self.current_block = None

    def _maybe_heading(self, block_type, text):
        plain = re.sub(r"<[^>]+>", "", text)
        # 括号统一：全角 -> 半角，并在中文与 ( 之间补一个空格
        normalized = plain.replace("（", "(").replace("）", ")")
        normalized = re.sub(r"([\u4e00-\u9fff])\s*\(", r"\1 (", normalized)
        normalized = re.sub(r"\)\s*([\u4e00-\u9fff])", r")\1", normalized)
        normalized = normalized.replace("〔", "[").replace("〕", "]")

        if re.search(r"[\u4e00-\u9fff]", normalized):
            m = re.match(
                r"^(.+?)\s*\(\s*([A-Za-z][A-Za-z0-9 ,.'’&/\-:()]*?)\s*\)\s*$",
                normalized,
            )
            if m:
                return f"<h5>{normalized}</h5>"

        if block_type == "h5":
            return f"<h5>{normalized}</h5>"
        return f"<{block_type}>{text}</{block_type}>"


def post_process(blocks):
    """对解析出的块串做整体规整：字段加粗、括号统一、合并相邻斜体/加粗、包裹 ul。"""
    text = "\n".join(blocks)
    # 字段加粗：<b>字段</b>：值 -> <b>字段：</b>值
    text = FIELD_RE.sub(lambda m: m.group(1).replace("</b>", "：</b>"), text)
    # 全角括号/书名号统一为半角
    text = text.replace("〔", "[").replace("〕", "]")
    text = text.replace("（", "(").replace("）", ")")
    # 中文与 ( 之间补一个空格
    text = re.sub(r"([\u4e00-\u9fff])\s*\(", r"\1 (", text)
    # 合并相邻的斜体/加粗边界（最终清洗阶段，统一合并更干净）
    text = re.sub(r"</i><i>", "", text)
    text = re.sub(r"</b><b>", "", text)
    # 把连续的 <li> 包裹进 <ul>…</ul>
    text = re.sub(r"(<li>.*?</li>)(?=\n<li>)", lambda m: "<ul>\n" + m.group(1), text)
    text = re.sub(r"\n(<li>.*?</li>)\n", r"\n<ul>\n\1\n</ul>\n", text)
    # 清理可能的多余空行
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def clean_body(body):
    parser = WordCleaner()
    parser.feed(body)
    parser.close()
    return post_process(parser.blocks)


def process_file(path, dry=False):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    header, body = split_tid(content)
    new_body = clean_body(body)
    new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()
    if dry:
        print("===== DRY:", os.path.basename(path), "=====")
        print(new_body[:4000])
        print("..... (truncated)" if len(new_body) > 4000 else "")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + new_body + "\n")
    if not header.startswith("title:"):
        print("!!! HEADER WARN:", os.path.basename(path))
    print("CLEANED:", os.path.basename(path), f"({len(body)} -> {len(new_body)})")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--dry":
        name = args[1] if len(args) > 1 else None
        if name:
            process_file(os.path.join(TARGET_DIR, name), dry=True)
        else:
            print("用法: python clean_spell_tids.py --dry <文件名.tid>")
        return

    files = sorted(f for f in os.listdir(TARGET_DIR) if f.lower().endswith(".tid"))
    for name in files:
        if name in SKIP_FILES:
            print("SKIP(ref):", name)
            continue
        process_file(os.path.join(TARGET_DIR, name))
    print("done.")


if __name__ == "__main__":
    main()
