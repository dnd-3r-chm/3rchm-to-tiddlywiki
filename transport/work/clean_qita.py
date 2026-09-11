# -*- coding: utf-8 -*-
"""`11 其他资源` 系列后处理：clean 去噪/表格紧凑化 + 单 '?' 乱码清理（仅限本系列）。

复用 clean_series.clean_body（去 Word/DND3R-FEEDBACK 噪音、表格紧凑化、全角/引号归一）
与 fix_lone_qmark 的单 ? 乱码规则（含疑问词保护），仅遍历 `11 其他资源` 目录下的 tid。

安全设计：--apply 前自动备份整个 `11 其他资源` 目录；可见字符数自检（防内容丢失）。

用法：
  python clean_qita.py            # 干跑
  python clean_qita.py --apply    # 写入（先备份）
"""
import datetime
import html
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import clean_series as cs

BOOK = os.path.join(P.WIKI_TIDDLERS, "11 其他资源")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(P.WORK, f"backup_qita_clean_{TS}")

CJK = r"\u4e00-\u9fff"
PAT_MID = re.compile(r"(?<=[" + CJK + r"])\?(?=[" + CJK + r"])")
SEG_RE = re.compile(r"<p\b[^>]*>.*?</p>|<td\b[^>]*>.*?</td>", re.S | re.I)
QW = ("吗", "呢", "什么", "为什么", "如何", "谁", "哪", "是否", "怎么")


def fix_seg(seg):
    if any(w in seg for w in QW):
        return seg  # 含疑问词：保留（真问句保护）
    seg = PAT_MID.sub("，", seg)      # 中文?中文 -> 逗号
    seg = seg.replace("?", "")         # 其余孤立 ? -> 删除
    return seg


def fix_text(s):
    return SEG_RE.sub(lambda m: fix_seg(m.group(0)), s)


def split_tid(raw):
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end():]
    return "", raw


def main():
    apply = "--apply" in sys.argv
    if apply:
        os.makedirs(BAK, exist_ok=True)
        print(f"[备份] -> {BAK}\n")

    files = []
    for root, dirs, fs in os.walk(BOOK):
        dirs[:] = [x for x in dirs if not x.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                files.append(os.path.join(root, x))

    stats = {"files": 0, "changed": 0, "tb": 0, "ta": 0}
    lost = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        header, body = split_tid(raw)
        new = cs.clean_body(body)
        new = fix_text(new)
        tb = re.sub(r"\s+", "", cs.strip_tags(html.unescape(cs.normalize(body))))
        ta = re.sub(r"\s+", "", cs.strip_tags(html.unescape(new)))
        stats["files"] += 1
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
            lost.append((os.path.relpath(path, P.WIKI_TIDDLERS), len(tb), len(ta)))
        if new != body.strip():
            stats["changed"] += 1
            if apply:
                d2 = os.path.join(BAK, os.path.relpath(path, P.WIKI_TIDDLERS))
                os.makedirs(os.path.dirname(d2), exist_ok=True)
                shutil.copy2(path, d2)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(header.rstrip("\n") + "\n\n" + new + "\n")

    print(f"文件 {stats['files']}  修改 {stats['changed']}")
    print(f"可见字符 {stats['tb']} -> {stats['ta']}")
    if lost:
        print(f"[!! 字符数异常 {len(lost)}] " + "; ".join(f"{f} {b}->{a}" for f, b, a in lost[:8]))
    if not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
