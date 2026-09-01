#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理 10 附录 目录下 .tid 中残余的 <span> 标签（unwrap：删标签留文本）。

处理对象（用户反馈：部分节点有残余 span 标签）：
  - <span style='FONT-FAMILY: "微软雅黑"...; COLOR: ...; mso-...'>文字</span>  Word 默认格式残留
  - <span lang=EN-US></span>  空标签
  - <span style="color: ...">...</span>  含展示样式（统一 unwrap，与既有 strip_hooks 规则一致）

规则：
  1) 删除所有 <span ...> 开始标签与 </span> 结束标签，保留内部文本/子标签。
  2) 严格保留 .tid 头部 4 行 metadata（title/tags/source/type）。
  3) 运行前备份整目录。
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
RE_SPAN_OPEN = re.compile(r"<span\b[^>]*>")
RE_SPAN_CLOSE = re.compile(r"</span\s*>")

SKIP_FILES = set()  # 暂无固定跳过


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def process(body):
    new = RE_SPAN_OPEN.sub("", body)
    new = RE_SPAN_CLOSE.sub("", new)
    return new


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_span_%s" % ts)
    files = 0
    total_spans = 0
    for dp, dn, fn in os.walk(BASE):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, BASE)
            if rel in SKIP_FILES:
                continue
            text = open(full, encoding="utf-8", errors="replace").read()
            header, body = split_tid(text)
            n_before = len(RE_SPAN_OPEN.findall(body)) + len(RE_SPAN_CLOSE.findall(body))
            if n_before == 0:
                continue
            new_body = process(body)
            new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()
            total_spans += n_before
            files += 1
            if dry:
                print("===== DRY:", rel, "(spans=%d)" % n_before, "=====")
                # 展示前若干行含 span 的片段已去除效果无法直观看，仅报告计数
                continue
            bdest = os.path.join(backup_root, rel)
            os.makedirs(os.path.dirname(bdest), exist_ok=True)
            shutil.copy2(full, bdest)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  移除 span 标签总数: %d" % (mode, files, total_spans))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
