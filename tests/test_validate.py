"""validate_zh 门禁单测：术语禁用扫描 / front-matter 解析 / 结构画像。"""

import validate_zh as vz


def test_glossary_forbidden_masks_allowed_terms(tmp_path):
    """合法统一译名内含禁用子串时不得误报（真实时间 ⊃ 实时）。"""
    g = tmp_path / "glossary.md"
    g.write_text(
        "| real time / wallclock | 真实时间 | 实时、挂钟时间 | |\n"
        "| run | 运行 | 跑分（benchmark 语境） | |\n",
        encoding="utf-8")
    body = "对基于真实时间的测试，这是耗时的下限。\n"
    assert vz.glossary_forbidden(g, body) == []
    body2 = "实时场景不应这样写。跑分工具亦禁止。\n"
    assert vz.glossary_forbidden(g, body2) == ["实时", "跑分"]
    # 短于 3 字的统一译名不参与屏蔽（避免过度掩蔽）
    g2 = tmp_path / "g2.md"
    g2.write_text("| run | 运行 | 跑分 | |\n", encoding="utf-8")
    assert vz.glossary_forbidden(g2, "运行测试") == []


def test_strip_front_matter():
    fm, body = vz.strip_front_matter(
        "---\nupstream_file: a.md\nstatus: partial\n---\n\n# Body\n")
    assert fm == {"upstream_file": "a.md", "status": "partial"}
    assert body.startswith("\n\n# Body")
    fm2, body2 = vz.strip_front_matter("# No front matter\n")
    assert fm2 is None and body2.startswith("# No")


def test_structure_profile_counts():
    tokens = vz.MD.parse("# T\n\npara `code` [link](a.md)\n\n```bash\nrun\n```\n\n| a |\n|---|\n| 1 |\n")
    prof = vz.structure_profile(tokens)
    assert prof["headings"] == ["h1"]
    assert prof["fences"] == ["bash"]
    assert prof["table_tr"] == 2
    assert prof["code_inline"] == 1
    assert prof["links"] == 1


def test_normalize_target_parent():
    assert vz.normalize_target("../README.md#x") == (
        "https://github.com/google/benchmark/blob/main/README.md#x")
    assert vz.normalize_target("user_guide.md") == "user_guide.md"


def test_residue_strips_urls():
    """链接续行的 URL 字母不得拉低 CJK 占比造成误报（P2-b 批次实测）。"""
    run = [(1, "参见 LLVM 项目的[基准测试"),
           (2, "技巧](https://llvm.org/docs/Benchmarking.html)）。")]
    assert vz._residue_of_run(run) == []
    # 真正的英文段落仍会被检出
    en = [(1, "The benchmark library provides a comprehensive set of testing "
              "utilities for measuring the performance of code snippets.")]
    assert vz._residue_of_run(en) != []
