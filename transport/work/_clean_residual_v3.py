# -*- coding: utf-8 -*-
"""第三轮：压 p 标签内部空行 <p>\n\n<b> -> <p>\n<b>。
干跑预览，--apply 实写。"""
import os, glob, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

def fix(body):
    # <p> 紧跟的连续换行压成单个换行（标签内空行）
    body = re.sub(r"(<p[^>]*>)\s*\n\s*", r"\1\n", body)
    # </p> 前的连续换行压成单个换行
    body = re.sub(r"\s*\n\s*(</p>)", r"\1", body)
    return body

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
                if not apply and len(samples) < 8:
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
