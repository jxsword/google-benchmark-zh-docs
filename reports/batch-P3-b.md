# 批次报告：P3-b（perf_counters + python_bindings + random_interleaving 合批）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/perf_counters.md`（9 段）：用户请求的性能计数器——PMU/libpfm 前提、
  Bazel/CMake 启用方式、`--benchmark_perf_counters` 用法、经用户计数器机制回报
- `zh/python_bindings.md`（8 段）：PyPI wheel（含 3.14t/3.15t 自由线程构建）、
  虚拟环境建议、源码构建 wheel
- `zh/random_interleaving.md`（4 段）：随机交错——运行间方差平均降低 40%、
  三个关联 flag
- 占位符合计 22 处全保真

## 2. 变更段清单

- 新译：三文件全文；random_interleaving 的标题与正文统一 glossary 译名「随机交错」
- 本批发现并修复门禁冲突（见 §4.1）

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| Performance Monitoring Unit (PMU) → 性能监控单元（PMU） | |
| wheel → wheel（不译） | Python 打包格式专名 |
| free-threaded build → 自由线程构建 | Python 3.14t/3.15t 语境 |
| opt-in → 启用方式 | |
| run-to-run variance → 运行间方差 | 与「随机交错」条目配套 |

## 4. 遗留问题与门禁修复（随批入库）

1. **占位符门禁与链接门禁冲突修复**：全库唯一跨目录链接
   `../README.md#custom-counters` 经 fix_links 映射为上游绝对 URL 后，URL 内容哈希
   改变，第 3 项占位符比对报「缺失/多余」，与第 4 项链接归一比对矛盾。修复：URL 类
   占位符（PROTECTED_URL_*）不参与占位符多重集比对，链接目标语义由第 4 项独占约束；
   新增回归用例 test_check_ignores_url_tokens_mapped_by_fix_links。
2. perf_counters 页首 `<a name>` 锚点行保留原样（M5 锚点注入时统一处理）。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 22/22 |
| 结构对等 / 链接集合（含 ../ 映射） | 全部一致 |
| `validate_zh.sh`（三文件） | 各 0 error / 0 warning |
| 全库单测 | 44 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
