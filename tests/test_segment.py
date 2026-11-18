"""segment_md 分段器单测：结构与 OOM 回归用例。"""

from sync_upstream import segment_md


def test_basic_paragraph_and_heading():
    doc = "# Title\n\nFirst paragraph.\n\n空行分隔的两个段落。\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["heading", "paragraph", "paragraph"]
    assert segs[1].section == "Title"
    assert segs[2].section == "Title"


def test_code_block_consumes_fence():
    doc = "```bash\n$ run --flag\n```\n\nAfter.\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["code_block", "paragraph"]
    assert "$ run --flag" in segs[0].content


def test_unclosed_fence_single_segment():
    # 无闭合 fence：整块收进单段；不含尾随换行的输入按真实行数计
    doc = "```bash\n$ run"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["code_block"]
    assert segs[0].line_start == 1
    assert segs[0].line_end == 2


def test_table_groups_consecutive_lines():
    doc = "| a | b |\n|---|---|\n| 1 | 2 |\n\nAfter.\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["table", "paragraph"]


def test_html_block_multiline_comment():
    doc = "<!-- {% raw %} -->\n\ntext\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["html_block", "paragraph"]


def test_html_anchor_single_line():
    doc = '<a name="x" />\n\ntext\n'
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["html_block", "paragraph"]


def test_paragraph_consumes_following_structure_line():
    # 段落后紧跟结构行（无空行分隔）：首行必被消费，结构行新起段
    doc = "text line\n# Heading\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["paragraph", "heading"]


def test_oom_regression_line_starting_lt_without_gt():
    """2026-11-18 fmt 事故触发形态：行以 < 开头且同行无 >。

    必须有界分段、非空行全部被恰一次消费、无死循环。"""
    doc = "para one\n\n< unclosed bracket line\n\npara two\n"
    segs = segment_md(doc, "t.md")
    assert [s.type for s in segs] == ["paragraph", "html_block", "paragraph"]
    assert segs[1].content == "< unclosed bracket line"
    covered = sum(s.line_end - s.line_start + 1 for s in segs)
    assert covered == 3  # 三个非空行各被恰一次消费

