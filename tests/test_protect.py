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


def test_indented_code_protected_but_list_exempt():
    doc = (
        "    indented code line\n"
        "    second code line\n"
        "\n"
        "- item\n"
        "    - nested item\n"
    )
    protected, pmap = protect(doc)
    values = "\n".join(pmap.values())
    assert "indented code line" in values     # 缩进代码块被保护
    assert "nested item" not in values        # 嵌套列表标记行豁免，保持可译
    assert restore(protected, pmap) == doc


def test_link_def_protected():
    doc = "[scipy]: https://www.scipy.org\n\ntext\n"
    protected, pmap = protect(doc)
    assert "https://www.scipy.org" not in protected
    assert restore(protected, pmap) == doc


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
