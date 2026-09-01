# -*- coding: utf-8 -*-
"""统一路径常量：基于本文件位置自动定位，消除硬编码的旧绝对路径。

目录结构假定（本文件位于 <ROOT>/transport/work/_paths.py）：

    <ROOT>/                      仓库根（含 Contents.hhc、0 核心三宝书\\ 等源目录）
    <ROOT>/transport/
        work/                    本文件所在目录（脚本、CSV 映射表）
        wiki/tiddlers/           所有 .tid 与图片，按源目录存放
        logs/                    转换日志、链接校验报告

用法（各脚本统一范式，保持原有变量名不变）：

    import _paths as P
    ROOT = P.ROOT
    WIKI = P.WIKI_TIDDLERS

深层路径请用 os.path.join 拼接，避免写死反斜杠：

    TARGET_DIR = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "PHB玩家手册", "11法术", "法术描述")
"""
import os

# work/ 目录（本文件所在目录）
WORK = os.path.dirname(os.path.abspath(__file__))
# transport/ 目录
TRANSPORT = os.path.dirname(WORK)
# 仓库根目录
ROOT = os.path.dirname(TRANSPORT)

# TiddlyWiki
WIKI = os.path.join(TRANSPORT, "wiki")
WIKI_TIDDLERS = os.path.join(WIKI, "tiddlers")

# 日志
LOGS = os.path.join(TRANSPORT, "logs")
LOG_FILE = os.path.join(LOGS, "转换日志.log")

# 源目录树中的 CHM 目录树文件
HHC_PATH = os.path.join(ROOT, "Contents.hhc")

# work/ 下的映射表
INVENTORY_CSV = os.path.join(WORK, "inventory.csv")
HHC_CSV = os.path.join(WORK, "hhc_mapping.csv")
FINAL_MAPPING = os.path.join(WORK, "final_mapping.csv")

# 高频深层目录（多个脚本复用）
# wiki/tiddlers/0 核心三宝书/DMG城主指南
DMG_TIDDLERS = os.path.join(WIKI_TIDDLERS, "0 核心三宝书", "DMG城主指南")
# .../DMG城主指南/所有DMG表格
DMG_TABLES = os.path.join(DMG_TIDDLERS, "所有DMG表格")


def self_check():
    """打印解析结果，用于路径自检（只读，无副作用）。"""
    items = [
        ("WORK", WORK),
        ("TRANSPORT", TRANSPORT),
        ("ROOT", ROOT),
        ("WIKI_TIDDLERS", WIKI_TIDDLERS),
        ("LOGS", LOGS),
        ("HHC_PATH", HHC_PATH),
        ("FINAL_MAPPING", FINAL_MAPPING),
        ("DMG_TIDDLERS", DMG_TIDDLERS),
        ("DMG_TABLES", DMG_TABLES),
    ]
    print("=" * 60)
    print("_paths.py 路径自检")
    print("=" * 60)
    for name, value in items:
        exists = "OK " if os.path.exists(value) else "-- "
        print(f"{exists}{name:<16}{value}")
    print("-" * 60)
    missing = [n for n, v in items if not os.path.exists(v)]
    if missing:
        print(f"[WARN] 以下路径不存在（不影响导入，但相关脚本会失败）: {', '.join(missing)}")
    else:
        print("[OK] 全部路径存在")
    print("=" * 60)


if __name__ == "__main__":
    self_check()
