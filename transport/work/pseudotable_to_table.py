# -*- coding: utf-8 -*-
"""把「用全角空格对齐列的伪表格」(连续纯文本 <p> 行) 转换为真 <table>。

识别规则：
  * 行 = 纯文本 <p>...</p>（内部无其它标签）且含全角空格 U+3000
  * 块 = 连续的上述行（中间只允许空行；出现其它内容则断块），且行数 >= 2
  * 列 = 按 1+ 连续全角空格切分（不能要求 >=2：列宽被词长占满时只剩 1 个空格，
         如 "吟游诗人　控制者"）
  * 首行作表头 <th>，其余 <td>；各行补空单元格到块内最大列数

跳过 0 核心三宝书\\PHB玩家手册（已排版完成）。默认干跑，--apply 才写入并备份。
"""
import datetime
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
SKIP = "0 核心三宝书\\PHB玩家手册\\"

P_ROW = re.compile(r"^<p>([^<]*)</p>$")
FWSP = "\u3000"


def find_blocks(lines):
    """返回 [(start, end)] 行索引区间，块内为连续伪表格行。"""
    blocks = []
    cur = []
    prev = None
    for i, ln in enumerate(lines):
        m = P_ROW.match(ln)
        is_pt = bool(m) and FWSP in m.group(1)
        if is_pt:
            if cur and i - prev > 1:
                between = lines[prev + 1 : i]
                if not all(not b.strip() for b in between):
                    blocks.append(cur)
                    cur = []
            cur.append(i)
            prev = i
        else:
            if cur and ln.strip():
                blocks.append(cur)
                cur = []
                prev = None
    if cur:
        blocks.append(cur)
    return [b for b in blocks if len(b) >= 2]


def split_row(inner):
    return [c.strip() for c in re.split(FWSP + "+", inner.strip())]


def make_table(rows_cells):
    maxc = max(len(r) for r in rows_cells)
    out = ["<table>"]
    for idx, cells in enumerate(rows_cells):
        cells = cells + [""] * (maxc - len(cells))
        tag = "th" if idx == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def process_file(path, apply=False):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    blocks = find_blocks(lines)
    if not blocks:
        return None
    info = []
    for b in blocks:
        rows = []
        for i in b:
            m = P_ROW.match(lines[i])
            rows.append(split_row(m.group(1)))
        maxc = max(len(r) for r in rows) if rows else 0
        # 块内最大列数 < 2 说明没有真正的列分隔，不是表格
        if maxc < 2:
            continue
        # 列数一致性：真伪表格各行应切出相同的列数。
        # 人物卡/键值文本(如 "男性　半兽人　野蛮人5…；" / "挑战等级　8；")
        # 会被切成 4 列与 2 列，比例不足 70%，据此排除，避免误转。
        counts = [len(r) for r in rows]
        mode = max(set(counts), key=counts.count)
        if counts.count(mode) / len(rows) < 0.7:
            continue
        # 排除 D&D 人物卡/stat block（"属性名 + 自由文本值"，如
        # "CR　8；中型类人生物(精灵)；" / "防御等级　18，接触..."）：
        # 其"值"单元格几乎都以中文分号 ；结尾，而真表格的数据单元格不会。
        data_rows = rows[1:]
        if data_rows:
            semi = sum(
                1
                for r in data_rows
                if [c for c in r if c] and [c for c in r if c][-1].endswith("；")
            )
            if semi / len(data_rows) >= 0.5:
                continue
        # 排除「并排双表」：两个表以半角空格并排时，分隔用的是半角而非全角空格，
        # 切分会把两列内容并进同一单元格（如 "价格   页面(100)"），自动转会错乱，
        # 故保留原样交由人工处理（宁可漏转，也不错转破坏内容）。
        if any(re.search(r" {2,}", c) for r in rows for c in r):
            continue
        info.append((b, rows, maxc))
    if not info:
        return None
    if apply:
        # 从后往前替换，避免行索引失效
        for b, rows, _ in reversed(info):
            table = make_table(rows)
            lines[b[0] : b[-1] + 1] = [table]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
    return info


def main():
    apply = "--apply" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(BASE, "backups", "wiki_pseudotable_" + ts)
    if apply:
        os.makedirs(bak, exist_ok=True)

    total_blocks = 0
    total_files = 0
    samples = []
    for root, _, fs in os.walk(SRC):
        for f in fs:
            if not f.endswith(".tid"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SRC)
            if rel.startswith(SKIP):
                continue
            with open(p, "r", encoding="utf-8") as fh:
                s = fh.read()
            title_line = ""
            for line in s.split("\n", 5):
                if line.startswith("title:"):
                    title_line = line
                    break
            if "$:/" in title_line:
                continue
            info = process_file(p, apply=False)
            if not info:
                continue
            total_files += 1
            total_blocks += len(info)
            if apply:
                dst = os.path.join(bak, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(p, dst)
                process_file(p, apply=True)
            print(f"[块 {len(info)}] {rel}")
            for b, rows, maxc in info:
                head = " | ".join(rows[0][:5])
                print(f"    行{b[0]+1}-{b[-1]+1}  {len(rows)}行 x {maxc}列   [{head[:70]}]")
            if len(samples) < 6:
                b, rows, maxc = info[0]
                samples.append((rel, b, rows, maxc))

    print(f"\n文件 {total_files}  伪表格块 {total_blocks}")
    for rel, b, rows, maxc in samples:
        print(f"\n----- 样本 {rel} (行{b[0]+1}-{b[-1]+1}, {maxc}列) -----")
        print(make_table(rows)[:700])
    if not apply:
        print("\n（干跑，未写入。确认无误后加 --apply 执行并自动备份）")
    else:
        print(f"\n[备份] -> {bak}")


if __name__ == "__main__":
    main()
