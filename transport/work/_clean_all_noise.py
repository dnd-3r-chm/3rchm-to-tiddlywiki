# -*- coding: utf-8 -*-
"""全库通用噪音清理（保守版）：只删 Word 噪音，不动合法表格/div 结构。
- 删 <o:p>/<u1:p>/xml:namespace/StartFragment/EndFragment
- 去 span/font/style/class/lang 标签与属性（噪音）
- 压标签内部换行（<p \\n align= -> <p align=）
- 全角直双引号 0xff02 -> "（管线 MAP 漏掉的）
- 删空 <p>&nbsp;</p> / <p></p>
- 压缩连续空行（3+ -> 2）
干跑预览，--apply 实写。"""
import os, glob, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

FW = {}
for i in range(26):
    FW[chr(0xFF21 + i)] = chr(0x41 + i)
    FW[chr(0xFF41 + i)] = chr(0x61 + i)
for i in range(10):
    FW[chr(0xFF10 + i)] = chr(0x30 + i)
FW.update({"\uff08": "(", "\uff09": ")", "\u201c": '"', "\u201d": '"',
           "\u2018": "'", "\u2019": "'", "\uff02": '"'})

def normalize(body):
    # Word 标记
    body = re.sub(r"<\?xml[^>]*\?>", "", body, flags=re.I)
    body = re.sub(r"<o:p>|</o:p>|<o:P>|</o:P>", "", body, flags=re.I)
    body = re.sub(r"<u1:p>|</u1:p>|<u1:P>|</u1:P>", "", body, flags=re.I)
    body = re.sub(r"<\??xml:namespace[^>]*>", "", body, flags=re.I)
    body = re.sub(r"StartFragment|EndFragment", "", body, flags=re.I)
    body = re.sub(r"mso-[a-z-]+:\s*[^;\"]*;?", "", body, flags=re.I)
    # 去无用的 span/font 标签与 style/class/lang 属性
    body = re.sub(r"</?span[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?font[^>]*>", "", body, flags=re.I)
    body = re.sub(r'\sclass="[^"]*"', "", body, flags=re.I)
    body = re.sub(r"\sstyle=\"[^\"]*\"", "", body, flags=re.I)
    body = re.sub(r"\sclass='[^']*'", "", body, flags=re.I)
    body = re.sub(r"\sstyle='[^']*'", "", body, flags=re.I)
    body = re.sub(r"\slang=\"[^\"]*\"", "", body, flags=re.I)
    body = re.sub(r"\slang='[^']*'", "", body, flags=re.I)
    # 压标签内部换行：<p \n align= -> <p align=  ； <td \n height= -> <td height=
    body = re.sub(r"<\s*(\w+)", r"<\1", body)            # < p  -> <p
    body = re.sub(r"(\w+)\s*\n\s*([a-zA-Z-]+)\s*=", r"\1 \2=", body)  # p \n align= -> p align=
    body = re.sub(r"=\s*\n\s*\"", r'="', body)           # = \n " -> ="
    body = re.sub(r"\"\s*\n\s*", '"', body)              # " \n  -> "
    body = re.sub(r"\s+>", ">", body)                    # 尖括号内尾随空格
    # 空加粗/空斜体残留
    body = re.sub(r"<b>\s*(?:<br\s*/?>\s*)*</b>", "", body, flags=re.I)
    body = re.sub(r"<i>\s*(?:<br\s*/?>\s*)*</i>", "", body, flags=re.I)
    # 全角 ASCII 转半角（含 0xff02 全角直双引号）
    body = body.translate(str.maketrans(FW))
    body = body.replace("&nbsp;", " ")
    # 压缩连续空白行（3+ 换行 -> 2 换行）
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    # 删除空段落
    body = re.sub(r"<p>\s*&nbsp;\s*</p>", "", body, flags=re.I)
    body = re.sub(r"<p>\s*</p>", "", body, flags=re.I)
    return body.strip()

def main():
    apply = "--apply" in sys.argv
    changed = 0
    diff_samples = []
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_root = os.path.join(ROOT, "transport", "work", f"backup_allnoise_{ts}")
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
            new_body = normalize(body)
            if new_body != body:
                changed += 1
                if not apply and len(diff_samples) < 10:
                    rel = os.path.relpath(p, TID)
                    for i, (a, b) in enumerate(zip(body, new_body)):
                        if a != b:
                            diff_samples.append(f"  [preview] {rel}: {repr(body[max(0,i-25):i+25])} -> {repr(new_body[max(0,i-25):i+25])}")
                            break
                else:
                    # 备份原文件
                    rel = os.path.relpath(p, TID)
                    bak = os.path.join(bak_root, rel)
                    os.makedirs(os.path.dirname(bak), exist_ok=True)
                    with open(bak, "w", encoding="utf-8") as bf:
                        bf.write(raw)
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(header + "\n" + new_body + "\n")
    for s in diff_samples:
        print(s)
    print(f"\n{'[DRY-RUN] ' if not apply else '[APPLIED] '}修改文件数: {changed}")
    if apply:
        print(f"备份目录: {bak_root}")

if __name__ == "__main__":
    main()
