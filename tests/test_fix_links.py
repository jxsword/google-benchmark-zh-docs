"""fix_links 单测：../ 跨目录链接映射、相对链接保留与页内锚点注入。"""

from pathlib import Path

from fix_links import fix_content, inject_anchors


def test_parent_link_mapped_with_anchor():
    text = "See [Custom Counters](../README.md#custom-counters) section.\n"
    fixed, changes = fix_content(text)
    assert fixed == (
        "See [Custom Counters](https://github.com/google/benchmark/blob/main/"
        "README.md#custom-counters) section.\n"
    )
    assert changes == [
        "../README.md#custom-counters -> https://github.com/google/benchmark"
        "/blob/main/README.md#custom-counters"
    ]


def test_relative_and_anchor_links_kept():
    text = "A [user guide](user_guide.md) and [section](#anchor) and [t](./tools.md).\n"
    fixed, changes = fix_content(text)
    assert fixed == text
    assert changes == []


def test_http_links_kept():
    text = "[google](https://github.com/google/benchmark)\n"
    fixed, changes = fix_content(text)
    assert fixed == text
    assert changes == []


def test_image_untouched_even_with_parent_path():
    text = "![logo](../assets/images/icon.png)\n"
    fixed, changes = fix_content(text)
    assert fixed == text
    assert changes == []


def test_multi_parent_prefix_collapsed():
    text = "[x](../../sub/page.md)\n"
    fixed, changes = fix_content(text)
    assert fixed == (
        "[x](https://github.com/google/benchmark/blob/main/sub/page.md)\n"
    )
    assert len(changes) == 1


def test_inject_anchors_positions_and_slugs(tmp_path):
    """被引用的英文 slug 按标题位置注入 zh 对应标题行尾（attr_list）。"""
    src = tmp_path / "src.md"
    zh = tmp_path / "zh.md"
    src.write_text(
        "# Guide\n\n"
        "[Options](#command-line-options) and [Formats](#output-formats).\n\n"
        "## Command Line Options\n\n"
        "text\n\n"
        "## Output Formats\n\n"
        "more\n",
        encoding="utf-8")
    zh.write_text(
        "# 指南\n\n"
        "[选项](#command-line-options)与[格式](#output-formats)。\n\n"
        "## 命令行选项\n\n"
        "正文\n\n"
        "## 输出格式\n\n"
        "更多\n",
        encoding="utf-8")
    new_text, injections = inject_anchors(zh, src)
    assert "## 命令行选项 {#command-line-options}" in new_text
    assert "## 输出格式 {#output-formats}" in new_text
    assert len(injections) == 2
    # 未被引用的标题不注入
    assert "# 指南 {" not in new_text


def test_inject_anchors_idempotent(tmp_path):
    src = tmp_path / "src.md"
    zh = tmp_path / "zh.md"
    src.write_text("[x](#sec-one)\n\n## Sec One\n", encoding="utf-8")
    zh.write_text("[x](#sec-one)\n\n## 第一节 {#sec-one}\n", encoding="utf-8")
    new_text, injections = inject_anchors(zh, src)
    assert new_text.count("{#sec-one}") == 1
    assert injections == []


def test_inject_anchors_heading_count_mismatch_aborts(tmp_path):
    src = tmp_path / "src.md"
    zh = tmp_path / "zh.md"
    src.write_text("[x](#a)\n\n## A\n\n## B\n", encoding="utf-8")
    zh.write_text("[x](#a)\n\n## 甲\n", encoding="utf-8")
    try:
        inject_anchors(zh, src)
        assert False, "应当报错"
    except RuntimeError as e:
        assert "标题数不一致" in str(e)


def test_slugify_variants():
    from fix_links import heading_slug_candidates
    assert "command-line-options" in heading_slug_candidates("Command Line Options")
    # KeepRunning 无空格：两种 slugify 均为 keeprunning
    assert "a-faster-keeprunning-loop" in heading_slug_candidates(
        "A Faster KeepRunning Loop")
