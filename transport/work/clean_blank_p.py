#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理 10 附录 目录下 .tid 中「纯空白」的 <p> 标签，保留含 &nbsp; 的。

目标（用户要求）：
  - 删除 <p></p>、<p>   </p>、<p>\n</p> 等仅含空白字符的空段落
  - 保留 <p>&nbsp;</p>、<p class="x">&nbsp;</p> 等含 &nbsp; 的（作为占位间距）

实现：
  - 用 <p[^>]*>\\s*</p> 匹配：内部仅空白(\\s 含空格/Tab/换行)的 p 段落。
    &nbsp; 不是 \\s，故 <p>&nbsp;</p> 不会被匹配，得以保留。
  - 同时复用 clean_p_inner 的折叠，避免删后留下多余空行。
  - 严格保留 .tid 头部 4 行 metadata（title/tags/source/type）。
范围：d:/.../wiki/tiddlers/10 附录（含子目录）
支持 --dry 预览。
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

BASE = os.path.join(P.WIKI_TIDDLERS, "10 附录")

# 仅含空白的 p（含任意属性），不含 &nbsp; / 文字
RE_BLANK_P = re.compile(r"<p[^>]*>\s*</p>", re.DOTALL)
# 兜底：<p ...> 标签属性内换行（来自 clean_p_tags）
RE_NL = re.compile(r"<p\s*\n")
RE_ATTR = re.compile(r"<p([^>]+?)\s+>")
RE_PURE = re.compile(r"<p\s+>")


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def process(body):
    body = RE_NL.sub("<p ", body)
    body = RE_ATTR.sub(r"<p\1>", body)
    body = RE_PURE.sub("<p>", body)
    body = RE_BLANK_P.sub("", body)
    return body


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_blankp_%s" % ts)
    files = 0
    total = 0
    for dp, dn, fn in os.walk(BASE):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, BASE)
            text = open(full, encoding="utf-8", errors="replace").read()
            header, body = split_tid(text)
            n = len(RE_BLANK_P.findall(body))
            if n == 0:
                continue
            new_body = process(body)
            new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()
            total += n
            files += 1
            if dry:
                print("===== DRY:", rel, "(blank p=%d)" % n, "=====")
                continue
            bdest = os.path.join(backup_root, rel)
            os.makedirs(os.path.dirname(bdest), exist_ok=True)
            shutil.copy2(full, bdest)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  移除空白 <p> 标签总数: %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
