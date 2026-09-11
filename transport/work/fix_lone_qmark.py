# -*- coding: utf-8 -*-
"""修复 CW 中单个 '?' 乱码（源混编码致中文逗号/句号解码失败）。

仅限 CW 完美战力（本次新搬运、已确认为乱码）。**不碰其他书**——实测 PHB/MM5/PHB2
等书中的 '?' 多为真问句（"谁能…解决掉?"、"为什么不使用模板呢?"），误改会破坏内容。

规则：
  * 句中 '?'（前后均为中文）-> '，'
  * 句末 '?'（后紧跟 </p>）-> '。'
  * 保护：若该 '?' 所在 <p> 段落含疑问词（吗/呢/什么/为什么/如何/谁/哪/是否/怎么），
    则跳过不动（视为真问句）。

默认干跑，--apply 写入并备份。
"""
import datetime
import os
import re
import shutil
import sys

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers", "3 完美系列", "CW完美战力")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_loneqmark_" + TS)

CJK = r"\u4e00-\u9fff"
PAT_MID = re.compile(r"(?<=[" + CJK + r"])\?(?=[" + CJK + r"])")
PAT_END = re.compile(r"\?(?=</p>)")
PARA_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
QUESTION_WORDS = ("吗", "呢", "什么", "为什么", "如何", "谁", "哪", "是否", "怎么")


def para_has_question(text, pos):
    """判断 pos 所在 <p> 段落是否含疑问词（含则视为真问句，保护）。"""
    for m in PARA_RE.finditer(text):
        if m.start() <= pos < m.end():
            seg = m.group(0)
            return any(w in seg for w in QUESTION_WORDS)
    return True  # 找不到段落时保守跳过


def convert(s):
    """返回 (new_text, n_mid, n_end, skipped)"""
    out_mid = out_end = skipped = 0
    res = []
    pos = 0
    # 先处理句中，再处理句末；逐处判断疑问词保护
    for m in PAT_MID.finditer(s):
        res.append(s[pos : m.start()])
        if para_has_question(s, m.start()):
            res.append("?")
            skipped += 1
        else:
            res.append("，")
            out_mid += 1
        pos = m.end()
    res.append(s[pos:])
    s2 = "".join(res)

    res = []
    pos = 0
    for m in PAT_END.finditer(s2):
        res.append(s2[pos : m.start()])
        if para_has_question(s2, m.start()):
            res.append("?")
            skipped += 1
        else:
            res.append("。")
            out_end += 1
        pos = m.end()
    res.append(s2[pos:])
    return "".join(res), out_mid, out_end, skipped


files_hit = []
for root, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        if not (PAT_MID.search(s) or PAT_END.search(s)):
            continue
        files_hit.append((p, rel, s))

tot_m = tot_e = tot_s = 0
converted = []
for p, rel, s in files_hit:
    new, nm, ne, sk = convert(s)
    converted.append((p, rel, new))
    tot_m += nm
    tot_e += ne
    tot_s += sk

print("文件 %d" % len(files_hit))
print("  句中 '?' -> ，  %d 处" % tot_m)
print("  句末 '?' -> 。  %d 处" % tot_e)
print("  疑问词保护跳过  %d 处" % tot_s)

print("\n样本（前 5 个文件）：")
for p, rel, new in converted[:5]:
    i = new.find("，")
    j = new.find("。")
    k = i if i >= 0 else j
    print("  %s" % rel)
    if k >= 0:
        print("     ...%s..." % new[max(0, k - 30) : k + 30].replace("\n", " "))

if "--apply" in sys.argv and converted:
    for p, rel, new in converted:
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)
    print("\n已写入，备份 ->", BAK)
else:
    print("\n（干跑，未写入。加 --apply 执行并自动备份）")
