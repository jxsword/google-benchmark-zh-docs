#!/usr/bin/env python3
"""zh/ 译文链接规范化与页内锚点注入。

跨目录链接（PLAN §7 第 4 项 / §11）：上游 docs 内 .md 互链在 zh/ 同名镜像结构下由
mkdocs 天然解析，保留相对路径；`../README.md` 类跨目录链接在 mkdocs 站点
无处解析（zh/ 之上没有目录），统一映射为上游 GitHub blob 绝对 URL。
基线快照实测（88e2febd38，2026-11-19）：docs 内互链 18 处；跨目录链接 1 处
（perf_counters.md:33 `../README.md#custom-counters`）。

页内锚点注入（M5）：上游页内 TOC 用英文标题 slug（如 #command-line-options），
标题译成中文后 mkdocs 生成的锚点会变，链接断链。本模式把被引用的英文 slug 以
attr_list 语法（` {#slug}`）注入到 zh 对应标题（按标题位置与 source 一一配对，
数量必须相等），使中文站沿用上游锚点。

CLI:
  --apply            原地改写 zh/ 文件
  --check            只报告（默认；validate 门禁第 4 项调用，存在未映射 ../ 链接 → exit 2）
  --file F           只处理指定 zh 文件（相对 zh/ 的文件名）
  --anchors          启用页内锚点注入（与 --apply/--check 组合）
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent.resolve()
ZH_DIR = REPO_ROOT / "zh"
SOURCE_DIR = REPO_ROOT / "source"

UPSTREAM_BLOB_URL = "https://github.com/google/benchmark/blob/main"

# 行内链接（ (?<!!) 排除图片 ![alt](target) —— 图片路径一律不动 ）
LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# ../ 前缀（可多级）
_PARENT_RE = re.compile(r"^(?:\.\./)+")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
_ANCHOR_REF_RE = re.compile(r"\]\(#([^)\s]+)\)")


def fix_content(text: str) -> Tuple[str, List[str]]:
    """返回 (fixed_text, changes)；changes 元素形如 "../X -> https://..."。

    两类规范化：
    1. `../` 跨目录目标 → 上游 GitHub blob 绝对 URL；
    2. 缺 .md 后缀的相对页链接（上游笔误，如 user_guide#anchor）→ 补 .md，
       仅当 zh/ 同名镜像存在该文件（mkdocs 对此类链接报 unrecognized 且站点 404，
       2026-11-19 M5 本地构建实测 reducing_variance.md 两处）。"""
    changes: List[str] = []

    def _sub(match: re.Match) -> str:
        link_text = match.group(1)
        target = match.group(2)
        if not _PARENT_RE.match(target):
            # 缺 .md 后缀补全：形如 page#anchor 且 zh 同名文件存在
            m2 = re.fullmatch(r"([A-Za-z0-9_\-]+)(#.+)", target)
            if m2 and (ZH_DIR / f"{m2.group(1)}.md").exists():
                new_target = f"{m2.group(1)}.md{m2.group(2)}"
                changes.append(f"{target} -> {new_target}")
                return f"[{link_text}]({new_target})"
            return match.group(0)
        rel = _PARENT_RE.sub("", target)
        new_target = f"{UPSTREAM_BLOB_URL}/{rel}"
        changes.append(f"{target} -> {new_target}")
        return f"[{link_text}]({new_target})"

    fixed = LINK_RE.sub(_sub, text)
    return fixed, changes


# ---------- 页内锚点注入（M5） ----------

def _slugify_kramdown(text: str) -> str:
    """kramdown（Jekyll，上游站点渲染器）auto_ids 风格 slug。"""
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = s.strip()
    s = re.sub(r"\s+", "-", s)
    return s


def _slugify_github(text: str) -> str:
    """GitHub 渲染风格 slug（空格逐个转连字符，不压缩）。"""
    s = text.lower()
    s = re.sub(r"[^\w\- ]", "", s)
    s = s.replace(" ", "-")
    return s


def heading_slug_candidates(title: str) -> Tuple[str, ...]:
    return (_slugify_kramdown(title), _slugify_github(title))


def inject_anchors(zh_file: Path, source_file: Path) -> Tuple[str, List[str]]:
    """把被引用的英文 slug 注入 zh 对应标题行尾（attr_list `{#slug}`）。

    标题按位置与 source 一一配对；数量不等时报错（validate 结构对等应已拦截）。
    返回 (new_text, injections)；injections 形如 "L#12: 命令行选项 -> {#command-line-options}"。
    幂等：标题行尾已有该 {#slug} 时跳过。"""
    zh_text = zh_file.read_text(encoding="utf-8")
    source_text = source_file.read_text(encoding="utf-8")

    refs = set(_ANCHOR_REF_RE.findall(source_text))
    if not refs:
        return zh_text, []

    src_headings = [(m.group(2).strip(), m.group(1)) for m in _HEADING_RE.finditer(source_text)]
    zh_matches = list(_HEADING_RE.finditer(zh_text))
    if len(src_headings) != len(zh_matches):
        raise RuntimeError(
            f"{zh_file.name}: 标题数不一致 src={len(src_headings)} zh={len(zh_matches)}（结构对等应已拦截）")

    # slug -> 第一个匹配的 source 标题序号
    slug_index: Dict[str, int] = {}
    for i, (title, _lvl) in enumerate(src_headings):
        for slug in heading_slug_candidates(title):
            slug_index.setdefault(slug, i)

    needed: Dict[int, str] = {}
    for ref in refs:
        if ref in slug_index:
            needed.setdefault(slug_index[ref], ref)
        else:
            print(f"fix_links: 警告：引用锚点 #{ref} 在 {source_file.name} 无对应标题",
                  file=sys.stderr)

    if not needed:
        return zh_text, []

    lines = zh_text.split("\n")
    injections: List[str] = []
    for i, m in enumerate(zh_matches):
        if i not in needed:
            continue
        ref = needed[i]
        line_no = m.start()
        prefix = zh_text[:line_no].count("\n") + 1
        line = lines[prefix - 1]
        if f"{{#{ref}}}" in line:
            continue  # 幂等
        lines[prefix - 1] = line.rstrip() + f" {{#{ref}}}"
        injections.append(f"L{prefix}: {line.rstrip()} -> {{#{ref}}}")
    return "\n".join(lines), injections


def process(zh_file: Path, apply: bool, anchors: bool = False) -> List[str]:
    text = zh_file.read_text(encoding="utf-8")
    fixed, changes = fix_content(text)
    if fixed != text:
        if apply:
            zh_file.write_text(fixed, encoding="utf-8")
        return changes
    if anchors:
        source_file = SOURCE_DIR / zh_file.name
        if not source_file.exists():
            return changes
        new_text, injections = inject_anchors(zh_file, source_file)
        if injections and apply:
            zh_file.write_text(new_text, encoding="utf-8")
        return injections
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="fix_links.py",
        description="zh/ 跨目录链接映射与页内锚点注入（默认只检查）")
    parser.add_argument("--apply", action="store_true", help="原地改写 zh/ 文件")
    parser.add_argument("--check", action="store_true",
                        help="只检查不写（默认行为；显式给出以提升可读性）")
    parser.add_argument("--file", help="只处理指定 zh 文件")
    parser.add_argument("--anchors", action="store_true",
                        help="启用页内英文锚点注入（attr_list {#slug}，M5）")
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
    parent_changes = 0
    for f in targets:
        if not f.exists():
            print(f"fix_links: 文件不存在：{f}", file=sys.stderr)
            sys.exit(1)
        changes = process(f, args.apply, anchors=args.anchors)
        if changes:
            report[f.name] = changes
            all_changes.extend(changes)
            parent_changes += sum(1 for c in changes if c.startswith("../"))

    print(json.dumps({
        "ok": True,
        "apply": args.apply,
        "anchors": args.anchors,
        "scanned": len(targets),
        "files_changed": sorted(report.keys()),
        "changes": report,
        "total": len(all_changes),
    }, ensure_ascii=False, indent=2))
    # 未映射的 ../ 链接在 check 模式下即残留（apply 后不应再出现）；
    # 锚点注入仅提示，不改变退出码（M5 一次性操作，非门禁）
    if not args.apply and parent_changes:
        print(f"fix_links: 发现 {parent_changes} 处待映射跨目录链接"
              "（--apply 改写）", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
