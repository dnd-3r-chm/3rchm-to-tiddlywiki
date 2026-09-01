#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理 10 附录 目录下 .tid 中 <p> 标签「内容内部」的换行与多余空白。

目标形态（用户反馈：部分 p 标签内有换行）：
    <p>第一行文字
    第二行文字</p>
折叠为：
    <p>第一行文字 第二行文字</p>

规则：
  1) 仅折叠 <p ...> 与 </p> 之间的文本换行，标签属性(style/class/id)与子标签(<b>/<i>/<br>等)原样保留。
  2) <br> 标签保留（它自身提供换行），其周围的换行折叠为空格。
  3) 若某 <p> 内部含 <pre / <code 代码块，则该 p 跳过不折叠（保护代码展示）。
  4) 附带复用 clean_p_tags 的「标签属性内换行」清理（<p \n>、<p class="x" \n> 等）做兜底。
  5) 严格保留 .tid 头部 4 行 metadata（title/tags/source/type）。

范围：d:/.../wiki/tiddlers/10 附录 （含子目录）
支持 --dry 预览。
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

BASE = os.path.join(P.WIKI_TIDDLERS, "10 附录")

# 标签属性内换行（兜底）
RE_NL = re.compile(r"<p\s*\n")
RE_ATTR = re.compile(r"<p([^>]+?)\s+>")
RE_PURE = re.compile(r"<p\s+>")

# <p ...>内部换行折叠
RE_P = re.compile(r"<p(?P<attr>[^>]*)>(?P<inner>[\s\S]*?)</p>")


def fold_inner(m):
    attr = m.group("attr")
    inner = m.group("inner")
    if "<pre" in inner or "<code" in inner:
        return m.group(0)  # 代码块不折叠
    # 换行 -> 空格，连续空白压缩为单空格
    inner = inner.replace("\n", " ")
    inner = re.sub(r"[ \t]+", " ", inner)
    inner = inner.strip()
    return f"<p{attr}>{inner}</p>"


def process(text):
    text = RE_NL.sub("<p ", text)
    text = RE_ATTR.sub(r"<p\1>", text)
    text = RE_PURE.sub("<p>", text)
    text = RE_P.sub(fold_inner, text)
    return text


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_pinner_%s" % ts)
    files = 0
    total = 0
    for dp, dn, fn in os.walk(BASE):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, BASE)
            try:
                text = open(full, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            header, body = split_tid(text)
            new_body = process(body)
            new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()
            if new_body == body.strip():
                continue
            files += 1
            total += 1
            if dry:
                print("===== DRY:", rel, "=====")
                # 打印变更区域：找含换行的 p 折叠前后
                print("(changed body length %d -> %d)" % (len(body), len(new_body)))
                continue
            bdest = os.path.join(backup_root, rel)
            os.makedirs(os.path.dirname(bdest), exist_ok=True)
            shutil.copy2(full, bdest)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  总节点: %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
