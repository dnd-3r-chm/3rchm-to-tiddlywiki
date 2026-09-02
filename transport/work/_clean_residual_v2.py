# -*- coding: utf-8 -*-
"""第二轮针对性清理（在 _clean_all_noise 之后）：
1. 删 HTML 注释 <!-- ... -->（第一轮漏掉）
2. 标签内多余空格 <p  align= -> <p align=，<p > -> <p>
3. p 标签内空行 <p>\n\n<b> -> <p>\n<b>
干跑预览，--apply 实写。"""
import os, glob, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

def fix(body):
    # 1. 删注释（含跨行）
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    # 2. 标签内多余空格：<p  align= -> <p align= ； <p > -> <p>
    body = re.sub(r"<(\w+)\s{2,}", r"<\1 ", body)   # 双+空格 -> 单空格
    body = re.sub(r"<(\w+)\s+>", r"<\1>", body)       # <p > -> <p>
    # 3. p 标签内空行：<p>\n\s*\n -> <p>\n
    body = re.sub(r"(<p[^>]*>)\s*\n\s*\n", r"\1\n", body)
    body = re.sub(r"\n\s*\n\s*(</p>)", r"\1", body)
    # 4. 连续空行压缩（3+ -> 2）
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()

def main():
    apply = "--apply" in sys.argv
    changed = 0
    samples = []
    for book in sorted(os.listdir(TID)):
        bd = os.path.join(TID, book)
        if not os.path.isdir(bd) or book.startswith("."):
            continue
        for p in glob.glob(os.path.join(bd, "**", "*.tid"), recursive=True):
            if os.sep + "插图" + os.sep in p:
                continue
            raw = open(p, encoding="utf-8").read()
            lines = raw.split("\n")
            header = "\n".join(lines[:5])
            body = "\n".join(lines[5:]) if len(lines) > 5 else ""
            new_body = fix(body)
            if new_body != body:
                changed += 1
                if not apply and len(samples) < 10:
                    rel = os.path.relpath(p, TID)
                    for i, (a, b) in enumerate(zip(body, new_body)):
                        if a != b:
                            samples.append(f"  [preview] {rel}: {repr(body[max(0,i-25):i+25])} -> {repr(new_body[max(0,i-25):i+25])}")
                            break
                else:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(header + "\n" + new_body + "\n")
    for s in samples:
        print(s)
    print(f"\n{'[DRY-RUN] ' if not apply else '[APPLIED] '}修改文件数: {changed}")

if __name__ == "__main__":
    main()
