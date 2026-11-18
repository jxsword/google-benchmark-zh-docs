# google-benchmark 中文文档

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![benchmark](https://img.shields.io/badge/benchmark-v1.10.0-blue.svg)](https://github.com/google/benchmark/releases/tag/v1.10.0)

> Google Benchmark 官方文档中文翻译版 — 基于 [google/benchmark](https://github.com/google/benchmark) 官方 `docs/` 目录系统性翻译，段落级增量同步跟随上游，术语一致性与质量门禁自动化保障。

## 📖 项目简介

[Google Benchmark](https://github.com/google/benchmark) 是一个 C++ 微基准测试支持库（官方文档站点见 [google.github.io/benchmark](https://google.github.io/benchmark/)）。本仓库将其官方文档 `docs/` 目录全部 12 个 Markdown 页面翻译为中文：

| 特性 | 说明 |
|------|------|
| **增量同步** | 段落级 hash 对比上游变更，只重译变更内容，不整篇重译 |
| **术语一致** | 统一术语表 + 门禁自动扫描，杜绝同词异译 |
| **质量门禁** | 结构对等 / 占位符 / 链接 / 排版 / 未译残留检查全自动化 |
| **持续跟随** | 每周定时检测上游 `docs/` 变更，自动产出可认领的翻译工作项 |

文档基线：上游 `main @ 88e2febd38`（2026-11-18），`docs/` 最后改动 commit `f6c2cc6b`（2026-11-09），上游当前版本 v1.10.0（2026-10-14 发布）。

## 🔗 在线阅读

- **中文版**: https://jxsword.github.io/google-benchmark-zh-docs/ （站点首次部署于 M5 里程碑后生效）
- **英文原版**: https://google.github.io/benchmark/
- **上游仓库**: https://github.com/google/benchmark

## ⚠️ 非官方声明

本项目为社区中文翻译，**非 Google 官方项目**，与 Google 无任何隶属关系。译文仅供参考；如与官方英文文档有出入，一律以官方英文文档为准。

## 📄 署名（Attribution）

本仓库译文基于以下上游文档翻译，并按相同许可发布：

- **文档标题**: Google Benchmark documentation（上游仓库 `docs/` 目录）
- **作者**: benchmark contributors
- **来源**: https://github.com/google/benchmark/tree/main/docs
- **基线 commit**: `main @ 88e2febd38`（`docs/` 最后改动 `f6c2cc6b`）
- **许可**: [Apache License 2.0](LICENSE)

## 🤝 参与翻译

1. 阅读执行蓝本 [PLAN.md](PLAN.md)：批次划分见 §6.1，批次协议见 §6.2，agent 硬性规则见 §6.3；
2. 翻译前必读 [STYLE_GUIDE.md](STYLE_GUIDE.md) 与 [glossary.md](glossary.md)：术语以术语表为准，标识符 / 函数名 / flag / 代码块一律不译；
3. 同一文件同一时刻只允许一个会话持有写权限；每批次结束产出 `reports/batch-<id>.md`，并自跑 `scripts/validate_zh.sh --file <f>`，零错误才算完成；
4. 修订类批次只动变更段，不动既有合格译文；跨目录链接（`../README.md` 类）由 `scripts/fix_links.py` 统一映射为上游 GitHub 绝对 URL。

## 🛠️ 本地构建复现

### 环境要求

- Python 3.10+
- Git

### 安装依赖

```bash
git clone https://github.com/jxsword/google-benchmark-zh-docs.git
cd google-benchmark-zh-docs
pip install -r requirements.txt          # 站点构建（mkdocs Material）
pip install -r requirements-dev.txt      # 同步 / 校验脚本与单元测试
```

### 常用命令

```bash
# 本地预览站点
mkdocs serve

# 构建站点（输出 site/，不入库）
mkdocs build

# 上游同步（dry-run，先看工作项不写盘；memgate 内存闸为安全纪律要求）
memgate 2048 python3 scripts/sync_upstream.py --dry-run

# 译文质量门禁
bash scripts/validate_zh.sh
```
