# -*- coding: utf-8 -*-
"""还原单个 tid 中的非 ASCII 数字实体（&#x4E16; / &#19990;）为真实字符。

根因：部分源 HTML（WinCHM 导出）body 本身就把中文写成了十六进制数字实体，
转换管线未 unescape，实体被原样写入 .tid。

安全边界（contexts.md §5.5）：只解 codepoint > 127 的实体（中文/全角标点/
破折号/省略号等）；ASCII 实体 &amp; &lt; &gt; &quot; &#39; 一律原样保留，
避免二次编码或破坏 HTML 结构。

用法：
    python _fix_entities_one.py          # 干跑，只打印统计
    python _fix_entities_one.py --apply  # 实际写回（先备份到 work/backup 下）
"""
import os
import re
import shutil
import sys

# 目标文件：只用这一个节点（用户指定），路径写成常量以规避 PowerShell 中文传参乱码
TARGET = os.path.join(
    "d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers",
    "9 世设", "艾伯伦", "ECS艾伯伦战役设定集",
    "7第七章 世界众生貌", "世界历史", "世界历史.tid",
)
BACKUP_DIR = "d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/work/backup_fix_entity_20260910"

ENT = re.compile(r"&#(?:x([0-9A-Fa-f]+)|(\d+));")


def _code(m):
    return int(m.group(1), 16) if m.group(1) else int(m.group(2))


def repl(m):
    code = _code(m)
    # 只还原非 ASCII；ASCII 实体保持原样，防止把 &amp; &lt; &gt; 解成裸字符
    return chr(code) if code > 127 else m.group(0)


def main():
    apply = "--apply" in sys.argv
    with open(TARGET, encoding="utf-8") as f:
        src = f.read()

    new = ENT.sub(repl, src)
    n_sub = sum(1 for m in ENT.finditer(src) if _code(m) > 127)
    leftover = sum(1 for m in ENT.finditer(new) if _code(m) > 127)

    print("文件:", TARGET)
    print("待还原的非 ASCII 实体:", n_sub)
    print("还原后剩余非 ASCII 实体:", leftover)
    print("可见字符数: %d -> %d" % (len(src), len(new)))

    if not apply:
        print("\n[干跑] 未写回。确认无误后加 --apply。")
        return

    if n_sub == 0:
        print("\n无可还原实体，跳过写回。")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    bak = os.path.join(BACKUP_DIR, "世界历史.tid.bak")
    shutil.copy2(TARGET, bak)
    print("\n已备份:", bak)

    with open(TARGET, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print("已写回:", TARGET)


if __name__ == "__main__":
    main()
