# -*- coding: utf-8 -*-
"""将 1 核心补充书籍 下所有节点中，<p> 段落内部的 <br> 标签
转换为段落分隔（</p>\n\n<p>），与全库正文 <p> 风格一致。
  - 仅处理 <p>...</p> 块内的 <br>（覆盖正文绝大多数场景）
  - 表格单元格内（<td>...</td>）的 <br> 保留不动（避免破坏紧凑表格）
  - 边界安全：删除因转换产生的空 <p></p>
用法：python _br_to_p.py            # 干跑
      python _br_to_p.py --apply    # 写入（自动备份）
"""
import datetime
import os
import re
import shutil
import sys

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
BR_RE = re.compile(r"<br\s*/?>", re.I)
P_BLOCK_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
EMPTY_P_RE = re.compile(r"<p>\s*</p>", re.I)


def transform_block(block):
    if not BR_RE.search(block):
        return block, 0
    # 块内 br -> 段落分隔
    new = BR_RE.sub("</p>\n\n<p>", block)
    # 删除空段落
    new = EMPTY_P_RE.sub("", new)
    n = len(BR_RE.findall(block))
    return new, n


def main():
    apply = "--apply" in sys.argv
    total_files = 0
    total_br = 0
    changed_files = []
    for dp, _, ns in os.walk(BASE):
        for nm in sorted(ns):
            if not nm.lower().endswith(".tid"):
                continue
            p = os.path.join(dp, nm)
            t = open(p, encoding="utf-8").read()
            # 仅取 <p> 块
            blocks = list(P_BLOCK_RE.finditer(t))
            if not blocks:
                continue
            new = t
            fcnt = 0
            for m in blocks:
                repl, n = transform_block(m.group(0))
                if n:
                    fcnt += n
                    new = new.replace(m.group(0), repl, 1)
            if fcnt:
                total_files += 1
                total_br += fcnt
                changed_files.append((os.path.relpath(p, BASE), fcnt))
                if apply:
                    pass
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(BASE, f"_bak_br2p_{ts}")
        os.makedirs(bak, exist_ok=True)
        for rel, _ in changed_files:
            src = os.path.join(BASE, rel)
            d2 = os.path.dirname(os.path.join(bak, rel))
            os.makedirs(d2, exist_ok=True)
            shutil.copy2(src, os.path.join(bak, rel))
        # 真正写回
        for rel, fcnt in changed_files:
            src = os.path.join(BASE, rel)
            t = open(src, encoding="utf-8").read()
            new = t
            for m in P_BLOCK_RE.finditer(t):
                repl, n = transform_block(m.group(0))
                if n:
                    new = new.replace(m.group(0), repl, 1)
            open(src, "w", encoding="utf-8").write(new)
        print(f"已写入 {total_files} 个文件，转换 {total_br} 处 <br>。备份 -> {bak}")
    else:
        print(f"[干跑] 将修改 {total_files} 个文件，转换 {total_br} 处 <br>（仅 <p> 段落内）")
        for rel, c in changed_files[:10]:
            print("  ", rel, c)
        if len(changed_files) > 10:
            print(f"  ... 共 {len(changed_files)} 个文件")


if __name__ == "__main__":
    main()
