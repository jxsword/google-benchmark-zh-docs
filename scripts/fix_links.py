#!/usr/bin/env python3
"""zh/ 译文跨目录链接规范化：`../` 开头的链接目标 → 上游 GitHub 绝对 URL。

背景（PLAN §7 第 4 项 / §11）：上游 docs 内 .md 互链在 zh/ 同名镜像结构下由
mkdocs 天然解析，保留相对路径；`../README.md` 类跨目录链接在 mkdocs 站点
无处解析（zh/ 之上没有目录），统一映射为上游 GitHub blob 绝对 URL。
基线快照实测（88e2febd38，2026-11-19）：docs 内互链 18 处；跨目录链接 1 处
（perf_counters.md:33 `../README.md#custom-counters`）。PLAN §11 的
「15 处互链 + 2 处跨目录」为计划期估测，以快照实测为准，报告已记录差异。

CLI:
  --apply      原地改写 zh/ 文件
  --check      只报告（默认；validate 门禁第 4 项调用，存在未映射 ../ 链接 → exit 2）
  --file F     只处理指定 zh 文件（相对 zh/ 的文件名）
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).parent.parent.resolve()
ZH_DIR = REPO_ROOT / "zh"

UPSTREAM_BLOB_URL = "https://github.com/google/benchmark/blob/main"

# 行内链接（ (?<!!) 排除图片 ![alt](target) —— 图片路径一律不动 ）
LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# ../ 前缀（可多级）
_PARENT_RE = re.compile(r"^(?:\.\./)+")


def fix_content(text: str) -> Tuple[str, List[str]]:
    """返回 (fixed_text, changes)；changes 元素形如 "../X -> https://..."。"""
    changes: List[str] = []

    def _sub(match: re.Match) -> str:
        link_text = match.group(1)
        target = match.group(2)
        if not _PARENT_RE.match(target):
            return match.group(0)
        rel = _PARENT_RE.sub("", target)
        new_target = f"{UPSTREAM_BLOB_URL}/{rel}"
        changes.append(f"{target} -> {new_target}")
        return f"[{link_text}]({new_target})"

    fixed = LINK_RE.sub(_sub, text)
    return fixed, changes


def process(zh_file: Path, apply: bool) -> List[str]:
    text = zh_file.read_text(encoding="utf-8")
    fixed, changes = fix_content(text)
    if apply and changes and fixed != text:
        zh_file.write_text(fixed, encoding="utf-8")
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="fix_links.py",
        description="zh/ 跨目录链接映射为上游 GitHub 绝对 URL（默认只检查）")
    parser.add_argument("--apply", action="store_true", help="原地改写 zh/ 文件")
    parser.add_argument("--file", help="只处理指定 zh 文件")
    args = parser.parse_args(argv)

    if args.file:
        targets = [ZH_DIR / args.file]
    else:
        targets = sorted(ZH_DIR.glob("*.md")) if ZH_DIR.is_dir() else []
    if not targets:
        print(json.dumps({"ok": True, "files": 0, "changes": []},
                         ensure_ascii=False))
        return

    report = {}
    all_changes: List[str] = []
    for f in targets:
        if not f.exists():
            print(f"fix_links: 文件不存在：{f}", file=sys.stderr)
            sys.exit(1)
        changes = process(f, args.apply)
        if changes:
            report[f.name] = changes
            all_changes.extend(changes)

    print(json.dumps({
        "ok": True,
        "apply": args.apply,
        "scanned": len(targets),
        "files_changed": sorted(report.keys()),
        "changes": report,
        "total": len(all_changes),
    }, ensure_ascii=False, indent=2))
    # 未映射的 ../ 链接在 check 模式下即残留（apply 后不应再出现）
    if not args.apply and all_changes:
        print(f"fix_links: 发现 {len(all_changes)} 处待映射跨目录链接"
              "（--apply 改写）", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
