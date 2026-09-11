# -*- coding: utf-8 -*-
"""排查 6/7/9 系列所有疑似 WinCHM 默认模板文件（新建主题/新建项目/untitled 等）：
正确解码后读 <title>，并统计正文纯文本中文字符数。
判定：title 仍为默认名（新建主题/新建项目/untitled/空）且 正文中文 < 30 -> 空模板（应 SKIP）；
否则为真内容页（保留转换）。
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import convert_pilot as cp

SRC = cp.ROOT
SERIES = ["6 种族书", "7 扩展全新体系", "9 世设"]
SUSPECTS = ("新建", "untitled", "new ", "主题", "topic", "untitl")

DEFAULT_TITLES = {"新建主题", "新建项目", "新建网页", "untitled", "untitled document", ""}


def main():
    for key in SERIES:
        base = os.path.join(SRC, key)
        for root, dirs, fs in os.walk(base):
            for x in sorted(fs):
                low = x.lower()
                if not any(s in low for s in SUSPECTS):
                    continue
                fp = os.path.join(root, x)
                try:
                    text = cp.read_text(fp)
                except Exception as e:
                    print(f"[读取失败] {os.path.relpath(fp, SRC)}: {e}")
                    continue
                tm = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
                title = tm.group(1).strip() if tm else ""
                body = cp.extract_body(text)
                plain = re.sub(r"<[^>]+>", "", body)
                cn = len(re.findall(r"[一-鿿]", plain))
                rel = os.path.relpath(fp, SRC)
                is_default = title.strip().lower() in {t.lower() for t in DEFAULT_TITLES}
                flag = "EMPTY(应SKIP)" if (is_default and cn < 30) else "CONTENT(保留)"
                print(f"[{flag}] cn={cn:5d} title={title!r:28} {rel}")


if __name__ == "__main__":
    main()
