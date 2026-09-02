# -*- coding: utf-8 -*-
"""清理 HBG英雄构筑指南 已生成 tid 的噪音（2026-09-02）。

问题：HBG 源 HTML 的段落被 Word/网页导出样式包裹，形如：
    <span \n\n style='FONT-SIZE: 13px; FONT-FAMILY: "Segoe UI", ...（超长）'>
    文字</span><br \n\n style='超长样式'>
convert_pilot.clean_html() 只剥离 <style> 块与 <script>，不删标签的 style 属性；
strip_hooks.process_body() 对 HBG 这本书也无匹配规则，故大量噪音残留：
  - <span style='...'> 超长内联样式（287+ 处）
  - <br style='...'> 作段落分隔（未按规范转 <p>）

清洗步骤：
  1. 删除 <span> 开闭标签（unwrap，保留文字；[^>]* 可跨行匹配被拆开的标签）
  2. 删除 <br ...>（含跨行 style）并标记为段落分隔点
  3. 删除所有剩余标签的 style 属性（引号/无引号两种，含跨行）
  4. 按分隔点切分，非空段用 <p> 包裹
  5. 全角 ASCII 转半角（对齐全库规则）、压缩连续空行

用法：
  python clean_hbg.py            # 干跑预览
  python clean_hbg.py --apply    # 写入（自动备份到 transport/work/backup_hbg_clean_<时间戳>）
"""
import datetime
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_pilot as cp

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/HBG英雄构筑指南"
WORK_BAK = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/work"

MARK = "@@HBGBR@@"
BR_RE = re.compile(r"<br\b[^>]*>", re.S | re.I)
SPAN_RE = re.compile(r"</?span\b[^>]*>", re.S | re.I)
STYLE_ATTR_RE = re.compile(
    r"\s+style\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^\s>]+)", re.S | re.I
)


def clean_body(body):
    # 1. unwrap <span>
    body = SPAN_RE.sub("", body)
    # 2. <br ...> -> 段落分隔标记（含跨行的 <br \n\n style='...'>）
    body = BR_RE.sub(MARK, body)
    # 3. 删除剩余标签的 style 属性
    body = STYLE_ATTR_RE.sub("", body)
    # 4. 按标记切分并包 <p>
    segs = body.split(MARK)
    parts = []
    for seg in segs:
        seg = seg.strip()
        if not seg:
            continue
        # 已是块级标签（h*/p/div/table/ul 等）开头的，原样保留
        if re.match(r"^<(h[1-6]|p|div|table|ul|ol|li|details|blockquote)\b", seg, re.I):
            parts.append(seg)
        else:
            parts.append(f"<p>{seg}</p>")
    out = "\n\n".join(parts)
    # 5. 全角 ASCII 转半角 + 压缩连续空行 + 清理残留空标签属性空格
    out = cp.normalize_fullwidth_punct(out)
    out = re.sub(r"<(\w+)\s+>", r"<\1>", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def split_tid(content):
    """返回 (头部4行+空行, 正文)。"""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "":
            return "\n".join(lines[: i + 1]), "\n".join(lines[i + 1 :])
    return content, ""


def main():
    apply = "--apply" in sys.argv
    files = sorted(f for f in os.listdir(D) if f.endswith(".tid") and not f.endswith(".bak"))
    changed = []
    for f in files:
        p = os.path.join(D, f)
        raw = open(p, encoding="utf-8").read()
        head, body = split_tid(raw)
        if not body:
            continue
        new_body = clean_body(body)
        if new_body == body.strip():
            continue
        changed.append((f, new_body))

    print(f"待清洗 {len(changed)} / {len(files)} 个文件")
    for f, _ in changed[:6]:
        print("  ", f)

    if not apply:
        if changed:
            f0, nb = changed[0]
            print(f"\n----- 样本 {f0} 清洗后（前 500 字符）-----")
            print(nb[:500])
        print("\n（干跑，未写入。加 --apply 执行并自动备份到 work/）")
        return

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(WORK_BAK, f"backup_hbg_clean_{ts}")
    os.makedirs(bak, exist_ok=True)
    for f, _ in changed:
        shutil.copy2(os.path.join(D, f), os.path.join(bak, f))
    for f, nb in changed:
        p = os.path.join(D, f)
        raw = open(p, encoding="utf-8").read()
        head, _ = split_tid(raw)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(head + nb + "\n")
    print(f"\n已清洗 {len(changed)} 个文件。备份 -> {bak}")


if __name__ == "__main__":
    main()
