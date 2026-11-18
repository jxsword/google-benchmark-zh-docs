#!/usr/bin/env python3
"""上游 google/benchmark docs/ 同步脚本（blob sha 检测 + 段落级 diff + manifest 状态机）。

决策依据：DR-002（段落 hash + manifest 状态机）、DR-001（source/ 快照 + zh/ 同名译文）。
安全纪律：PLAN §5.2 六条 ——
  1. 运行强制 memgate 包裹：`memgate 2048 python3 scripts/sync_upstream.py …`
  2. 输入规模硬上限：单文件 >2MB 或总解析段数 >50k 直接报错退出
  3. 逐文件分段，不把全仓库 AST/段列表同时驻留内存；对齐用 difflib 逐文件 O(n·m)
  4. --dry-run 只打印不写盘；--file 单文件调试
  5. tests/ 覆盖 新增/修改/删除/改名/乱序 五种 diff 用例
  6. 移植自 fmt-zh-docs sync_docs.py，移植前已过 OOM 复盘三项审查
     （死循环护栏 `if i == start: i += 1` 保留；无界列表加段数上限；无递归解析）
     —— 2026-11-18 fmt sync_docs.py OOM 事故复盘见 fmt 仓 docs/incident-2026-11-18-oom.md

manifest.yml 只能由本脚本读写（人工直改视为账本损坏，validate 门禁报错）。

CLI:
  --init                  首次快照：写 source/（md + assets）、_upstream_commit、
                          manifest 全量 missing，产出同步报告
  --check                 只检测：文件级 blob sha 比对，打印变更摘要，不写盘
  --apply                 应用变更：更新 source/、manifest（stale/missing）、
                          段落级工作项 diff，产出 reports/sync-<date>-<sha>.md
  --mark-current FILE     校验 zh/<file> front-matter 与 manifest 对齐后，把该文件标记 current
  --dry-run               与 --init/--apply 组合：只打印工作项不写盘
  --file NAME             只处理指定文件（调试）
  --repo URL              覆盖上游仓库地址（测试注入本地 file:// 仓库）
  --workdir DIR           覆盖克隆缓存目录（测试隔离）
  --ref REF               上游分支/标签（默认 main）

状态机：current（译文与上游对齐）| stale（上游已变，待修订）| partial（批次进行中）|
        missing（未开译）。partial 只由翻译批次经 --mark-current 流转，sync 不产生。
"""

import argparse
import difflib
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.resolve()
SOURCE_DIR = REPO_ROOT / "source"
ZH_DIR = REPO_ROOT / "zh"
REPORTS_DIR = REPO_ROOT / "reports"
MANIFEST_FILE = REPO_ROOT / "manifest.yml"

UPSTREAM_REPO = "https://github.com/google/benchmark"
UPSTREAM_DOC = "docs"
UPSTREAM_ASSETS = "assets"
DEFAULT_REF = "main"
UPSTREAM_BLOB_URL = "https://github.com/google/benchmark/blob/main"

# PLAN §5.2 第 2 条：规模硬上限（正常上游 12 文件共 ~110KB，永远触不到）
MAX_FILE_BYTES = 2 * 1024 * 1024       # 单文件 2MB
MAX_TOTAL_SEGMENTS = 50_000            # 全库总段数

# 上游 docs/ 顶层已知非 md 文件（白名单：跳过不入库）；出现其他新文件 → 报错停下
KNOWN_NON_MD = {"_config.yml"}

MANIFEST_SCHEMA_VERSION = "v1"

SYNC_CONTEXT = None  # 测试注入用（SyncContext 实例覆盖目录常量）


@dataclass
class SyncContext:
    """目录注入：生产用模块常量，测试注入 tmp_path 隔离目录。"""
    source_dir: Path
    zh_dir: Path
    reports_dir: Path
    manifest_file: Path
    workdir: Path


@dataclass
class Segment:
    """段落：行扫描分段结果，hash 供段落级对齐。"""
    index: int
    type: str            # heading / paragraph / code_block / table / html_block / image
    content: str
    hash: str            # sha256(content)[:16]
    line_start: int      # 1-based
    line_end: int        # 1-based, inclusive
    section: str         # 所属最近一级标题


