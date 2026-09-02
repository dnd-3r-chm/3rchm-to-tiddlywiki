# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

# 严格噪音定义
word = re.compile(r"StartFragment|EndFragment|&nbsp;|<o:p>|<o:P>|<u1:p>|<u1:P>|xml:namespace|class=\"?Mso|mso-|<!--", re.I)
span_font = re.compile(r"</?span[\s>]|</?font[\s>]|style=", re.I)
empty_attr_p = re.compile(r"<p\s+>")                       # 真·<p > 空属性
p_inner_blank = re.compile(r"<p[^>]*>\s*\n\s*\n")          # p 标签内连续空行（真空行）
fullwidth = re.compile(r"[Ａ-Ｚａ-ｚ０-９（）＂＇‘’\uff02]")

total = {"word":0,"span_font":0,"empty_attr_p":0,"p_inner_blank":0,"fullwidth":0}
samples = {k:[] for k in total}
for book in sorted(os.listdir(TID)):
    bd = os.path.join(TID, book)
    if not os.path.isdir(bd) or book.startswith("."):
        continue
    for p in glob.glob(os.path.join(bd, "**", "*.tid"), recursive=True):
        if os.sep + "插图" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        parts = t.split("\n")
        body = "\n".join(parts[5:]) if len(parts) > 5 else ""
        for k, rx in {"word":word,"span_font":span_font,"empty_attr_p":empty_attr_p,
                      "p_inner_blank":p_inner_blank,"fullwidth":fullwidth}.items():
            m = rx.search(body)
            if m:
                total[k] += 1
                if len(samples[k]) < 3:
                    i = m.start()
                    samples[k].append((os.path.relpath(p, TID), repr(body[max(0,i-20):i+30])))

print("=== 严格噪音复验（全库）===")
for k, v in total.items():
    print(f"  {k}: {v}")
for k, lst in samples.items():
    if lst:
        print(f"\n[{k}] 样本:")
        for rel, s in lst:
            print("  ", rel, s)
