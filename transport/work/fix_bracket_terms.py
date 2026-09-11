# -*- coding: utf-8 -*-
"""统一处理「中文 + 单方括号」：

1) 技能子项  知识[地下城]  ->  知识(地下城)
   （3R 规范：技能子项/子学派用圆括号）
2) 其余（法术描述符、脚注、杂项）  塑能系[力场]  ->  塑能系&#91;力场&#93;
   （实体化：渲染仍是 [] 外观，但不会被 TiddlyWiki 解析成指向不存在条目的链接）

不匹配 [[wikilink]]、[img[...]]（要求方括号前是中文字符，且内容不含 [ ]）。
默认干跑，--apply 才写入并备份。
"""
import datetime
import os
import re
import shutil
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_brackets_" + TS)

# 技能子项 -> 圆括号
TERM_PAT = re.compile(r"(知识|专业|手艺)\[([^\[\]]{1,20})\]")
# 其余中文后的单方括号 -> 实体
DESC_PAT = re.compile(r"(?<=[\u4e00-\u9fff])\[([^\[\]]{1,20})\]")


def scan():
    out = []
    for root, _, fs in os.walk(SRC):
        for f in fs:
            if not f.endswith(".tid"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SRC)
            with open(p, "r", encoding="utf-8") as fh:
                s = fh.read()
            title_line = ""
            for line in s.split("\n", 5):
                if line.startswith("title:"):
                    title_line = line
                    break
            if "$:/" in title_line:
                continue
            ms = list(DESC_PAT.finditer(s))
            if ms:
                out.append((p, rel, s, ms))
    return out


def main():
    apply = "--apply" in sys.argv
    items = scan()
    total = sum(len(m) for _, _, _, m in items)
    term_n = 0
    counter = Counter()
    for _, _, s, ms in items:
        term_n += len(TERM_PAT.findall(s))
        for m in ms:
            counter[m.group(1)] += 1
    print("文件 %d  单方括号总计 %d 处" % (len(items), total))
    print(
        "  其中 技能子项(->圆括号) %d 处；描述符/脚注(->实体) %d 处"
        % (term_n, total - term_n)
    )
    print("\n按内容统计（前 25）：")
    for k, v in counter.most_common(25):
        print("   [%s]  %d" % (k, v))
    print("\n涉及文件（前 10）：")
    for p, rel, s, ms in items[:10]:
        print("   %s  (%d 处)" % (rel, len(ms)))
    if apply and items:
        for p, rel, s, ms in items:
            dst = os.path.join(BAK, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)
            new = TERM_PAT.sub(lambda m: m.group(1) + "(" + m.group(2) + ")", s)
            new = DESC_PAT.sub(lambda m: "&#91;" + m.group(1) + "&#93;", new)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
        print("\n已写入，备份 -> %s" % BAK)
    elif not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
