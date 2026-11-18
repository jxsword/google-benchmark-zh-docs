"""sync_upstream 端到端单测（file:// 注入临时上游仓库；五种 diff 用例全覆盖）。

覆盖 §5.2 第 5 条：新增（A）/ 修改（M）/ 删除（D）/ 改名（R）/ 乱序（段落重排），
另含 blob sha 与 git hash-object 一致性、manifest 损坏拒绝、结构突变报错、
mark-current 成功与拒绝路径。"""

import os
import subprocess

import pytest

import sync_upstream as su
from sync_upstream import (
    SyncContext,
    compute_blob_sha,
    sync_init,
    sync_check_or_apply,
    mark_current,
)


def _run_git(repo, *args):
    env = dict(os.environ,
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def make_ctx(tmp_path):
    return SyncContext(
        source_dir=tmp_path / "source",
        zh_dir=tmp_path / "zh",
        reports_dir=tmp_path / "reports",
        manifest_file=tmp_path / "manifest.yml",
        workdir=tmp_path / "cache",
    )


def make_upstream(tmp_path, files, assets=None, subdirs=None):
    repo = tmp_path / "upstream-repo"
    (repo / "docs" / "assets").mkdir(parents=True)
    for name, content in files.items():
        (repo / "docs" / name).write_text(content, encoding="utf-8")
    for rel, content in (subdirs or {}).items():
        p = repo / "docs" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    for rel, content in (assets or {}).items():
        p = repo / "docs" / "assets" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", "init")
    return repo


FILES = {
    "a.md": "# A\n\nalpha paragraph\n\nsecond para\n",
    "b.md": "# B\n\nbeta paragraph\n",
}


def _commit_all(repo, msg):
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", msg)


def _baseline_commit(ctx):
    return (ctx.source_dir / "_upstream_commit").read_text(encoding="utf-8").strip()


def _write_zh(ctx, fname, *, status, upstream_hash=None, body="译文正文"):
    commit = _baseline_commit(ctx)
    if upstream_hash is None:
        upstream_hash = su.load_manifest(ctx.manifest_file).entry(fname)["blob_sha"]
    zh = ctx.zh_dir / fname
    zh.parent.mkdir(parents=True, exist_ok=True)
    zh.write_text(
        f"---\nupstream_file: {fname}\nupstream_commit: {commit}\n"
        f"upstream_hash: {upstream_hash}\nstatus: {status}\n---\n\n{body}\n",
        encoding="utf-8")
    return zh


# ---------- init ----------

def test_init_snapshot(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    res = sync_init(ctx, str(repo), "main", None, False)
    assert res["has_changes"]
    assert (ctx.source_dir / "a.md").read_text(encoding="utf-8") == FILES["a.md"]
    commit = _baseline_commit(ctx)
    assert len(commit) == 40
    m = su.load_manifest(ctx.manifest_file)
    assert m.baseline_commit == commit
    assert [f["file"] for f in m.files] == ["a.md", "b.md"]
    assert all(f["status"] == "missing" for f in m.files)
    assert m.entry("a.md")["paragraphs"] == 3  # heading + 2 段
    # 二次 --init 拒绝
    with pytest.raises(RuntimeError, match="已存在"):
        sync_init(ctx, str(repo), "main", None, False)


def test_init_only_file_filter(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", "a.md", False)
    m = su.load_manifest(ctx.manifest_file)
    assert [f["file"] for f in m.files] == ["a.md"]


def test_blob_sha_matches_git_hash_object(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    out = subprocess.run(["git", "hash-object", "docs/a.md"], cwd=repo,
                         capture_output=True, text=True, check=True).stdout.strip()
    assert out == compute_blob_sha(FILES["a.md"].encode("utf-8"))


def test_assets_mirror(tmp_path):
    repo = make_upstream(tmp_path, FILES,
                         assets={"images/logo.png": b"\x89PNG\r\n\x1a\n"})
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    dest = ctx.source_dir / "assets" / "images" / "logo.png"
    assert dest.read_bytes() == b"\x89PNG\r\n\x1a\n"


def test_manifest_corruption_refused(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.manifest_file.write_text("schema: v9\nfiles: []\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="损坏"):
        su.load_manifest(ctx.manifest_file)


def test_structure_mutation_subdir_md_aborts(tmp_path):
    repo = make_upstream(tmp_path, FILES, subdirs={"guide/extra.md": "# X\n"})
    ctx = make_ctx(tmp_path)
    with pytest.raises(RuntimeError, match="结构突变"):
        sync_init(ctx, str(repo), "main", None, False)


def test_structure_mutation_unknown_toplevel_file_aborts(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    (repo / "docs" / "strange.txt").write_text("?", encoding="utf-8")
    _commit_all(repo, "add stray")
    with pytest.raises(RuntimeError, match="结构突变"):
        sync_check_or_apply(ctx, str(repo), "main", None, dry_run=True, apply=False)


# ---------- 五种 diff 用例（§5.2 第 5 条） ----------

def test_no_changes_roundtrip(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=True, apply=False)
    assert res["has_changes"] is False
    assert all(c["type"] == "NONE" for c in res["changes"])


def test_modified_paragraphs_added_modified_removed(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    # 修改 1 段 + 新增 1 段（second para 保持不动）
    (repo / "docs" / "a.md").write_text(
        "# A\n\nALPHA CHANGED\n\nsecond para\n\nbrand new para\n", encoding="utf-8")
    _commit_all(repo, "edit a")
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=True, apply=False)
    assert res["has_changes"]
    ch = next(c for c in res["changes"] if c["file"] == "a.md")
    assert (ch["added"], ch["modified"], ch["removed"]) == (1, 1, 0)
    # check/dry-run 不写盘
    assert (ctx.source_dir / "a.md").read_text(encoding="utf-8") == FILES["a.md"]


def test_apply_status_stale_if_zh_else_missing(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    _write_zh(ctx, "b.md", status="partial")
    (repo / "docs" / "a.md").write_text("# A\n\nchanged alpha\n", encoding="utf-8")
    (repo / "docs" / "b.md").write_text("# B\n\nchanged beta\n", encoding="utf-8")
    _commit_all(repo, "edit both")
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=False, apply=True)
    m = su.load_manifest(ctx.manifest_file)
    assert m.entry("b.md")["status"] == "stale"    # zh 已开译
    assert m.entry("a.md")["status"] == "missing"  # 未开译
    assert (ctx.source_dir / "a.md").read_text(encoding="utf-8") == "# A\n\nchanged alpha\n"
    # init 报告 + apply 报告各一份；apply 报告对应本次 commit
    reports = list(ctx.reports_dir.glob("sync-*.md"))
    assert len(reports) == 2
    assert any(res["commit"][:8] in p.name for p in reports)
    assert res["workitems"]["b.md"]["modified"] >= 1


def test_reordered_paragraphs_produce_workitems(tmp_path):
    repo = make_upstream(tmp_path, {"o.md": "# O\n\none para\n\ntwo para\n"})
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    (repo / "docs" / "o.md").write_text("# O\n\ntwo para\n\none para\n", encoding="utf-8")
    _commit_all(repo, "reorder")
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=True, apply=False)
    wi = res["workitems"]["o.md"]
    assert wi["added"] + wi["modified"] + wi["removed"] >= 1


def test_rename_moves_zh_keeps_translation(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    _write_zh(ctx, "a.md", status="current", body="alpha 的译文")
    (repo / "docs" / "a.md").rename(repo / "docs" / "a2.md")
    _commit_all(repo, "rename a->a2")
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=False, apply=True)
    renames = [c for c in res["changes"] if c["type"] == "R"]
    assert renames and renames[0]["file"] == "a.md -> a2.md"
    assert not (ctx.zh_dir / "a.md").exists()
    zh2 = ctx.zh_dir / "a2.md"
    assert zh2.exists()
    zh_text = zh2.read_text(encoding="utf-8")
    assert "upstream_file: a2.md" in zh_text
    assert "alpha 的译文" in zh_text  # 译文保留，不重译
    m = su.load_manifest(ctx.manifest_file)
    assert m.entry("a2.md") is not None and m.entry("a.md") is None


def test_upstream_delete_flagged_for_human(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    _write_zh(ctx, "b.md", status="current")
    (repo / "docs" / "b.md").unlink()
    _commit_all(repo, "delete b")
    res = sync_check_or_apply(ctx, str(repo), "main", None, dry_run=False, apply=True)
    deletes = [c for c in res["changes"] if c["type"] == "D"]
    assert deletes and deletes[0]["action"] == "flagged-for-human"
    # source 与 zh 均保留（人工决定处置，不自动删）
    assert (ctx.source_dir / "b.md").exists()
    assert (ctx.zh_dir / "b.md").exists()
    assert su.load_manifest(ctx.manifest_file).entry("b.md") is not None


# ---------- mark-current ----------

def test_mark_current_success(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    _write_zh(ctx, "a.md", status="current")
    commit = _baseline_commit(ctx)
    mark_current(ctx, "a.md", commit)
    m = su.load_manifest(ctx.manifest_file)
    assert m.entry("a.md")["status"] == "current"


def test_mark_current_refuses_misaligned_frontmatter(tmp_path):
    repo = make_upstream(tmp_path, FILES)
    ctx = make_ctx(tmp_path)
    sync_init(ctx, str(repo), "main", None, False)
    commit = _baseline_commit(ctx)
    _write_zh(ctx, "a.md", status="current", upstream_hash="0" * 40)
    with pytest.raises(RuntimeError, match="校验失败"):
        mark_current(ctx, "a.md", commit)
    # manifest 未被改动
    assert su.load_manifest(ctx.manifest_file).entry("a.md")["status"] == "missing"
