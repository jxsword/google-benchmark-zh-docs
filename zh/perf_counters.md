---
upstream_file: perf_counters.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: f342092c99704c58cea9658e3f1cd9d7bf0b74dc
status: current
generated_by: agent
---

<a name="perf-counters" />

# 用户请求的性能计数器

运行基准测试时，用户可以选择请求收集性能计数器。这在调查场景下很有用——缩小回归原因的范围；或验证性能改进的根本原因是否符合预期。

该特性在以下条件满足时可用：

* 基准测试运行在配备性能监控单元（PMU）的架构上；
* 基准测试编译时带计数器收集支持。目前这需要 [libpfm](http://perfmon2.sourceforge.net/)，它经 Bazel 作为依赖构建。

该特性无需修改基准测试代码。计数器收集在与计时收集相同的边界处处理。

启用方式：
* Bazel 构建：把 `--define pfm=1` 加进构建 flag
* CMake：
  * 安装 `libpfm4-dev`，例如 `apt-get install libpfm4-dev`。
  * 在 `CMakeLists.txt` 中启用 CMake flag `BENCHMARK_ENABLE_LIBPFM`。

使用时，通过 `--benchmark_perf_counters` flag 传入逗号分隔的计数器名称列表。名称经 libpfm 解码——即它们是平台特定的，但部分（如 `CYCLES` 或 `INSTRUCTIONS`）由 libpfm 映射为平台特定名称——详见 libpfm
[文档](http://perfmon2.sourceforge.net/docs.html)。

计数器值经[用户计数器](https://github.com/google/benchmark/blob/main/README.md#custom-counters)
机制回报，因此它们在用户计数器支持的所有格式（如 JSON）中均可用。
