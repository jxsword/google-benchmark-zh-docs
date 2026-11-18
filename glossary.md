# 术语表（glossary.md）

> 版本: v1.0（2026-11-19，M2 定稿）
> 用法: 翻译批次 agent 必读；术语以本表为准，分歧时以官方文档上下文自译并**在本表登记**。
> 门禁: `validate_zh.sh` 第 5 项扫描「禁用译名」列——禁用译名在 zh/ 出现即 error。

## 1. 统一译名表

| 英文 | 统一译名 | 禁用译名 | 备注 |
|---|---|---|---|
| benchmark / microbenchmark | 基准测试 / 微基准测试 | 跑分 | 函数 `Benchmark()` 与类名不译 |
| state（`benchmark::State`） | 迭代状态 | 状态机、状态对象 | 类名不译 |
| iteration | 迭代 | — | 控制台输出列 `iterations` 不译；「循环」仅禁用于迭代次数语境（机器不扫，抽检把关），Loop 译「循环」正确 |
| repetition | 重复 | 复制、重复执行 | 输出列 `repetitions` 不译 |
| fixture | （不译） | 夹具、测试夹具、脚手架 | 对齐 Google Test 社区习惯 |
| reporter | reporter（类名）/ 报告器（泛指） | 汇报器、报告员 | `BenchmarkReporter` 等类名不译 |
| counter（`benchmark::Counter`） | 计数器 | 量测 | 类名不译 |
| custom counters | 自定义计数器 | — | |
| warmup | 预热 | — | `--benchmark_min_warmup_time` 等 flag 不译 |
| pause timing / resume timing | 暂停计时 / 恢复计时 | 暂停时间、恢复时间 | `PauseTiming()` 等函数名不译 |
| random interleaving | 随机交错 | 随机穿插、交错执行 | 上游特性专有名 |
| perf counter / performance counter | 性能计数器 | — | |
| variance | 方差 | 偏差（统计语境） | |
| outlier | 离群值 | 异常值（统计语境） | |
| complexity / big-O | 复杂度 / big-O | 大 O 表示法 | big-O 不译 |
| throughput | 吞吐量 | — | |
| family | benchmark 族 | 家族 | 表格聚合语境 |
| aggregation | 聚合 | 聚集、汇总（表格语境） | |
| command-line flag | 命令行 flag | 开关、命令行参数（flag 语境） | flag 一律不译 |
| user guide | 用户指南 | 使用手册、用户手册 | 本项目《用户指南》 |
| dependency | 依赖 | — | |
| release | 发布 | 发行、发版 | |
| thread | 线程 | — | 出现 157 次，全文高频 |
| CPU time | CPU 时间 | 处理器时间 | |
| real time / wallclock | 真实时间 | 实时、挂钟时间 | 上游用 "real time" 表墙钟；「实时」易误导 |
| run | 运行 | 跑分（benchmark 语境） | 动词「跑」不作机器门禁（单字子串误伤复合词）；「跑一次」→「运行一次」靠抽检把关 |
| setup / teardown | setup / teardown | 准备/清理（类名语境） | `SetUp()`/`TearDown()` 函数名不译 |

## 2. 不译清单（标识符规则）

凡以下形式**一律不译**，且保持逐字一致（validate 第 5 项 + protect 占位符双重保障）：

- 命令行 flag：`--benchmark_filter`、`--benchmark_out`、`--benchmark_repetitions`、
  `--benchmark_min_time`、`--benchmark_min_warmup_time`、`--benchmark_format`、
  `--benchmark_out_format`、`--benchmark_color`、`--benchmark_list_tests`、
  `--benchmark_report_aggregates_only`、`--benchmark_display_aggregates_only`、
  `--benchmark_counters_tabular`、`--benchmark_context`、`--benchmark_time_unit`、
  `--benchmark_perf_counters`、`--benchmark_enable_random_interleaving`、
  `--benchmark_dry_run`、`--tags`、`--v`/`--v` 以外的第三方工具 flag（compare.py 的
  `--display_aggregates_only` 等）；
- 环境变量 / 宏：`BENCHMARK_FILTER`、`BENCHMARK_OUT`、`BENCHMARK_FORMAT`、
  `BENCHMARK_OUT_FORMAT`、`BENCHMARK_COLOR`、`BENCHMARK_CONTEXT`、
  `BENCHMARK_FORMAT`、`BENCHMARK_LIST_TESTS`、`BENCHMARK_MIN_TIME`、
  `BENCHMARK_MIN_WARMUP_TIME`、`BENCHMARK_REPETITIONS`、`BENCHMARK_REPORT_AGGREGATES_ONLY`、
  `BENCHMARK_DISPLAY_AGGREGATES_ONLY`、`BENCHMARK_COUNTERS_TABULAR`、
  `BENCHMARK_DRY_RUN`、`BENCHMARK_TIME_UNIT`、`BENCHMARK_PERF_COUNTERS`、
  `BENCHMARK_ENABLE_RANDOM_INTERLEAVING`、`BENCHMARK_ENABLE_LIBPFM`、
  `BENCHMARK_CAPTURE`、`BENCHMARK_DEFINE_F`、`BENCHMARK_NAMED`、`BENCHMARK_F`、
  `BENCHMARK_MAIN` 等；
- 类 / 函数 / 类型：`benchmark::State`、`benchmark::Counter`、`Benchmark()`、
  `BenchmarkReporter`、`State::KeepRunning()`、`State::PauseTiming()`、
  `State::ResumeTiming()`、`State::SetItemProcessed()`、`DoNotOptimize()`、
  `ClobberMemory()`、`RunTheBenchmarks...` 等——**凡代码字体（反引号）内的标识符一律不译**；
- 文件名 / 路径：`compare.py`、`requirements.txt`、`CMakeLists.txt`、`WORKSPACE` 等；
- CMake/Bazel 选项：`-DBENCHMARK_ENABLE_...`、`--define` 等。

## 3. 大小写与缩写规范

- 不译且保持原大小写：API、CPU、GPU、I/O、RAM、CMake、Bazel、Jekyll、GitHub；
- 「i/o」写作「I/O」；
- flag 保留 `--` 前缀原样；
- 首字母缩写词在译文中不自行创造新缩写。
