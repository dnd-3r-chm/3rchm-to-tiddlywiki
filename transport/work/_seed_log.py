# -*- coding: utf-8 -*-
"""初始化 logs/转换日志.log。

说明：PowerShell 的命令行参数会破坏中文字符，因此不能用 `python -c` 写日志，
必须经由本脚本文件（UTF-8）写入。用后即删。
"""
import _paths as P
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

LOG_DIR = P.LOGS
LOG_FILE = os.path.join(LOG_DIR, "转换日志.log")

os.makedirs(LOG_DIR, exist_ok=True)
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== 转换日志 ===\n")
    f.write("由 transport/work/convert_book.py 的 log() 追加写入，编码 UTF-8。\n")
    f.write("每次批量转换会记录：开始/完成、SKIP(已合并)、MISSING(源文件缺失)、ERROR、OK。\n\n")

with open(LOG_FILE, "r", encoding="utf-8") as f:
    print(f.read())
print("written:", LOG_FILE)
