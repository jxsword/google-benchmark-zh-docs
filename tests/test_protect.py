"""protect_untranslatable 单测：roundtrip / 嵌套保护还原回归 / check 门禁。"""

from protect_untranslatable import protect, restore, check_placeholders


def test_roundtrip_basic():
    doc = (
        "# Title\n\n"
        "Use `benchmark::State` here.\n\n"
        "```cpp\n"
        "auto* b = Benchmark();\n"
        "```\n\n"
        "See [docs](https://github.com/google/benchmark) for details.\n"
    )
    protected, pmap = protect(doc)
    assert restore(protected, pmap) == doc


def test_nested_protection_restore_order():
    """嵌套保护（行内代码内含尖括号）必须逆序还原。

    user_guide.md 实际形态：`--benchmark_min_time=<seconds>`（2026-11-19
    roundtrip 冒烟发现并修复的回归）。"""
    doc = "The flag `--benchmark_min_time=<seconds>` (BENCHMARK_MIN_TIME).\n"
    protected, pmap = protect(doc)
    assert restore(protected, pmap) == doc


def test_double_backtick_code_span():
    """CommonMark 双反引号码段必须整体保护，不吞噬跨段文本。

    回归：user_guide.md L1197-1198 ``BM_UserCounter`` to ``BM_Factorial``
    旧正则把 " to " 等跨段文本误配为行内代码（2026-11-19 P1-b 批次实测）。"""
    doc = "changes from ``BM_UserCounter`` to ``BM_Factorial`` here.\n"
    protected, pmap = protect(doc)
    assert "``BM_UserCounter``" in pmap.values()
    assert "``BM_Factorial``" in pmap.values()
    assert " to " not in pmap.values()
    assert restore(protected, pmap) == doc


def test_single_backtick_still_works():
    doc = "use `--benchmark_filter` and `x` plus `y` now\n"
    protected, pmap = protect(doc)
    assert restore(protected, pmap) == doc
    assert pmap and all(v.startswith("`") for v in pmap.values())


def test_link_url_only_protected():
    doc = "See [the user guide](user_guide.md) for details.\n"
    protected, pmap = protect(doc)
    assert "[the user guide](" in protected   # 链接文本保留可译
    assert "user_guide.md)]" not in protected  # URL 已被占位符替换
    assert restore(protected, pmap) == doc


def test_image_fully_protected():
    doc = "![logo](assets/images/icon.png)\n"
    protected, pmap = protect(doc)
    assert list(pmap.values()) == ["![logo](assets/images/icon.png)"]
    assert restore(protected, pmap) == doc


def test_indented_prose_not_protected():
    """列表项正文续行（4–5 空格缩进）不得被误保护为代码（P2-a 实测回归）。

    tools.md 的编号列表续行是正文；语料实测零独立缩进代码块，故不设
    INDENTED_CODE 模式。"""
    doc = (
        "1. **Benchmark:** The name of the function, along with the\n"
        "     size of the input (after the slash).\n"
        "2. **Time:** The average time per operation.\n"
    )
    protected, pmap = protect(doc)
    assert "size of the input" not in "".join(pmap.values())
    assert restore(protected, pmap) == doc


def test_link_def_protected():
    doc = "[scipy]: https://www.scipy.org\n\ntext\n"
    protected, pmap = protect(doc)
    assert "https://www.scipy.org" not in protected
    assert restore(protected, pmap) == doc


def test_check_ignores_url_tokens_mapped_by_fix_links():
    """../ 跨目录链接经 fix_links 映射为绝对 URL 后，URL 占位符不参与比对。

    回归：URL 内容哈希随映射改变，占位符比对若不排除 URL 类 token 会与
    validate 第 4 项（链接归一比对）互相矛盾（2026-11-19 P3 批次实测）。"""
    src = "See [User Counters](../README.md#custom-counters) and `keep()`.\n"
    zh = "参见[用户计数器](https://github.com/google/benchmark/blob/main/README.md#custom-counters)与 `keep()`。\n"
    ok, detail = check_placeholders(src, zh)
    assert ok, detail


def test_check_placeholders_gate():
    src = "Use `foo()` and [link](https://example.com/a) here.\n"
    ok, detail = check_placeholders(src, src)
    assert ok and detail == {"missing": [], "extra": []}

    # 译文已翻译链接文本：URL 占位符不变 → 仍 ok
    translated = "使用 `foo()` 与[链接](https://example.com/a)。\n"
    ok, detail = check_placeholders(src, translated)
    assert ok and detail == {"missing": [], "extra": []}

    # 误删行内代码 → missing
    ok, detail = check_placeholders(src, "使用  与[链接](https://example.com/a)。\n")
    assert not ok and detail["missing"] and not detail["extra"]

    # 译文自造占位符 → extra
    invented = "使用 `foo()` 与[链接](https://example.com/a)。" \
               "{{PROTECTED_CODE_BLOCK_00000000}}\n"
    ok, detail = check_placeholders(src, invented)
    assert not ok and detail["extra"]


def test_check_placeholders_protected_intermediate():
    """受保护中间产物（译文含占位符字面量）按字面比对，不二次 protect。

    回归：`[文本]({{PROTECTED_URL_xxx}})` 若被二次 protect，链接模式会把
    占位符重新包一层产生假差异（2026-11-19 P1-a 批次实测发现）。"""
    src = "See [the guide](user_guide.md) and `flags`.\n"
    protected, pmap = protect(src)
    assert "[the guide]({{" in protected and "{{PROTECTED_INLINE_CODE_" in protected
    translated = protected.replace("[the guide]", "[用户指南]")
    ok, detail = check_placeholders(src, translated)
    assert ok, detail
    assert detail == {"missing": [], "extra": []}
