"""fix_links 单测：../ 跨目录链接映射与相对链接保留。"""

from fix_links import fix_content


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
