# -*- coding: utf-8 -*-
"""搬运 HBG英雄构筑指南（HTML 源，干净页面，非 CHM，不在 final_mapping.csv）。

复用 convert_pilot 的核心清洗管线（extract_body / clean_html / rewrite_images
/ normalize_fullwidth_punct 等），自行推导 title/tags，平铺到：
    transport/wiki/tiddlers/1 核心补充书籍/HBG英雄构筑指南/

约定（与全库一致）：
  title : 文件名 (HBG-英雄构筑指南)        例：人类 (HBG-英雄构筑指南)
  tags  : [[1 核心补充书籍]] [[HBG英雄构筑指南]]
  source: 1 核心补充书籍/HBG英雄构筑指南/文件名.html

说明：
  - HBG 源是平铺的 34 个 html，无 hhc 章节映射，故不猜测章节子目录，直接平铺。
  - 源页面干净（<p>/<h3> 结构良好，无 <br>、无表格噪音），clean_html 处理后
    即符合本会话对 1 核心补充书籍/ 的规范（全角转半角、feedback 区块删除等）。
  - 无互链 <a href> 指向其他节点，rewrite_links 以空 mapping 安全跳过。

用法：
  python convert_hbg.py            # 干跑预览
  python convert_hbg.py --apply    # 写入（自动备份已有 tid）
"""
import datetime
import os
import re
import shutil
import sys

import convert_pilot as cp
from _paths import ROOT, WIKI_TIDDLERS

SRC_DIR = os.path.join(ROOT, "1 核心补充书籍", "HBG英雄构筑指南")
OUT_DIR = os.path.join(WIKI_TIDDLERS, "1 核心补充书籍", "HBG英雄构筑指南")
BOOK = "HBG英雄构筑指南"
BOOK_SHORT = "HBG"
BOOK_FULL = "英雄构筑指南"
TAGS = "[[1 核心补充书籍]] [[HBG英雄构筑指南]]"
IMG_DIR = SRC_DIR  # 源图片与 html 同目录（封面.jpeg）
IMG_BASE_REL = "1 核心补充书籍/HBG英雄构筑指南"  # 用于 copy_image 的相对基


def derive_title(fname):
    name = os.path.splitext(fname)[0]
    return f"{name} ({BOOK_SHORT}-{BOOK_FULL})"


def convert_one(fname):
    src_path = os.path.join(SRC_DIR, fname)
    text = cp.read_text(src_path)
    body = cp.extract_body(text)
    body = cp.clean_html(body, BOOK)
    # 图片：base_rel_dir 让 copy_image 将 封面.jpeg 复制到 wiki 同目录
    body = cp.rewrite_images(body, IMG_BASE_REL)
    # HBG 无互链 mapping，跳过 rewrite_links（空映射无害）
    title = derive_title(fname)
    source = (IMG_BASE_REL + "/" + fname).replace("\\", "/")
    tid = (
        f"title: {title}\n"
        f"tags: {TAGS}\n"
        f"source: {source}\n"
        f"type: text/vnd.tiddlywiki\n"
        f"\n"
        f"{body}\n"
    )
    return title, tid


def main():
    apply = "--apply" in sys.argv
    htmls = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".html"))
    print(f"发现 HBG 源文件 {len(htmls)} 个")
    total = len(htmls)
    ok = 0
    for fname in htmls:
        title, tid = convert_one(fname)
        out_path = os.path.join(OUT_DIR, os.path.splitext(fname)[0] + ".tid")
        if apply:
            # 仅在「已存在且非空」且「内容与新生成结果有实质差异」时才备份
            # （2026-09-02 用户要求：避免无条件备份堆积无价值的 .bak_* 临时文件）
            if os.path.exists(out_path):
                with open(out_path, encoding="utf-8", errors="replace") as f:
                    old = f.read()
                if old.strip() and old.strip() != tid.strip():
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy2(out_path, out_path + f".bak_{ts}")
                    print(f"  [备份] {os.path.basename(out_path)}（内容有差异）")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(tid)
            ok += 1
            print(f"[OK ] {title}")
        else:
            print(f"[DRY] {title}")
    if apply:
        print(f"\n已写入 {ok}/{total} 个 tid 到 {OUT_DIR}")
    else:
        print(f"\n（干跑，未写入。共 {total} 个待转换，加 --apply 执行）")


if __name__ == "__main__":
    main()
