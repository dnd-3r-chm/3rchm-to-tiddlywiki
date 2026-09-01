#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse CHM Contents.hhc into a flat mapping table (CSV)."""
import csv
import html
import os
import sys
import urllib.parse
from html.parser import HTMLParser

HHC_PATH = r"E:\dnd3r_full\Contents.hhc"
OUT_CSV = r"E:\dnd3r_full\transport\work\hhc_mapping.csv"


class HHCParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = []          # list of top-level nodes
        self.stack = []         # stack of child lists
        self.cur_node = None    # most recently opened <li> node

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        if tag == "ul":
            if not self.stack:
                self.stack.append(self.root)
            else:
                children = []
                if self.stack[-1]:
                    parent = self.stack[-1][-1]
                    parent["children"] = children
                self.stack.append(children)
        elif tag == "li":
            node = {
                "name": "",
                "local": "",
                "children": [],
            }
            self.stack[-1].append(node)
            self.cur_node = node
        elif tag == "param":
            name = attrs.get("name", "")
            value = attrs.get("value", "")
            if self.cur_node is not None:
                if name == "Name":
                    self.cur_node["name"] = html.unescape(value)
                elif name == "Local":
                    self.cur_node["local"] = html.unescape(value)

    def handle_endtag(self, tag):
        if tag.lower() == "ul" and self.stack:
            self.stack.pop()


def iter_nodes(nodes, ancestors):
    for node in nodes:
        path = ancestors + [node["name"]] if node["name"] else ancestors
        yield node, path
        yield from iter_nodes(node.get("children", []), path)


def main():
    with open(HHC_PATH, "rb") as f:
        raw = f.read()
    # CHM 中文目录通常为 GBK/GB2312；用 gb18030 兼容解析
    try:
        text = raw.decode("gb18030")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")

    parser = HHCParser()
    parser.feed(text)

    rows = []
    for node, path in iter_nodes(parser.root, []):
        local_raw = node.get("local", "") or ""
        local = urllib.parse.unquote(local_raw)
        local = local.replace("/", "\\")
        depth = len(path)
        rows.append({
            "标题": node["name"],
            "源文件相对路径": local,
            "层级": depth,
            "祖先路径": " / ".join(path[:-1]),
            "一级": path[0] if len(path) > 0 else "",
            "二级": path[1] if len(path) > 1 else "",
        })

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["标题", "源文件相对路径", "层级", "祖先路径", "一级", "二级"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"nodes: {len(rows)}")
    print(f"with local: {sum(1 for r in rows if r['源文件相对路径'])}")
    print(f"output: {OUT_CSV}")


if __name__ == "__main__":
    main()
