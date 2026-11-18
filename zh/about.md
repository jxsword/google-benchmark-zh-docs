---
generated: local
---

# 关于本翻译

## 项目简介

本站是 [Google Benchmark](https://github.com/google/benchmark) 官方文档的中文翻译，
由社区维护，跟随上游增量同步（段落级 hash 对齐，只重译变更段）。

- 在线阅读：https://jxsword.github.io/google-benchmark-zh-docs/
- 仓库：https://github.com/jxsword/google-benchmark-zh-docs
- 执行蓝本：[PLAN.md](https://github.com/jxsword/google-benchmark-zh-docs/blob/main/PLAN.md)

## 非官方声明

本项目为社区中文翻译，**非 Google 官方项目**，与 Google 无任何隶属关系。译文仅供参考；
如与官方英文文档有出入，一律以官方英文文档为准：
https://google.github.io/benchmark/

## 署名与许可

- **文档标题**: Google Benchmark documentation（上游仓库 `docs/` 目录）
- **作者**: benchmark contributors
- **来源**: https://github.com/google/benchmark/tree/main/docs
- **基线 commit**: `main @ 88e2febd385d65ad3d43c9d7327d36f19f2727b4`
  （`docs/` 最后改动 `f6c2cc6b`，2026-11-09；快照日期 2026-11-19）
- **许可**: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## 翻译范围与基线

上游 `docs/` 目录全部 12 个 Markdown 页面（共 106,487 字节、568 个段落），
不含源码注释、上游 README 与 CHANGELOG。术语以
[glossary.md](https://github.com/jxsword/google-benchmark-zh-docs/blob/main/glossary.md) 为准。

## 本地构建复现

```bash
git clone https://github.com/jxsword/google-benchmark-zh-docs.git
cd google-benchmark-zh-docs
pip install -r requirements.txt
mkdocs serve
```