@dataclass
class FileChange:
    """单文件变更工作项。"""
    file: str
    type: str            # A / M / D / R / NONE
    old_blob: str = ""
    new_blob: str = ""
    added: int = 0
    modified: int = 0
    removed: int = 0
    action: str = ""     # applied / would-apply / detected / archived-none


@dataclass
class Manifest:
    schema: str
    remote: str
    baseline_commit: str
    snapshot_date: str
    files: List[Dict] = field(default_factory=list)

    def entry(self, fname: str) -> Optional[Dict]:
        for f in self.files:
            if f["file"] == fname:
                return f
        return None


# ---------- 基础工具 ----------

def compute_hash(content: str) -> str:
    """段落 hash（sha256 前 16 位）。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def compute_blob_sha(data: bytes) -> str:
    """git blob sha1（与 `git hash-object` 等价），文件级变更检测依据（§5.4）。

    注意：此处 sha1 是 git 对象 ID 的规范格式（必须与 git/GitHub blob sha 逐字节
    一致方可比对），仅作内容标识符，非安全原语；段落 hash 用 sha256（见 compute_hash）。"""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _git(args: List[str], cwd: Optional[Path] = None) -> str:
    """git 子进程：一律参数列表，不用 shell 拼接。"""
    result = subprocess.run(["git", *args], cwd=cwd, check=True,
                            capture_output=True, text=True)
    return result.stdout


def _safe_join(base: Path, rel: str) -> Path:
    """resolve 后校验仍位于 base 内，防路径逃逸。"""
    base = base.resolve()
    p = (base / rel).resolve()
    if not p.is_relative_to(base):
        raise ValueError(f"path escapes {base}: {rel}")
    return p


def get_ctx() -> SyncContext:
    global SYNC_CONTEXT
    if SYNC_CONTEXT is not None:
        return SYNC_CONTEXT
    # 上游克隆缓存放仓库外（~/.cache，GBZD_UPSTREAM_CACHE 可覆盖）：缓存内容是
    # 第三方源码克隆，不入库；仓库外存放避免安全扫描/工具状态污染项目目录
    # （对 PLAN §5.4「workdir/upstream」的位置调整，意图不变：缓存不进版本库）
    cache_root = Path(os.environ.get(
        "GBZD_UPSTREAM_CACHE", str(Path.home() / ".cache" / "google-benchmark-zh-docs")))
    return SyncContext(
        source_dir=SOURCE_DIR, zh_dir=ZH_DIR, reports_dir=REPORTS_DIR,
        manifest_file=MANIFEST_FILE, workdir=cache_root / "upstream",
    )


# ---------- 上游克隆缓存（§5.4：workdir/upstream，depth-1，不依赖 raw API） ----------

def prepare_upstream(repo_url: str, workdir: Path, ref: str) -> str:
    """确保 workdir 缓存最新并检出 ref，返回 HEAD SHA。

    已有缓存 → fetch --depth 1 更新；无缓存 → clone --depth 1 --single-branch。"""
    if workdir.exists() and (workdir / ".git").exists():
        _git(["fetch", "--depth", "1", "origin", ref], cwd=workdir)
        _git(["checkout", "FETCH_HEAD"], cwd=workdir)
    else:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.parent.mkdir(parents=True, exist_ok=True)
        _git(["clone", "--depth", "1", "--single-branch", "--branch", ref,
              repo_url, str(workdir)])
    return _git(["rev-parse", "HEAD"], cwd=workdir).strip()


def read_upstream_md(doc_dir: Path) -> Dict[str, bytes]:
    """读取上游 docs/ 顶层 md 文件；结构突变（md 进子目录 / 未知新文件）报错停下。"""
    if not doc_dir.is_dir():
        raise RuntimeError(f"upstream docs dir not found: {doc_dir}")
    files: Dict[str, bytes] = {}
    for p in sorted(doc_dir.iterdir()):
        rel = p.name
        if p.is_dir():
            if rel == UPSTREAM_ASSETS:
                continue  # assets 递归镜像，单独处理
            raise RuntimeError(
                f"结构突变：上游 docs/ 出现新子目录 {rel}/（PLAN §11：报错停下，人工介入）")
        if p.suffix == ".md":
            files[rel] = p.read_bytes()
        elif rel in KNOWN_NON_MD:
            logger.info("跳过上游配置文件 %s（中文站不复用，DR-003）", rel)
        else:
            raise RuntimeError(
                f"结构突变：上游 docs/ 出现未知顶层文件 {rel}（PLAN §11：报错停下，人工介入）")
    if not files:
        raise RuntimeError("upstream docs/ 无 md 文件")
    return files


def mirror_assets(doc_dir: Path, source_dir: Path) -> List[str]:
    """docs/assets/ 递归镜像进 source/assets/（§5.4），返回镜像文件相对路径列表。"""
    src_assets = doc_dir / UPSTREAM_ASSETS
    if not src_assets.is_dir():
        return []
    mirrored = []
    for p in sorted(src_assets.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src_assets)
        dest = _safe_join(source_dir / UPSTREAM_ASSETS, str(rel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        mirrored.append(f"{UPSTREAM_ASSETS}/{rel.as_posix()}")
    return mirrored


# ---------- 段落分段（fmt 加固版移植） ----------

def segment_md(content: str, fname: str) -> List[Segment]:
    """行扫描分段：heading / paragraph / code_block / table / html_block / image。

    加固要点（2026-11-18 OOM 复盘）：
    - 段落分支末尾 `if i == start: i += 1` 防死循环护栏（任何未推进情形强制前进）；
    - html 分支消费到空行（跨行注释 <!-- ... 整块捕获）；
    - 首行必被内层循环消费（`i > start` 才允许 break），残缺行不产生空段。"""
    segs: List[Segment] = []
    lines = content.split("\n")
    i = 0
    seg_idx = 0
    cur_sec = ""
    while i < len(lines):
        line = lines[i]
        st = line.strip()
        if st.startswith("```"):
            start = i
            fence = st[:3]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                i += 1
            if i < len(lines):
                i += 1  # 消费闭合 fence
            code = "\n".join(lines[start:i])
            segs.append(Segment(seg_idx, "code_block", code, compute_hash(code),
                                start + 1, i, cur_sec))
        elif st.startswith("|") and "|" in st[1:]:
            start = i
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
            tbl = "\n".join(lines[start:i])
            segs.append(Segment(seg_idx, "table", tbl, compute_hash(tbl),
                                start + 1, i, cur_sec))
        elif st.startswith("#"):
            level = len(st) - len(st.lstrip("#"))
            title = st.lstrip("#").strip()
            segs.append(Segment(seg_idx, "heading", line, compute_hash(line),
                                i + 1, i + 1, cur_sec))
            cur_sec = title
            i += 1
        elif st.startswith("![") and "](" in st:
            segs.append(Segment(seg_idx, "image", line, compute_hash(line),
                                i + 1, i + 1, cur_sec))
            i += 1
        elif st.startswith("<"):
            # HTML 块 / 跨行注释（<!-- ... --> 可跨多行，'>' 未必在首行）
            start = i
            while i < len(lines) and lines[i].strip() != "":
                i += 1
            html = "\n".join(lines[start:i])
            segs.append(Segment(seg_idx, "html_block", html, compute_hash(html),
                                start + 1, i, cur_sec))
        elif st:
            start = i
            paras: List[str] = []
            while i < len(lines) and lines[i].strip() != "":
                ls = lines[i].strip()
                if i > start and (ls.startswith("#") or ls.startswith("```")
                                  or (ls.startswith("|") and "|" in ls[1:])
                                  or ls.startswith("![") or ls.startswith("<")):
                    break
                paras.append(lines[i])
                i += 1
            p = "\n".join(paras)
            segs.append(Segment(seg_idx, "paragraph", p, compute_hash(p),
                                start + 1, i, cur_sec))
            if i == start:
                # 防死循环护栏：内层循环未推进时强制前进一行
                # （2026-11-18 OOM 事故根因，缺此行会无限生成空段）
                i += 1
        else:
            i += 1
        seg_idx += 1
        if len(segs) > MAX_TOTAL_SEGMENTS:
            raise RuntimeError(
                f"{fname}: 段数超过硬上限 {MAX_TOTAL_SEGMENTS}（PLAN §5.2 第 2 条，报错退出）")
    return segs


def diff_paragraphs(old_segs: List[Segment],
                    new_segs: List[Segment]) -> List[Tuple[str, List[Segment], List[Segment]]]:
    """段落 hash 序列 difflib 对齐（等价 LCS），产出三类工作项。

    返回 [(tag, old_slice, new_slice)]，tag ∈ {insert(新增), replace(修改,复译),
    delete(删除)}。不做模糊匹配：hash 不等即不同段（宁多译不误译，§5.4）。"""
    if not old_segs and not new_segs:
        return []
    sm = difflib.SequenceMatcher(a=[s.hash for s in old_segs],
                                 b=[s.hash for s in new_segs], autojunk=False)
    work = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        work.append((tag, old_segs[i1:i2], new_segs[j1:j2]))
    return work


# ---------- manifest（脚本独占读写，纪律 2） ----------

def load_manifest(path: Path) -> Optional[Manifest]:
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != MANIFEST_SCHEMA_VERSION:
        raise RuntimeError(
            f"manifest.yml schema 异常（期望 {MANIFEST_SCHEMA_VERSION}）——账本疑似损坏，停止")
    files = data.get("files")
    if files is None:
        raise RuntimeError("manifest.yml 缺 files 节——账本疑似损坏，停止")
    return Manifest(
        schema=data["schema"],
        remote=data.get("upstream", {}).get("remote", UPSTREAM_REPO),
        baseline_commit=data.get("upstream", {}).get("baseline_commit", ""),
        snapshot_date=data.get("upstream", {}).get("snapshot_date", ""),
        files=files,
    )


def save_manifest(path: Path, m: Manifest):
    data = {
        "schema": m.schema,
        "upstream": {
            "remote": m.remote,
            "baseline_commit": m.baseline_commit,
            "snapshot_date": m.snapshot_date,
        },
        "files": m.files,
    }
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")


def front_matter_of(zh_file: Path) -> Optional[Dict]:
    """读取 zh 文件 YAML front-matter；无 front-matter 返回 None。"""
    if not zh_file.exists():
        return None
    text = zh_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return None
    return yaml.safe_load(parts[0][3:]) or {}


# ---------- 核心流程 ----------

def scan_workitems(old_segs: List[Segment], new_segs: List[Segment]) -> Dict[str, int]:
    counts = {"added": 0, "modified": 0, "removed": 0}
    for tag, olds, news in diff_paragraphs(old_segs, new_segs):
        if tag == "insert":
            counts["added"] += len(news)
        elif tag == "delete":
            counts["removed"] += len(olds)
        elif tag == "replace":
            counts["modified"] += max(len(olds), len(news))
    return counts


def sync_init(ctx: SyncContext, repo_url: str, ref: str,
              only_file: Optional[str], dry_run: bool) -> Dict:
    """首次快照：source/ + _upstream_commit + manifest 全量 missing。"""
    if ctx.manifest_file.exists():
        raise RuntimeError("manifest.yml 已存在；首次快照只应执行一次。"
                           "后续同步用 --check / --apply。")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "upstream-tmp"
        # 复用/重建 workdir 缓存再拷贝 checkout 内容，避免临时区重复下载
        sha = prepare_upstream(repo_url, ctx.workdir, ref)
        doc_dir = ctx.workdir / UPSTREAM_DOC
        files = read_upstream_md(doc_dir)
        logger.info("上游文件（%d 个 md）：", len(files))
        for name in files:
            logger.info("  %s (%d B)", name, len(files[name]))

        if only_file:
            files = {k: v for k, v in files.items() if k == only_file}
            if not files:
                raise RuntimeError(f"--file {only_file}: 上游不存在该文件")

        total_segments = 0
        seg_counts: Dict[str, int] = {}
        for name, raw in files.items():
            if len(raw) > MAX_FILE_BYTES:
                raise RuntimeError(f"{name}: 文件超过 {MAX_FILE_BYTES}B 硬上限")
            segs = segment_md(raw.decode("utf-8"), name)
            seg_counts[name] = len(segs)
            total_segments += len(segs)
        if total_segments > MAX_TOTAL_SEGMENTS:
            raise RuntimeError(f"总段数 {total_segments} 超过硬上限 {MAX_TOTAL_SEGMENTS}")

        if dry_run:
            print(json.dumps({
                "mode": "init", "dry_run": True, "commit": sha,
                "would_write": sorted(files.keys()),
                "paragraphs": seg_counts, "total_segments": total_segments,
            }, ensure_ascii=False, indent=2))
            return {"mode": "init", "commit": sha, "dry_run": True,
                    "has_changes": True, "files": sorted(files.keys())}

        ctx.source_dir.mkdir(parents=True, exist_ok=True)
        for name, raw in files.items():
            (_safe_join(ctx.source_dir, name)).write_bytes(raw)
        mirrored = mirror_assets(doc_dir, ctx.source_dir)
        logger.info("assets 镜像 %d 个文件", len(mirrored))

        (ctx.source_dir / "_upstream_commit").write_text(sha + "\n", encoding="utf-8")

        today = date.today().isoformat()
        m = Manifest(schema=MANIFEST_SCHEMA_VERSION, remote=repo_url,
                     baseline_commit=sha, snapshot_date=today, files=[])
        for name in sorted(files):
            raw = files[name]
            m.files.append({
                "file": name,
                "blob_sha": compute_blob_sha(raw),
                "size": len(raw),
                "status": "missing",
                "zh": f"zh/{name}",
                "paragraphs": seg_counts[name],
                "updated_at": today,
            })
        save_manifest(ctx.manifest_file, m)

        report = render_report(
            mode="init", sha=sha, ref=ref, dry_run=False,
            changes=[FileChange(f["file"], "A", new_blob=f["blob_sha"],
                                action="applied") for f in m.files],
            extra={"assets": mirrored, "total_segments": total_segments})
        report_path = ctx.reports_dir / f"sync-{today}-{sha[:8]}.md"
        ctx.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        logger.info("同步报告：%s", report_path)

        print(json.dumps({"mode": "init", "commit": sha, "dry_run": False,
                          "has_changes": True, "files": sorted(files.keys()),
                          "total_segments": total_segments,
                          "assets": len(mirrored), "report": report_path.name},
                         ensure_ascii=False))
        return {"mode": "init", "commit": sha, "dry_run": False,
                "has_changes": True, "files": sorted(files.keys())}


def sync_check_or_apply(ctx: SyncContext, repo_url: str, ref: str,
                        only_file: Optional[str], dry_run: bool, apply: bool) -> Dict:
    """--check / --apply：文件级 blob sha 比对 → 段落级工作项。"""
    m = load_manifest(ctx.manifest_file)
    if m is None:
        raise RuntimeError("manifest.yml 不存在；请先执行 --init 首次快照")
    sha = prepare_upstream(repo_url, ctx.workdir, ref)
    doc_dir = ctx.workdir / UPSTREAM_DOC
    upstream = read_upstream_md(doc_dir)

    changes: List[FileChange] = []
    workitems: Dict[str, Dict[str, int]] = {}

    manifest_names = {f["file"] for f in m.files}
    upstream_names = set(upstream.keys())
    if only_file:
        upstream_names = {n for n in upstream_names if n == only_file}
        manifest_names = {n for n in manifest_names if n == only_file}

    # 改名识别：上游删除集 × 新增集按 blob sha 配对（无 git 历史也可识别，§5.3）
    removed_names = manifest_names - upstream_names
    added_names = upstream_names - manifest_names
    renames: Dict[str, str] = {}  # old -> new
    for new_name in sorted(added_names):
        new_sha = compute_blob_sha(upstream[new_name])
        for old_name in sorted(removed_names):
            old_entry = m.entry(old_name)
            if old_entry and old_entry["blob_sha"] == new_sha:
                renames[old_name] = new_name
                break
    for old_name, new_name in renames.items():
        removed_names.discard(old_name)
        added_names.discard(new_name)

    today = date.today().isoformat()

    def _has_zh(fname: str) -> bool:
        return (ctx.zh_dir / fname).exists()

    for name in sorted(upstream_names & manifest_names):
        raw = upstream[name]
        if len(raw) > MAX_FILE_BYTES:
            raise RuntimeError(f"{name}: 文件超过 {MAX_FILE_BYTES}B 硬上限")
        entry = m.entry(name)
        new_blob = compute_blob_sha(raw)
        ch = FileChange(name, "NONE", old_blob=entry["blob_sha"], new_blob=new_blob)
        if new_blob != entry["blob_sha"]:
            ch.type = "M"
            old_segs = segment_md(
                (_safe_join(ctx.source_dir, name)).read_text(encoding="utf-8"), name)
            new_segs = segment_md(raw.decode("utf-8"), name)
            counts = scan_workitems(old_segs, new_segs)
            ch.added, ch.modified, ch.removed = (counts["added"], counts["modified"],
                                                 counts["removed"])
            workitems[name] = counts
            if apply and not dry_run:
                (_safe_join(ctx.source_dir, name)).write_bytes(raw)
                entry["blob_sha"] = new_blob
                entry["size"] = len(raw)
                entry["paragraphs"] = len(new_segs)
                entry["updated_at"] = today
                # stale 仅当 zh 已开译（存在 front-matter），否则保持/置为 missing
                entry["status"] = "stale" if _has_zh(name) else "missing"
                ch.action = "applied"
            else:
                ch.action = "would-apply" if apply else "detected"
        changes.append(ch)

    for old_name, new_name in renames.items():
        ch = FileChange(f"{old_name} -> {new_name}", "R",
                        old_blob=m.entry(old_name)["blob_sha"],
                        new_blob=compute_blob_sha(upstream[new_name]))
        if apply and not dry_run:
            raw = upstream[new_name]
            (_safe_join(ctx.source_dir, new_name)).write_bytes(raw)
            src_old = _safe_join(ctx.source_dir, old_name)
            if src_old.exists():
                src_old.unlink()
            zh_old = ctx.zh_dir / old_name
            if zh_old.exists():
                zh_new = ctx.zh_dir / new_name
                shutil.move(str(zh_old), str(zh_new))
                # 机械性改写 front-matter 的 upstream_file / zh 路径（保留译文不重译）
                fm = front_matter_of(zh_new)
                if fm is not None:
                    text = zh_new.read_text(encoding="utf-8")
                    text = text.replace(
                        f"upstream_file: {old_name}", f"upstream_file: {new_name}",
                        1)
                    zh_new.write_text(text, encoding="utf-8")
            entry = m.entry(old_name)
            entry["file"] = new_name
            entry["zh"] = f"zh/{new_name}"
            entry["blob_sha"] = ch.new_blob
            entry["size"] = len(raw)
            entry["paragraphs"] = len(segment_md(raw.decode("utf-8"), new_name))
            entry["updated_at"] = today
            ch.action = "applied"
        else:
            ch.action = "would-apply" if apply else "detected"
        changes.append(ch)

    for name in sorted(removed_names):
        # 上游删除：不自动删译文（保留工作成果），报告标记人工处置
        changes.append(FileChange(name, "D", old_blob=m.entry(name)["blob_sha"],
                                  action="flagged-for-human"))

    if apply and not dry_run:
        for name in sorted(added_names):
            raw = upstream[name]
            if len(raw) > MAX_FILE_BYTES:
                raise RuntimeError(f"{name}: 文件超过 {MAX_FILE_BYTES}B 硬上限")
            segs = segment_md(raw.decode("utf-8"), name)
            (_safe_join(ctx.source_dir, name)).write_bytes(raw)
            m.files.append({
                "file": name, "blob_sha": compute_blob_sha(raw),
                "size": len(raw), "status": "missing", "zh": f"zh/{name}",
                "paragraphs": len(segs), "updated_at": today,
            })
            changes.append(FileChange(name, "A", new_blob=compute_blob_sha(raw),
                                      action="applied"))
        m.files.sort(key=lambda f: f["file"])
        save_manifest(ctx.manifest_file, m)
        (ctx.source_dir / "_upstream_commit").write_text(sha + "\n", encoding="utf-8")
        mirrored = mirror_assets(doc_dir, ctx.source_dir)
        if mirrored:
            logger.info("assets 增量镜像 %d 个文件", len(mirrored))

    stale = [f["file"] for f in m.files if f["status"] == "stale"]
    missing = [f["file"] for f in m.files if f["status"] == "missing"]
    summary = {
        "mode": "apply" if apply else "check",
        "commit": sha,
        "dry_run": dry_run,
        "has_changes": any(c.type != "NONE" for c in changes),
        "changes": [c.__dict__ for c in changes],
        "workitems": workitems,
        "stale": stale,
        "missing": missing,
    }

    if apply and not dry_run and changes:
        report_path = ctx.reports_dir / f"sync-{today}-{sha[:8]}.md"
        ctx.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            render_report(mode="apply", sha=sha, ref=ref, dry_run=False,
                          changes=changes, extra={"workitems": workitems}),
            encoding="utf-8")
        logger.info("同步报告：%s", report_path)
        summary["report"] = report_path.name
    elif changes:
        print(render_report(mode="apply" if apply else "check", sha=sha, ref=ref,
                            dry_run=True, changes=changes,
                            extra={"workitems": workitems}))

    print(json.dumps(summary, ensure_ascii=False))
    return summary


def mark_current(ctx: SyncContext, fname: str, upstream_sha: str) -> Dict:
    """--mark-current：校验 zh front-matter 与 manifest/上游对齐后置 status=current。"""
    m = load_manifest(ctx.manifest_file)
    if m is None:
        raise RuntimeError("manifest.yml 不存在")
    entry = m.entry(fname)
    if entry is None:
        raise RuntimeError(f"manifest 中不存在 {fname}")
    zh_file = ctx.zh_dir / fname
    fm = front_matter_of(zh_file)
    if fm is None:
        raise RuntimeError(f"{zh_file} 缺 front-matter，不能标记 current")
    problems = []
    if fm.get("upstream_file") != fname:
        problems.append(f"front-matter upstream_file={fm.get('upstream_file')!r}")
    if fm.get("upstream_hash") != entry["blob_sha"]:
        problems.append(
            f"front-matter upstream_hash={fm.get('upstream_hash')!r} != manifest "
            f"blob_sha={entry['blob_sha']!r}")
    if fm.get("upstream_commit") != upstream_sha:
        problems.append(
            f"front-matter upstream_commit={fm.get('upstream_commit')!r} != "
            f"上游 {_upstream_commit_of(ctx)!r}")
    if fm.get("status") != "current":
        problems.append(f"front-matter status={fm.get('status')!r}（批次完成后应为 current）")
    if problems:
        raise RuntimeError("mark-current 校验失败（front-matter 与账本不一致）：\n  - "
                           + "\n  - ".join(problems))
    entry["status"] = "current"
    entry["updated_at"] = date.today().isoformat()
    save_manifest(ctx.manifest_file, m)
    print(json.dumps({"mode": "mark-current", "file": fname, "status": "current"},
                     ensure_ascii=False))
    return {"file": fname, "status": "current"}


def _upstream_commit_of(ctx: SyncContext) -> str:
    f = ctx.source_dir / "_upstream_commit"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


# ---------- 报告渲染 ----------

def render_report(mode: str, sha: str, ref: str, dry_run: bool,
                  changes: List[FileChange], extra: Dict) -> str:
    today = date.today().isoformat()
    lines = [
        f"# 同步报告：{today} @ {sha[:8]}（{ref}）",
        "",
        f"- 模式：`--{mode}`" + ("（dry-run 预演，未写盘）" if dry_run else ""),
        f"- 上游 commit：`{sha}`",
        f"- 仓库：`{UPSTREAM_REPO}`",
        "",
        "| 文件 | 变更 | 新增段 | 修改段 | 删除段 | 动作 |",
        "|---|---|---|---|---|---|",
    ]
    for c in changes:
        if c.type == "R":
            name_disp = c.file
            c_type = "R(改名)"
        else:
            name_disp = c.file
            c_type = c.type
        lines.append(
            f"| {name_disp} | {c_type} | {c.added} | {c.modified} | {c.removed} "
            f"| {c.action} |")
    if "workitems" in extra and extra["workitems"]:
        lines += ["", "## 段落级工作项", ""]
        for fname, counts in extra["workitems"].items():
            if any(counts.values()):
                lines.append(
                    f"- `{fname}`：新增 {counts['added']} / 修改（复译）"
                    f"{counts['modified']} / 删除 {counts['removed']}")
        lines.append("")
        lines.append("批次认领：按 PLAN §6.1 批次表执行；同一文件批次串行。")
    if "assets" in extra:
        lines += ["", f"assets 镜像 {len(extra['assets'])} 个文件："]
        lines += [f"- {a}" for a in extra["assets"]]
    lines += ["", "---", "",
              f"*报告生成：{mode} 模式 @ {sha[:8]}（{today}）*"]
    return "\n".join(lines)


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sync_upstream.py",
        description="同步上游 google/benchmark docs/（--init / --check / --apply / "
                    "--mark-current；一律建议 memgate 包裹运行）")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--init", action="store_true", help="首次快照（仅一次）")
    g.add_argument("--check", action="store_true",
                   help="只检测变更，不写盘（CI 每周检测用）")
    g.add_argument("--apply", action="store_true",
                   help="应用变更：更新 source/ 与 manifest，产出工作项报告")
    g.add_argument("--mark-current", metavar="FILE",
                   help="校验对齐后把 zh/<FILE> 标记为 current（翻译批次收尾用）")
    p.add_argument("--dry-run", action="store_true",
                   help="与 --init/--apply 组合：只打印工作项不写盘")
    p.add_argument("--file", metavar="NAME", help="只处理指定文件（调试）")
    p.add_argument("--repo", default=UPSTREAM_REPO,
                   help=f"上游仓库 URL（默认 {UPSTREAM_REPO}；测试可注入本地 file://）")
    p.add_argument("--workdir", default=None,
                   help="克隆缓存目录（默认 workdir/upstream；测试隔离用）")
    p.add_argument("--ref", default=DEFAULT_REF, help="上游分支/标签（默认 main）")
    return p


def main(argv: Optional[List[str]] = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    ctx = get_ctx()
    if args.workdir:
        ctx = SyncContext(source_dir=ctx.source_dir, zh_dir=ctx.zh_dir,
                          reports_dir=ctx.reports_dir,
                          manifest_file=ctx.manifest_file,
                          workdir=Path(args.workdir))
    if args.mark_current and (args.dry_run or args.file):
        parser.error("--mark-current 不支持 --dry-run/--file")
    if args.dry_run and (args.check or args.mark_current):
        parser.error("--dry-run 仅与 --init/--apply 组合")
    if args.file and args.mark_current:
        parser.error("--file 与 --mark-current 互斥")

    try:
        if args.init:
            sync_init(ctx, args.repo, args.ref, args.file, args.dry_run)
        elif args.check:
            sync_check_or_apply(ctx, args.repo, args.ref, args.file,
                                dry_run=True, apply=False)
        elif args.apply:
            sync_check_or_apply(ctx, args.repo, args.ref, args.file,
                                dry_run=args.dry_run, apply=True)
        elif args.mark_current:
            mark_current(ctx, args.mark_current, _upstream_commit_of(ctx))
    except (RuntimeError, subprocess.CalledProcessError, OSError) as e:
        logger.error("Failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
