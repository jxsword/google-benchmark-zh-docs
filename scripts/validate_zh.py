#!/usr/bin/env python3
"""译文质量门禁聚合（PLAN §7 第 1–7 项；第 8 项 mkdocs 冒烟在 validate_zh.sh --smoke）。

检查项（per file，status=missing 的文件跳过）:
  1. front-matter schema 与 manifest 一致性（error）
  2. markdown 结构对等：标题层级序列 / 代码块 fence 序列 / 表格行列 / 列表项数 /
     链接 / 图片 / 行内代码 / html 块 / 引用块计数（error）
  3. 占位符完整性：protect(source) 与 protect(zh) 占位符多重集比对（error）
  4. 链接 URL 集合一致：source 目标经 ../ 映射归一后与 zh 多重集相等；
     zh 残留 `](../` 未映射链接（error）
  5. 术语扫描：glossary.md「禁用译名」列在 zh 正文（代码外）零出现（error）
  6. 未翻译残留启发式 + TODO/FIXME 标记（warning）
  7. 排版：行尾空格 / 全角空格 / 中英文间距（warning）

CLI:
  --file NAME   只校验指定文件（manifest 中的文件名）
  --root DIR    项目根覆盖（测试隔离）
  退出码: 0 无 error；1 有 error；2 用法/环境错误。
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from markdown_it import MarkdownIt

REPO_ROOT = Path(__file__).parent.parent.resolve()

MD = MarkdownIt("default")

FM_KEYS = ("upstream_file", "upstream_commit", "upstream_hash", "status", "generated_by")
STATUSES = {"current", "stale", "partial", "missing"}

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")
_TRAILING_WS_RE = re.compile(r"[ \t]+$")
# 中英相邻（无空格）：汉字紧邻 ASCII 字母/数字
_ADJACENCY_RE = re.compile(r"([\u4e00-\u9fff][A-Za-z0-9])|([A-Za-z0-9][\u4e00-\u9fff])")


def strip_front_matter(text: str) -> Tuple[Optional[Dict], str]:
    """返回 (front_matter_dict_or_None, body)。"""
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None, text
    return fm, parts[2]


def strip_code(body: str) -> str:
    """去掉围栏代码块与行内代码，供排版/术语/残留扫描（避免代码内容误报）。"""
    body = re.sub(r"```[\s\S]*?```", "", body)
    body = re.sub(r"`[^`\n]*`", "", body)
    return body


def walk(tokens):
    for t in tokens:
        yield t
        if t.children:
            yield from walk(t.children)


def structure_profile(tokens) -> Dict:
    """§7 第 2 项的结构画像。"""
    prof: Dict = {}
    prof["headings"] = [t.tag for t in tokens if t.type == "heading_open"]
    prof["fences"] = [
        (t.info.strip().split()[0] if t.info and t.info.strip() else "")
        for t in tokens if t.type == "fence"
    ]
    prof["table_tr"] = sum(1 for t in tokens if t.type == "tr_open")
    prof["table_cells"] = sum(1 for t in tokens if t.type in ("th_open", "td_open"))
    prof["list_items"] = sum(1 for t in tokens if t.type == "list_item_open")
    prof["blockquotes"] = sum(1 for t in tokens if t.type == "blockquote_open")
    prof["html_blocks"] = sum(1 for t in tokens if t.type == "html_block")
    inline_counts = Counter()
    for t in walk(tokens):
        if t.type in ("link_open", "image", "code_inline", "html_inline"):
            inline_counts[t.type] += 1
    prof["links"] = inline_counts["link_open"]
    prof["images"] = inline_counts["image"]
    prof["code_inline"] = inline_counts["code_inline"]
    prof["html_inline"] = inline_counts["html_inline"]
    return prof


def structure_diffs(src_prof: Dict, zh_prof: Dict) -> List[str]:
    diffs = []
    if src_prof["headings"] != zh_prof["headings"]:
        diffs.append(f"标题层级序列不一致: src={src_prof['headings']} zh={zh_prof['headings']}")
    if src_prof["fences"] != zh_prof["fences"]:
        diffs.append(f"代码块 fence 序列不一致: src={src_prof['fences']} zh={zh_prof['fences']}")
    for key in ("table_tr", "table_cells", "list_items", "blockquotes",
                "html_blocks", "links", "images", "code_inline", "html_inline"):
        if src_prof[key] != zh_prof[key]:
            diffs.append(f"{key} 不一致: src={src_prof[key]} zh={zh_prof[key]}")
    return diffs


def link_targets(tokens) -> List[str]:
    out = []
    for t in walk(tokens):
        if t.type == "link_open":
            out.append(str(t.attrs.get("href", "")))
        elif t.type == "image":
            out.append(str(t.attrs.get("src", "")))
    return out


def normalize_target(target: str) -> str:
    """source 目标归一：../ 前缀映射为上游 GitHub blob URL（与 fix_links 同规则）。"""
    from fix_links import UPSTREAM_BLOB_URL, _PARENT_RE
    if _PARENT_RE.match(target):
        return f"{UPSTREAM_BLOB_URL}/{_PARENT_RE.sub('', target)}"
    return target


# ---------- §7 第 6/7 项扫描器 ----------

def residue_warnings(body: str) -> List[str]:
    """未翻译残留启发式：长英文段（CJK 占比 < 0.15）+ TODO/FIXME。"""
    warns = []
    in_fence = False
    paragraph: List[str] = []
    for line_no, line in enumerate(body.split("\n"), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            paragraph = []
            continue
        if in_fence:
            continue
        if line.strip():
            paragraph.append((line_no, line))
        else:
            if paragraph:
                warns.extend(_residue_of_run(paragraph))
                paragraph = []
    if paragraph:
        warns.extend(_residue_of_run(paragraph))
    for line_no, line in enumerate(body.split("\n"), start=1):
        if _TODO_RE.search(line):
            warns.append(f"第 {line_no} 行: TODO/FIXME 标记残留")
    return warns


def _residue_of_run(paragraph: List[Tuple[int, str]]) -> List[str]:
    text = " ".join(line for _, line in paragraph)
    stripped = strip_code(text)
    cjk = len(_CJK_RE.findall(stripped))
    ascii_letters = sum(ch.isascii() and ch.isalpha() for ch in stripped)
    if cjk + ascii_letters < 40:
        return []
    if cjk == 0 or (cjk / (cjk + ascii_letters)) < 0.15:
        first = paragraph[0][0]
        return [f"第 {first} 行起: 疑似未翻译英文段落（CJK 占比过低）"]
    return []


def typography_warnings(body: str) -> List[str]:
    """排版：行尾空格 / 全角空格 / 中英文间距（代码内容剔除后扫描）。"""
    warns = []
    in_fence = False
    for line_no, line in enumerate(body.split("\n"), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _TRAILING_WS_RE.search(line):
            warns.append(f"第 {line_no} 行: 行尾空格")
        if "\u3000" in line:
            warns.append(f"第 {line_no} 行: 全角空格（U+3000）")
        scanned = strip_code(line)
        if _ADJACENCY_RE.search(scanned):
            warns.append(f"第 {line_no} 行: 中英文之间缺空格")
    return warns


def glossary_forbidden(glossary_path: Path, body_stripped: str) -> List[str]:
    """§7 第 5 项：glossary「禁用译名」列在正文（代码外）零出现。"""
    if not glossary_path.exists():
        return []
    forbidden: List[str] = []
    for raw in glossary_path.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("英文", "---", ""):
            continue
        if cells[0].startswith("-"):
            continue
        for term in cells[2].split("、"):
            term = re.sub(r"（[^）]*）", "", term).strip()
            if term and term not in ("—", "— （", ""):
                forbidden.append(term)
    hits = []
    for term in sorted(set(forbidden)):
        if term in body_stripped:
            hits.append(term)
    return hits


# ---------- 单文件校验 ----------

def validate_file(root: Path, fname: str, glossary_path: Path) -> Dict:
    """返回 {"file", "errors", "warnings", "skipped"}。"""
    errors: List[str] = []
    warns: List[str] = []
    source_dir = root / "source"
    zh_dir = root / "zh"
    manifest_file = root / "manifest.yml"

    m = None
    if manifest_file.exists():
        data = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
        entries = {f["file"]: f for f in (data or {}).get("files", [])}
        m = entries.get(fname)

    zh_file = zh_dir / fname
    if not zh_file.exists():
        return {"file": fname, "errors": [], "warnings": [], "skipped": "未开译"}
    text = zh_file.read_text(encoding="utf-8")
    fm, body = strip_front_matter(text)

    # 1. front-matter schema 与 manifest 一致性
    if fm is None:
        errors.append("缺 front-matter")
        fm = {}
    for key in FM_KEYS:
        if key not in fm:
            errors.append(f"front-matter 缺字段 {key}")
    if fm.get("status") not in STATUSES:
        errors.append(f"front-matter status 非法: {fm.get('status')!r}")
    if fm.get("generated_by") not in ("agent", "human"):
        errors.append(f"front-matter generated_by 非法: {fm.get('generated_by')!r}")
    if m is not None:
        if fm.get("upstream_file") not in (None, fname):
            errors.append(f"front-matter upstream_file={fm.get('upstream_file')!r} 与文件名不符")
        if m["status"] == "current":
            if fm.get("upstream_hash") != m["blob_sha"]:
                errors.append("front-matter upstream_hash 与 manifest blob_sha 不一致"
                              "（manifest 已标记 current）")
            up_commit = (source_dir / "_upstream_commit").read_text(encoding="utf-8").strip()
            if fm.get("upstream_commit") != up_commit:
                errors.append("front-matter upstream_commit 与 source/_upstream_commit 不一致")
        if fm.get("status") != m["status"] and m["status"] != "missing":
            warns.append(f"front-matter status={fm.get('status')!r} 与 manifest "
                         f"status={m['status']!r} 不一致（批次收尾跑 mark-current 对齐）")
    elif fm.get("upstream_file") != fname:
        errors.append(f"front-matter upstream_file={fm.get('upstream_file')!r} 与文件名不符")

    src_file = source_dir / fname
    if not src_file.exists():
        errors.append(f"source/{fname} 不存在（快照缺失）")
        return {"file": fname, "errors": errors, "warnings": warns, "skipped": None}

    src_tokens = MD.parse(src_file.read_text(encoding="utf-8"))
    zh_tokens = MD.parse(body)

    # 2. 结构对等
    for d in structure_diffs(structure_profile(src_tokens),
                             structure_profile(zh_tokens)):
        errors.append(f"结构对等失败: {d}")

    # 3. 占位符完整性（两边都重新 protect）
    from protect_untranslatable import check_placeholders
    ok, detail = check_placeholders(
        src_file.read_text(encoding="utf-8"), body)
    if not ok:
        for ph in detail["missing"]:
            errors.append(f"占位符缺失（受保护内容被删）: {ph}")
        for ph in detail["extra"]:
            errors.append(f"多余占位符: {ph}")

    # 4. 链接 URL 集合一致 + ../ 残留
    src_targets = Counter(normalize_target(t) for t in link_targets(src_tokens))
    zh_targets = Counter(link_targets(zh_tokens))
    if src_targets != zh_targets:
        missing = src_targets - zh_targets
        extra = zh_targets - src_targets
        if missing:
            errors.append(f"链接目标缺失: {sorted(missing.elements())}")
        if extra:
            errors.append(f"链接目标多余: {sorted(extra.elements())}")

    body_stripped = strip_code(body)

    # 5. 术语禁用译名
    for term in glossary_forbidden(glossary_path, body_stripped):
        errors.append(f"禁用译名出现: {term}")

    # 6. 未翻译残留（warning）
    warns.extend(residue_warnings(body))

    # 7. 排版（warning）
    warns.extend(typography_warnings(body))

    return {"file": fname, "errors": errors, "warnings": warns, "skipped": None}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="validate_zh.py",
        description="译文质量门禁聚合（PLAN §7 第 1–7 项）")
    parser.add_argument("--file", help="只校验指定文件（manifest 中的文件名）")
    parser.add_argument("--root", default=str(REPO_ROOT), help="项目根覆盖（测试隔离）")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    manifest_file = root / "manifest.yml"
    if not manifest_file.exists():
        print(json.dumps({"ok": True, "files": 0, "note": "manifest 不存在，无可校验项"},
                         ensure_ascii=False))
        return 0

    data = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
    names = [f["file"] for f in (data or {}).get("files", [])]
    if args.file:
        if args.file not in names:
            print(f"validate_zh: {args.file} 不在 manifest 中", file=sys.stderr)
            return 2
        names = [args.file]

    results = [validate_file(root, n, root / "glossary.md") for n in sorted(names)]
    total_errors = sum(len(r["errors"]) for r in results)
    total_warns = sum(len(r["warnings"]) for r in results)
    print(json.dumps({
        "ok": total_errors == 0,
        "files": len(results),
        "skipped": [r["file"] for r in results if r["skipped"]],
        "errors": {r["file"]: r["errors"] for r in results if r["errors"]},
        "warnings": {r["file"]: r["warnings"] for r in results if r["warnings"]},
    }, ensure_ascii=False, indent=2))
    if total_errors:
        print(f"validate_zh: {total_errors} error / {total_warns} warning",
              file=sys.stderr)
        return 1
    print(f"validate_zh: OK（0 error / {total_warns} warning）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
