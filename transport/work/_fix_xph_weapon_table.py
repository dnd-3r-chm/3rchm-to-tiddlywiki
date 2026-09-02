# -*- coding: utf-8 -*-
"""修复 XPH扩展灵能手册/7装备/武器.tid 内表7-5（第36-56行）的单元格闭合错误。

问题：表7-5 每行最后一列写成 <td>基础价格调整值</p></td>，
误将 </td> 写成了 </p>。正确应为 <td>基础价格调整值</td>。

处理范围：仅第一个 <table>...</table>（即表7-5），不影响表7-6
（其合法结构为 <td ...><p>文本</p></td>，内部含 <p>，不匹配本规则）。

规则：在表7-5 块内，将 <td>文本(无<p>包裹)</p></td> 修正为 <td>文本</td>。
"""
import datetime
import os
import re
import shutil

# 脚本位于 transport/work，目标文件相对 work 的路径
PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "wiki", "tiddlers",
    "1 核心补充书籍", "XPH扩展灵能手册", "7装备", "武器.tid"
))

# 仅匹配：td 直接以文本开头、错误以 </p> 闭合、且不含任何 <p> 的单元格
BAD_CELL = re.compile(r"<td>([^<]*)</p></td>")


def fix_first_table(text):
    # 定位第一个 <table> 与对应的 </table>
    start = text.find("<table>")
    if start == -1:
        return text, 0
    end = text.find("</table>", start)
    if end == -1:
        return text, 0
    end += len("</table>")
    block = text[start:end]
    new_block, n = BAD_CELL.subn(r"<td>\1</td>", block)
    if n == 0:
        return text, 0
    return text[:start] + new_block + text[end:], n


def main():
    raw = open(PATH, encoding="utf-8").read()
    new, n = fix_first_table(raw)
    if n == 0:
        print("未发现需修正的单元（已修复或模式不符），未改动。")
        return
    # 备份
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = PATH + f".bak_{ts}"
    shutil.copy2(PATH, bak)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"已修正 {n} 处单元闭合错误。")
    print(f"备份 -> {bak}")


if __name__ == "__main__":
    main()
