#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将指定节点内的 <br> 替换为「独立的 <p> 段落」（用户要求：魔宠手册.tid 不要使用 <br>，改用独立 p）。

策略：
  1) 合并连续 <br>（含其间的空白）为单个 <br>，避免后续产生空 <p>。
  2) 单个 <br> -> </p>\n<p>，把同一 <p> 内的多行内容拆成多个独立段落。
  3) 删除因 <br> 出现在段首/段尾而产生的空白 <p></p>（保留 <p>&nbsp;</p> 占位）。
  4) 折叠多余空行。
严格保留 .tid 头部 4 行 metadata。运行前备份该文件。

用法：python clean_nobr_p.py [--dry] [相对 10附录 的文件名，默认 职业心得/魔宠手册.tid]
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

BASE = os.path.join(P.WIKI_TIDDLERS, "10 附录")
DEFAULT = os.path.join("职业心得", "魔宠手册.tid")

RE_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
RE_BRSEQ = re.compile(r"(?:<br\s*/?>\s*)+")          # 连续 br（含空白）
RE_SPLIT = "</p>\n<p>"
RE_BLANK_P = re.compile(r"<p[^>]*>\s*</p>")           # 纯空白 p（不含 &nbsp;）


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def process(body):
    body = RE_BRSEQ.sub("<br>", body)        # 连续 br -> 单 br
    body = RE_BR.sub(RE_SPLIT, body)         # 单 br -> 段落分隔
    body = RE_BLANK_P.sub("", body)          # 删空 p（段首/段尾 br 产生）
    body = re.sub(r"\n{3,}", "\n\n", body)  # 折叠多余空行
    return body


def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    rel = args[0] if args else DEFAULT
    full = os.path.join(BASE, rel)

    text = open(full, encoding="utf-8", errors="replace").read()
    header, body = split_tid(text)
    n_br = len(RE_BR.findall(body))
    if n_br == 0:
        print("无 <br>，无需处理:", rel)
        return
    new_body = process(body)
    new_body = new_body.strip()

    if dry:
        print("===== DRY:", rel, "(br=%d)" % n_br, "=====")
        print(new_body[:900])
        print("......(truncated)")
        return

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(P.WORK, "backup_nobr_p_%s" % ts)
    os.makedirs(backup, exist_ok=True)
    shutil.copy2(full, os.path.join(backup, os.path.basename(full)))
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(header + new_body + "\n")
    n_br_after = len(RE_BR.findall(new_body))
    print("CLEANED:", rel, "原 <br> 数:", n_br, " 现 <br> 数:", n_br_after, " 备份:", backup)


if __name__ == "__main__":
    main()
