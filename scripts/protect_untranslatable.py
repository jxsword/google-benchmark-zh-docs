#!/usr/bin/env python3
"""不可译内容保护：代码块/行内代码/HTML/链接 URL/占位符替换与还原校验。

移植自 fmt-zh-docs scripts/protect_untranslatable.py（2026-11-19 版），移植前过
OOM 复盘三项审查：无死循环（re.sub 单遍替换，占位符映射规模 ≤ 内容规模）、
无递归解析。本项目增补：缩进代码块保护（列表标记行豁免）、引用式链接定义保护、
check 模式（validate 门禁第 3 项：占位符集合比对）。

原理：占位符 = `{{PROTECTED_<TYPE>_<hash8>}}`，hash 由被保护内容派生 ——
source 与 zh 中相同的受保护片段会生成相同占位符，故文件级比对
protect(source) 与 protect(zh) 的占位符多重集即可验证「无丢失/无新增」
（链接文本已译不影响：LINK 模式只对 URL 部分生成占位符）。

CLI:
  --mode protect FILE            替换为占位符，stdout 输出 JSON {"protected", "map"}
  --mode check --source F --zh F 占位符多重集比对，exit 1 有缺失/多余（门禁用）
  --mode restore FILE --map F [--out F]
                                 占位符还原（批次收尾用）
  --mode roundtrip FILE          protect→restore 自测，必须与原文逐字节一致
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent.resolve()
SOURCE_DIR = REPO_ROOT / "source"
ZH_DIR = REPO_ROOT / "zh"

# 顺序敏感：大块优先（代码块 → Jinja → 注释 → HTML → 图片 → 链接 → 行内代码）。
# 注意 CODE_BLOCK 先行，fence 内的 4 空格行随块整体保护，不会落入 INDENTED_CODE。
PROTECTED_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"```[\s\S]*?```"), "CODE_BLOCK"),
    (re.compile(r"\{%[\s\S]*?%\}"), "JINJA"),            # {% raw %} 等 Jekyll 标签
    (re.compile(r"<!--[\s\S]*?-->"), "HTML_COMMENT"),    # 多行 HTML 注释
    (re.compile(r"<[^>]+>"), "HTML_TAG"),
    (re.compile(r"!\[[^\]]*\]\([^)]+\)"), "IMAGE"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), "LINK"),    # 只保护 URL，链接文本可译
    # 行内代码：1–3 个反引号游程开闭配对（CommonMark 代码跨度）。
    # 旧式 `[^`\n]+` 会把双反引号码段 ``X`` 拆开，误吞跨段文本（如 ``a`` to ``b``
    # 中的 " to "）为"行内代码"，导致还原错位与幻影码段（2026-11-19 P1-b 批次实测）
    (re.compile(r"(?<!`)(`{1,3})(?!`)[^`\n]+?(?<!`)\1(?!`)"), "INLINE_CODE"),
    # 缩进代码块（≥4 空格连续行）；列表标记豁免在 protect() 内判定
    (re.compile(r"(?m)^(?: {4,}[^\n]*\n?)+"), "INDENTED_CODE"),
    (re.compile(r"(?m)^\[[^\]]+\]:\s*\S+"), "LINK_DEF"),
]

# 缩进代码豁免判定：整块均为列表标记行 → 不是代码，保持可译
_LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")

# 占位符提取（check 模式用）
_PLACEHOLDER_RE = re.compile(r"\{\{PROTECTED_[A-Z_]+_[0-9a-f]{8}\}\}")


def generate_placeholder(seg_type: str, content: str) -> str:
    hash_suffix = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
    return f"{{{{PROTECTED_{seg_type}_{hash_suffix}}}}}"


def protect(content: str) -> Tuple[str, Dict[str, str]]:
    """把不可译内容替换为占位符，返回 (protected_content, placeholder_map)。

    顺序敏感（大块优先）；LINK 只保护 URL 部分，链接文本保留可译。"""
    placeholder_map: Dict[str, str] = {}
    protected = content

    for pattern, seg_type in PROTECTED_PATTERNS:
        if seg_type == "INDENTED_CODE":

            def _sub_indented(match: re.Match, _t: str = seg_type) -> str:
                block = match.group(0)
                content_lines = [ln for ln in block.split("\n") if ln.strip()]
                if content_lines and all(_LIST_MARKER_RE.match(ln) for ln in content_lines):
                    return block  # 列表标记行豁免：保持可译
                ph = generate_placeholder(_t, block)
                placeholder_map[ph] = block
                return ph

            protected = pattern.sub(_sub_indented, protected)
            continue

        if seg_type == "LINK":

            def _sub_link(match: re.Match) -> str:
                link_text = match.group(1)
                url = match.group(2)
                ph = generate_placeholder("URL", url)
                placeholder_map[ph] = url
                return f"[{link_text}]({ph})"

            protected = pattern.sub(_sub_link, protected)
            continue

        def _sub_default(match: re.Match, _t: str = seg_type) -> str:
            original = match.group(0)
            ph = generate_placeholder(_t, original)
            placeholder_map[ph] = original
            return ph

        protected = pattern.sub(_sub_default, protected)

    return protected, placeholder_map


def restore(protected_content: str, placeholder_map: Dict[str, str]) -> str:
    """占位符还原；映射中不存在的占位符原样保留（由 check 模式负责拦截）。

    嵌套保护必须逆序还原：容器占位符的 original 内含先生成的内层占位符，
    须先还原容器、再还原其内层（逆序 = 后生成的先还原）。"""
    restored = protected_content
    for placeholder, original in reversed(list(placeholder_map.items())):
        restored = restored.replace(placeholder, original)
    return restored


def placeholder_multiset(text: str) -> Counter:
    return Counter(_PLACEHOLDER_RE.findall(text))


def check_placeholders(source_text: str, zh_text: str) -> Tuple[bool, Dict[str, List[str]]]:
    """占位符多重集比对（validate 门禁第 3 项 + 批次中间产物校验）。

    source 一侧始终重新 protect 派生占位符。zh 一侧分两种形态：
    - 已还原终稿（不含占位符字面量）：重新过 protect，相同受保护片段派生相同
      占位符（链接文本已译不影响 —— LINK 只对 URL 生成占位符）；
    - 受保护中间产物（zh 内含占位符字面量，如批次翻译的译文稿）：直接按字面
      占位符多重集比对，不再二次 protect（二次 protect 会把 `[文本]({{占位符}})`
      重新包一层，产生假差异）。
    zh 相对 source：缺失 = 误删受保护内容；多余 = 译文自造占位符。
    返回 (ok, {"missing": [...], "extra": [...]})。"""
    src_counter = placeholder_multiset(protect(source_text)[0])
    if _PLACEHOLDER_RE.search(zh_text):
        zh_counter = placeholder_multiset(zh_text)
    else:
        zh_counter = placeholder_multiset(protect(zh_text)[0])
    missing = sorted((src_counter - zh_counter).elements())
    extra = sorted((zh_counter - src_counter).elements())
    ok = not missing and not extra
    return ok, {"missing": missing, "extra": extra}


def protect_segments(segments: List[dict]) -> List[dict]:
    """段落 dict 列表批量保护（与 fmt 版 API 兼容）。"""
    out = []
    for seg in segments:
        if seg.get("type") == "code_block":
            out.append({**seg, "protected": True})
        else:
            protected_content, placeholder_map = protect(seg.get("content", ""))
            out.append({**seg, "content": protected_content,
                        "_placeholder_map": placeholder_map})
    return out


def restore_segments(segments: List[dict]) -> List[dict]:
    """段落 dict 列表批量还原（与 fmt 版 API 兼容）。"""
    out = []
    for seg in segments:
        if "_placeholder_map" in seg:
            content = restore(seg["content"], seg["_placeholder_map"])
            out.append({k: v for k, v in seg.items() if k != "_placeholder_map"}
                       | {"content": content})
        else:
            out.append(seg)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="protect_untranslatable.py",
        description="不可译内容保护 / 占位符校验（翻译批次与 validate 门禁共用）")
    parser.add_argument("--mode", required=True,
                        choices=["protect", "check", "restore", "roundtrip"])
    parser.add_argument("file", nargs="?", help="目标 markdown 文件")
    parser.add_argument("--source", help="check 模式：source 文件")
    parser.add_argument("--zh", help="check 模式：zh 译文文件")
    parser.add_argument("--map", help="restore 模式：占位符映射 JSON 文件")
    parser.add_argument("--out", help="restore 模式：输出路径（缺省打印 stdout）")
    args = parser.parse_args(argv)

    def _read(path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    if args.mode == "protect":
        if not args.file:
            parser.error("protect 模式需要 <file>")
        protected, pmap = protect(_read(args.file))
        print(json.dumps({"protected": protected, "map": pmap}, ensure_ascii=False))

    elif args.mode == "check":
        if not (args.source and args.zh):
            parser.error("check 模式需要 --source 与 --zh")
        ok, detail = check_placeholders(_read(args.source), _read(args.zh))
        print(json.dumps({"ok": ok, **detail}, ensure_ascii=False))
        if not ok:
            sys.exit(1)

    elif args.mode == "restore":
        if not (args.file and args.map):
            parser.error("restore 模式需要 <file> 与 --map")
        loaded = json.loads(_read(args.map))
        # 兼容 --mode protect 的完整输出（{"protected": ..., "map": {...}}）
        if isinstance(loaded, dict) and set(loaded.keys()) == {"protected", "map"}:
            loaded = loaded["map"]
        restored = restore(_read(args.file), loaded)
        if args.out:
            Path(args.out).write_text(restored, encoding="utf-8")
        else:
            print(restored)

    elif args.mode == "roundtrip":
        if not args.file:
            parser.error("roundtrip 模式需要 <file>")
        original = _read(args.file)
        protected, pmap = protect(original)
        ok = restore(protected, pmap) == original
        print(json.dumps({"ok": ok, "placeholders": len(pmap)},
                         ensure_ascii=False))
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
