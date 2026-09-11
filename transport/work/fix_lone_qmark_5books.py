# -*- coding: utf-8 -*-
"""修复 5 环境和社会 5 本书中单个 '?' 乱码（源混编码致中文标点/英文撇号/表格前导标记解码失败）。

仅限这 5 本书（本次新搬运、已确认为乱码）。不碰其他书——PHB/MM5/PHB2 等书中的
'?' 多为真问句，误改会破坏内容。

规则（片段级，逐 <p>/<td> 片段处理）：
  * 片段含疑问词（吗/呢/什么/为什么/如何/谁/哪/是否/怎么）-> 整段保留（真问句保护）
  * 否则：
      - 句中 '?'（前后均为中文）-> '，'（并列/译名分隔）
      - 其余孤立 '?'（表格前导 ?<tag>、独立 ? 段落、? 后非中文）-> 删除

默认干跑，--apply 写入并备份到 backups/。
"""
import datetime
import os
import re
import shutil
import sys

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
BOOKS = ["City城市风貌", "Dungeon地城风光", "Frost霜燃之书", "Sand沙暴之书", "Storm风暴之书"]
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_loneqmark_5books_" + TS)

CJK = r"\u4e00-\u9fff"
PAT_MID = re.compile(r"(?<=[" + CJK + r"])\?(?=[" + CJK + r"])")
SEG_RE = re.compile(r"<p\b[^>]*>.*?</p>|<td\b[^>]*>.*?</td>", re.S | re.I)
QUESTION_WORDS = ("吗", "呢", "什么", "为什么", "如何", "谁", "哪", "是否", "怎么")


def fix_seg(seg):
    if any(w in seg for w in QUESTION_WORDS):
        return seg  # 含疑问词：保留（真问句保护）
    seg = PAT_MID.sub("，", seg)   # 中文?中文 -> 逗号
    seg = seg.replace("?", "")      # 其余孤立 ? -> 删除
    return seg


def fix_text(s):
    return SEG_RE.sub(lambda m: fix_seg(m.group(0)), s)


def main():
    apply = "--apply" in sys.argv
    files_hit = []
    for b in BOOKS:
        src = os.path.join(BASE, "wiki", "tiddlers", "5 环境和社会", b)
        for root, _, fs in os.walk(src):
            for f in fs:
                if not f.endswith(".tid"):
                    continue
                p = os.path.join(root, f)
                with open(p, "r", encoding="utf-8") as fh:
                    s = fh.read()
                if "?" not in s:
                    continue
                new = fix_text(s)
                if new != s:
                    files_hit.append((p, os.path.relpath(p, src), s, new))

    tot_m = tot_del = 0
    for _, rel, s, new in files_hit:
        tot_m += len(PAT_MID.findall(s))
        tot_del += s.count("?") - new.count("?")

    print("命中文件 %d" % len(files_hit))
    print("  中文?中文 -> ， 约 %d 处（含疑问词保护跳过的）" % tot_m)
    print("  其余孤立 ? 删除  约 %d 处" % tot_del)

    print("\n样本（前 6 个文件，改造前后片段）：")
    for p, rel, s, new in files_hit[:6]:
        print("  %s" % rel)
        i = new.find("，")
        j = new.find(">?<")
        k = new.find("?<")
        pos = min([x for x in (i, j, k) if x >= 0], default=-1)
        if pos >= 0:
            print("     ...%s..." % new[max(0, pos - 25) : pos + 25].replace("\n", " "))

    if apply and files_hit:
        for p, rel, s, new in files_hit:
            dst = os.path.join(BAK, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
        print("\n已写入，备份 ->", BAK)
    else:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
