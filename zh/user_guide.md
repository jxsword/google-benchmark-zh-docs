---
upstream_file: user_guide.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 5e935123ec7bddb840c46f7c7d81005de3f97d47
status: current
generated_by: agent
---

# 用户指南

## 命令行

[命令行选项](#command-line-options)

[输出格式](#output-formats)

[输出文件](#output-files)

[运行基准测试](#running-benchmarks)

[运行基准测试子集](#running-a-subset-of-benchmarks)

[结果比较](#result-comparison)

[额外上下文](#extra-context)

## 库

[运行与报告注意事项](#runtime-and-reporting-considerations)

[Setup/Teardown](#setupteardown)

[传递参数](#passing-arguments)

[自定义基准测试名称](#custom-benchmark-name)

[计算渐进复杂度](#asymptotic-complexity)

[模板基准测试](#templated-benchmarks)

[接受参数的模板基准测试](#templated-benchmarks-with-arguments)

[Fixtures](#fixtures)

[自定义计数器](#custom-counters)

[多线程基准测试](#multithreaded-benchmarks)

[CPU 计时器](#cpu-timers)

[手动计时](#manual-timing)

[设置时间单位](#setting-the-time-unit)

[随机交错](random_interleaving.md)

[用户请求的性能计数器](perf_counters.md)

[防止优化](#preventing-optimization)

[报告统计](#reporting-statistics)

[自定义统计](#custom-statistics)

[内存用量](#memory-usage)

[使用 RegisterBenchmark](#using-register-benchmark)

[以错误退出](#exiting-with-an-error)

[更快的 `KeepRunning` 循环](#a-faster-keep-running-loop)

## 基准测试技巧

[禁用 CPU 频率调节](#disabling-cpu-frequency-scaling)

[降低基准测试中的方差](reducing_variance.md)
<a name="command-line-options" />

## 命令行选项 {#command-line-options}

基准测试接受若干选项，既可以通过命令行接口传入，也可以在执行前设置环境变量。每一个 `--option_flag=<value>` 命令行 flag 都有对应的环境变量 `OPTION_FLAG=<value>`，环境变量在设置后作为默认值使用（命令行 flag 始终优先）。

### 选择与执行基准测试

#### `--benchmark_list_tests` (BENCHMARK_LIST_TESTS)

打印所有基准测试名称的列表并退出。该选项优先于所有其他选项。

**示例：**
```bash
$ ./benchmark --benchmark_list_tests
BM_SomeFunction
BM_AnotherFunction
```

#### `--benchmark_filter=<regex>` (BENCHMARK_FILTER)

指定要执行的基准测试集合的正则表达式。若该 flag 为空、或取值为字符串 "all"，则运行链接进可执行文件的全部基准测试。

**示例：**
```bash
$ ./benchmark --benchmark_filter=BM_memcpy/32
```

#### `--benchmark_dry_run` (BENCHMARK_DRY_RUN)

启用后，强制每个基准测试恰好执行 1 次迭代与 1 次重复，绕过任何已配置的 `MinTime()`、`MinWarmUpTime()`、`Iterations()` 或 `Repetitions()`。这适合在不想等待完整执行的情况下快速验证基准测试能否成功运行。

**示例：**
```bash
$ ./benchmark --benchmark_dry_run
```

#### `--benchmark_enable_random_interleaving` (BENCHMARK_ENABLE_RANDOM_INTERLEAVING)

设置后，对所有基准测试的重复运行启用随机交错。这有助于降低系统状态变化对基准测试结果的影响。详见 [GitHub issue #1051](https://github.com/google/benchmark/issues/1051)。

**示例：**
```bash
$ ./benchmark --benchmark_enable_random_interleaving
```

### 计时与重复控制

#### `--benchmark_min_time=<seconds>` (BENCHMARK_MIN_TIME)

指定每个基准测试应运行的最短时间（秒）。对基于 CPU 时间的测试，这是构成该测试的全部线程所用 CPU 时间的下限；对基于真实时间的测试，这是基准测试执行所耗时间的下限，与线程数量无关。

**默认值：** `0.5` 秒

**示例：**
```bash
$ ./benchmark --benchmark_min_time=1.0
```

#### `--benchmark_min_warmup_time=<seconds>` (BENCHMARK_MIN_WARMUP_TIME)

基准测试在结果被计入之前至少应运行的秒数。当被测代码需要先填充某种缓存、其性能才有意义时，预热可能是必要的。在此期间收集的结果会被丢弃，不用于报告的结果。

**默认值：** `0.0` 秒

**示例：**
```bash
$ ./benchmark --benchmark_min_warmup_time=0.5
```

#### `--benchmark_repetitions=<count>` (BENCHMARK_REPETITIONS)

每个基准测试的运行次数。若大于 1，将报告各次运行的均值与标准差。

**默认值：** `1`

**示例：**
```bash
$ ./benchmark --benchmark_repetitions=5
```

### 输出格式化

#### `--benchmark_format=<console|json|csv>` (BENCHMARK_FORMAT)

控制台输出使用的格式。有效取值为 'console'、'json' 或 'csv'。详见[输出格式](#output-formats)。

**默认值：** `console`

**示例：**
```bash
$ ./benchmark --benchmark_format=json
```

#### `--benchmark_out=<filename>` (BENCHMARK_OUT)

把额外输出写入的文件。输出格式由 `--benchmark_out_format` 控制。指定该选项不会抑制控制台输出。

**示例：**
```bash
$ ./benchmark --benchmark_out=results.json
```

#### `--benchmark_out_format=<console|json|csv>` (BENCHMARK_OUT_FORMAT)

由 `--benchmark_out` 指定的文件输出所使用的格式。有效取值为 'console'、'json' 或 'csv'。

**默认值：** `json`

**示例：**
```bash
$ ./benchmark --benchmark_out=results.csv --benchmark_out_format=csv
```

#### `--benchmark_color=<auto|true|false>` (BENCHMARK_COLOR)

输出中是否使用颜色。有效取值为 'true'/'yes'/1、'false'/'no'/0 以及 'auto'。'auto' 表示当输出发送到终端、且 TERM 环境变量被设为支持颜色的终端类型时使用颜色。

**默认值：** `auto`

**示例：**
```bash
$ ./benchmark --benchmark_color=false
```

#### `--benchmark_time_unit=<ns|us|ms|s>` (BENCHMARK_TIME_UNIT)

设置报告使用的默认时间单位。有效取值为 'ns'（纳秒）、'us'（微秒）、'ms'（毫秒）或 's'（秒）。

**默认值：**（空，自动选择）

**示例：**
```bash
$ ./benchmark --benchmark_time_unit=us
```

### 报告选项

#### `--benchmark_report_aggregates_only` (BENCHMARK_REPORT_AGGREGATES_ONLY)

启用后，对重复运行的基准测试仅报告均值、标准差及其他统计量。这会影响所有报告器（控制台与文件输出皆受影响）。

**默认值：** `false`

**示例：**
```bash
$ ./benchmark --benchmark_repetitions=5 --benchmark_report_aggregates_only
```

#### `--benchmark_display_aggregates_only` (BENCHMARK_DISPLAY_AGGREGATES_ONLY)

启用后，对重复运行的基准测试仅显示均值、标准差及其他统计量。与 `--benchmark_report_aggregates_only` 不同，该选项仅影响显示（控制台）报告器，不影响文件报告器——后者仍包含全部输出。

**默认值：** `false`

**示例：**
```bash
$ ./benchmark --benchmark_repetitions=5 --benchmark_display_aggregates_only
```

#### `--benchmark_counters_tabular` (BENCHMARK_COUNTERS_TABULAR)

向控制台打印用户计数器时是否使用表格格式。有效取值：'true'/'yes'/1、'false'/'no'/0。

**默认值：** `false`

**示例：**
```bash
$ ./benchmark --benchmark_counters_tabular=true
```

### 性能计数器与上下文

#### `--benchmark_perf_counters=<list>` (BENCHMARK_PERF_COUNTERS)

要收集的额外性能计数器列表，以 libpfm 格式给出。关于 libpfm 的更多信息，参见 [libpfm 文档](https://man7.org/linux/man-pages/man3/libpfm.3.html)。

**示例：**
```bash
$ ./benchmark --benchmark_perf_counters=cycles,instructions,cache-misses
```

#### `--benchmark_context=<key=value,...>` (BENCHMARK_CONTEXT)

要包含在输出中的额外上下文，格式为逗号分隔的键值对。该上下文会包含在 JSON 输出的 `context` 对象中。

**示例：**
```bash
$ ./benchmark --benchmark_context=compiler=clang,version=13
```

### 其他

#### `-v` (V)

要输出的详细日志级别。数值越大，输出越详细。

**默认值：** `0`

**示例：**
```bash
$ ./benchmark -v
```

<a name="output-formats" />

## 输出格式 {#output-formats}

本库支持多种输出格式。使用 `--benchmark_format=<console|json|csv>` flag（或设置 `BENCHMARK_FORMAT=<console|json|csv>` 环境变量）设置格式类型。`console` 是默认格式。

Console 格式面向人类阅读。默认情况下该格式生成带颜色的输出。上下文信息输出到 stderr，表格数据输出到 stdout。表格输出的示例如下：

```
Benchmark                               Time(ns)    CPU(ns) Iterations
----------------------------------------------------------------------
BM_SetInsert/1024/1                        28928      29349      23853  133.097kiB/s   33.2742k items/s
BM_SetInsert/1024/8                        32065      32913      21375  949.487kiB/s   237.372k items/s
BM_SetInsert/1024/10                       33157      33648      21431  1.13369MiB/s   290.225k items/s
```

JSON 格式输出人类可读的 JSON，分为两个顶层字段：`context` 与 `benchmarks`。该格式适合需要使用基准测试结果而又不想解析控制台输出的工具。

`context` 对象包含本次运行的整体信息，包括日期、主机、CPU、缓存、负载均值、基准测试库版本以及 `json_schema_version`。通过 `benchmark::AddCustomContext` 或 `--benchmark_context` 添加的额外上下文会以额外字符串字段的形式输出到 `context` 中。

`benchmarks` 数组为每个基准测试结果包含一个对象。迭代结果通常包括 `name`、`run_name`、`run_type`、`iterations`、`real_time`、`cpu_time`、`time_unit` 与 `threads` 等字段。视基准测试配置而定，结果对象还可能包括聚合字段、渐进复杂度字段、跳过/错误字段、内存指标、标签、用户计数器以及用户请求的性能计数器。

用户计数器（包括 `bytes_per_second` 与 `items_per_second` 之类的速率）会作为额外的数值字段输出在基准测试对象上。用户请求的性能计数器以同样的方式报告。

JSON 输出随时间推移可能新增字段。使用方应忽略未知字段，并容忍可选字段缺席。这使得格式可以在保持对既有使用方兼容的前提下扩展。

JSON 输出示例（有删节）如下：

```json
{
  "context": {
    "date": "2015/03/17-18:40:25",
    "host_name": "my-host",
    "num_cpus": 40,
    "mhz_per_cpu": 2801,
    "cpu_scaling_enabled": false,
    "caches": [
      {
        "type": "Data",
        "level": 1,
        "size": 32768,
        "num_sharing": 2
      }
    ],
    "load_avg": [],
    "library_version": "vX.Y.Z",
    "library_build_type": "debug",
    "json_schema_version": 1
  },
  "benchmarks": [
    {
      "name": "BM_SetInsert/1024/1",
      "run_name": "BM_SetInsert/1024/1",
      "run_type": "iteration",
      "iterations": 94877,
      "real_time": 29275,
      "cpu_time": 29836,
      "time_unit": "ns",
      "bytes_per_second": 134066,
      "items_per_second": 33516
    },
    {
      "name": "BM_SetInsert/1024/8",
      "run_name": "BM_SetInsert/1024/8",
      "run_type": "iteration",
      "iterations": 21609,
      "real_time": 32317,
      "cpu_time": 32429,
      "time_unit": "ns",
      "bytes_per_second": 986770,
      "items_per_second": 246693
    },
    {
      "name": "BM_SetInsert/1024/10",
      "run_name": "BM_SetInsert/1024/10",
      "run_type": "iteration",
      "iterations": 21393,
      "real_time": 32724,
      "cpu_time": 33355,
      "time_unit": "ns",
      "bytes_per_second": 1199226,
      "items_per_second": 299807
    }
  ]
}
```

CSV 格式输出逗号分隔值。`context` 输出到 stderr，CSV 本体输出到 stdout。CSV 输出示例如下：

```
name,iterations,real_time,cpu_time,bytes_per_second,items_per_second,label
"BM_SetInsert/1024/1",65465,17890.7,8407.45,475768,118942,
"BM_SetInsert/1024/8",116606,18810.1,9766.64,3.27646e+06,819115,
"BM_SetInsert/1024/10",106365,17238.4,8421.53,4.74973e+06,1.18743e+06,
```

<a name="output-files" />

## 输出文件 {#output-files}

使用 `--benchmark_out=<filename>` 选项把基准测试结果写入文件（或设置 `BENCHMARK_OUT`）。用 `--benchmark_out_format={json|console|csv}` 指定输出格式（或设置 `BENCHMARK_OUT_FORMAT={json|console|csv}`）。注意：'csv' 报告器已废弃，所保存的 `.csv` 文件[无法被 csv 解析器解析](https://github.com/google/benchmark/issues/794)。

指定 `--benchmark_out` 不会抑制控制台输出。

<a name="running-benchmarks" />

## 运行基准测试 {#running-benchmarks}

基准测试通过运行产出的可执行文件来执行。基准测试可执行文件默认接受若干选项，既可以通过命令行接口传入，也可以在执行前设置环境变量。每一个 `--option_flag=<value>` 命令行 flag 都有对应的环境变量 `OPTION_FLAG=<value>`，环境变量在设置后作为默认值使用（命令行 flag 始终优先）。运行基准测试时传入 `--help` flag 可获得 CLI 选项的完整列表。

### 试运行

为了在不等待多次重复与迭代的情况下确认基准测试能够成功运行，可以使用 `--benchmark_dry_run` flag。它会像平常一样运行基准测试，但只执行 1 次迭代与 1 次重复。

<a name="running-a-subset-of-benchmarks" />

## 运行基准测试子集 {#running-a-subset-of-benchmarks}

`--benchmark_filter=<regex>` 选项（或 `BENCHMARK_FILTER=<regex>` 环境变量）可用于只运行匹配指定 `<regex>` 的基准测试。例如：

```bash
$ ./run_benchmarks.x --benchmark_filter=BM_memcpy/32
Run on (1 X 2300 MHz CPU )
2016-06-25 19:34:24
Benchmark              Time           CPU Iterations
----------------------------------------------------
BM_memcpy/32          11 ns         11 ns   79545455
BM_memcpy/32k       2181 ns       2185 ns     324074
BM_memcpy/32          12 ns         12 ns   54687500
BM_memcpy/32k       1834 ns       1837 ns     357143
```

## 禁用基准测试

把基准测试函数重命名为以 "DISABLED_" 为前缀，即可临时禁用基准测试。这会使该基准测试在运行时被跳过。

<a name="result-comparison" />

## 结果比较 {#result-comparison}

可以对基准测试结果进行比较，参见[附加工具文档](tools.md)。

<a name="extra-context" />

## 额外上下文 {#extra-context}

有时在结果前打印的内容中添加额外上下文很有用。默认情况下，这一节包含运行基准测试所用 CPU 的信息。如需添加更多上下文，可以使用 `benchmark_context` 命令行 flag：

```bash
$ ./run_benchmarks --benchmark_context=pwd=`pwd`
Run on (1 x 2300 MHz CPU)
pwd: /home/user/benchmark/
Benchmark              Time           CPU Iterations
----------------------------------------------------
BM_memcpy/32          11 ns         11 ns   79545455
BM_memcpy/32k       2181 ns       2185 ns     324074
```

通过 API 也可以达到同样效果：

```c++
  benchmark::AddCustomContext("foo", "bar");
```

注意：尝试为同一个键添加第二个值会失败并给出错误信息。

<a name="runtime-and-reporting-considerations" />

## 运行与报告注意事项 {#runtime-and-reporting-considerations}

执行基准测试可执行文件时，每个基准测试函数串行运行。要运行多少次迭代是动态确定的：先运行基准测试若干次并测量耗时，以保证最终结果在统计上稳定。因此，较快的基准测试函数比较慢的函数运行更多次迭代，迭代次数也会随之报告。

无论何种情况，基准测试运行的迭代次数都由基准测试的耗时决定。具体而言：迭代次数至少为 1、不超过 1e9，直到 CPU 时间超过最小时间，或真实时间达到最小时间的 5 倍为止。每个基准测试的最小时间通过在注册的基准测试对象上调用 `MinTime` 来设置。

也可以用 `--benchmark_min_time=<value>` 命令行选项为所有基准测试设置最小时间。该 flag 支持两种形式：

* `--benchmark_min_time=<float>s` 以秒为单位设置每次基准测试重复的最短运行时间。
* `--benchmark_min_time=<integer>x` 以显式指定的迭代次数运行每次基准测试重复，而不使用基于时间的动态迭代选择。该形式适用于未在代码中显式指定迭代次数的基准测试。

为兼容起见，`--benchmark_min_time=0.5` 这类裸数值也会被解释为秒，但为了清晰起见，建议使用显式的 `s` 后缀。

例如：

```bash
$ ./run_benchmarks.x --benchmark_min_time=0.5s
$ ./run_benchmarks.x --benchmark_min_time=100x
```

如果基准测试在代码中指定了自己的 `MinTime()` 或 `Iterations()`，这些逐基准测试设置将优先于对应的 `--benchmark_min_time` 命令行形式。

此外，由于被测代码的缓存效应等原因，可能需要对基准测试进行预热才能得到稳定结果。预热指在结果真正被计入之前，先运行基准测试一段给定的时间。预热时长可以逐基准测试设置——在注册的基准测试对象上调用 `MinWarmUpTime`，也可以对全部基准测试统一设置——使用 `--benchmark_min_warmup_time` 命令行选项。注意 `MinWarmUpTime` 会覆盖单个基准测试的 `--benchmark_min_warmup_time` 值。每次基准测试的预热运行包含多少次迭代，其确定方式与上一段所述相同。预热阶段默认为 0 秒，因此默认禁用。

报告的计时是所运行迭代上的平均值。如果通过 `--benchmark_repetitions` 命令行选项（或在注册时）请求多次重复，基准测试函数将被运行多次，同时还会报告跨这些重复的统计结果。

除了逐基准测试的条目之外，报告的前言部分还会包含运行基准测试的机器信息。

<a name="setup-teardown" />

## Setup/Teardown {#setupteardown}

可以通过向 Setup/Teardown 传入回调，为每个基准测试执行全局 setup/teardown：

setup/teardown 回调对每个基准测试各调用一次。如果基准测试是多线程的（将在 k 个线程中运行），那么每次以 k 线程运行之前，回调恰被调用一次。

如果基准测试使用不同规模的线程组，上述行为对每个规模组同样成立。

例如：

```c++
static void DoSetup(const benchmark::State& state) {
}

static void DoTeardown(const benchmark::State& state) {
}

static void BM_func(benchmark::State& state) {...}

BENCHMARK(BM_func)->Arg(1)->Arg(3)->Threads(16)->Threads(32)->Setup(DoSetup)->Teardown(DoTeardown);

```

在本例中，`DoSetup` 与 `DoTearDown` 各被调用 4 次，即对该 benchmark 族中的每一个各调用一次：
 - BM_func_Arg_1_Threads_16, BM_func_Arg_1_Threads_32
 - BM_func_Arg_3_Threads_16, BM_func_Arg_3_Threads_32

<a name="passing-arguments" />

## 传递参数 {#passing-arguments}

有时一个 benchmark 族可以用单个例程实现：该例程接受一个额外参数，用于指定要运行该族中的哪个基准测试。例如，下面的代码定义了一个 benchmark 族，用于测量不同长度的 `memcpy()` 调用速度：

```c++
static void BM_memcpy(benchmark::State& state) {
  char* src = new char[state.range(0)];
  char* dst = new char[state.range(0)];
  memset(src, 'x', state.range(0));
  for (auto _ : state)
    memcpy(dst, src, state.range(0));
  state.SetBytesProcessed(int64_t(state.iterations()) *
                          int64_t(state.range(0)));
  delete[] src;
  delete[] dst;
}
BENCHMARK(BM_memcpy)->Arg(8)->Arg(64)->Arg(512)->Arg(4<<10)->Arg(8<<10);
```

上面的代码相当重复，可以用下面的简写形式替代。下面的调用会在指定范围内选取若干合适的参数，并为每个这样的参数生成一个基准测试。

```c++
BENCHMARK(BM_memcpy)->Range(8, 8<<10);
```

默认情况下，范围内的参数按 8 的倍数生成，上面的命令选取 [ 8, 64, 512, 4k, 8k ]。下面的代码把范围乘数改为 2 的倍数。

```c++
BENCHMARK(BM_memcpy)->RangeMultiplier(2)->Range(8, 8<<10);
```

此时生成的参数为 [ 8, 16, 32, 64, 128, 256, 512, 1024, 2k, 4k, 8k ]。

上面的代码展示了定义稀疏范围的方法。下面的示例展示定义稠密范围的方法，然后用它对不同尺寸均匀递增时 `std::vector` 的初始化性能进行基准测试。

```c++
static void BM_DenseRange(benchmark::State& state) {
  for(auto _ : state) {
    std::vector<int> v(state.range(0), state.range(0));
    auto data = v.data();
    benchmark::DoNotOptimize(data);
    benchmark::ClobberMemory();
  }
}
BENCHMARK(BM_DenseRange)->DenseRange(0, 1024, 128);
```

此时生成的参数为 [ 0, 128, 256, 384, 512, 640, 768, 896, 1024 ]。

基准测试可能依赖两个或更多输入。例如，下面的代码定义了一个 benchmark 族，用于测量集合插入的速度。

```c++
static void BM_SetInsert(benchmark::State& state) {
  std::set<int> data;
  for (auto _ : state) {
    state.PauseTiming();
    data = ConstructRandomSet(state.range(0));
    state.ResumeTiming();
    for (int j = 0; j < state.range(1); ++j)
      data.insert(RandomNumber());
  }
}
BENCHMARK(BM_SetInsert)
    ->Args({1<<10, 128})
    ->Args({2<<10, 128})
    ->Args({4<<10, 128})
    ->Args({8<<10, 128})
    ->Args({1<<10, 512})
    ->Args({2<<10, 512})
    ->Args({4<<10, 512})
    ->Args({8<<10, 512});
```

上面的代码相当重复，可以用下面的简写形式替代。下面的宏会在两个指定范围的乘积中选取若干合适的参数，并为每个这样的参数对生成一个基准测试。

<!-- {% raw %} -->
```c++
BENCHMARK(BM_SetInsert)->Ranges({{1<<10, 8<<10}, {128, 512}});
```
<!-- {% endraw %} -->

某些基准测试可能需要 `Ranges` 无法表达的特定参数值。此时，`ArgsProduct` 可以为所提供向量的乘积中的每个组合生成一个基准测试输入。

<!-- {% raw %} -->
```c++
BENCHMARK(BM_SetInsert)
    ->ArgsProduct({{1<<10, 3<<10, 8<<10}, {20, 40, 60, 80}})
// would generate the same benchmark arguments as
BENCHMARK(BM_SetInsert)
    ->Args({1<<10, 20})
    ->Args({3<<10, 20})
    ->Args({8<<10, 20})
    ->Args({3<<10, 40})
    ->Args({8<<10, 40})
    ->Args({1<<10, 40})
    ->Args({1<<10, 60})
    ->Args({3<<10, 60})
    ->Args({8<<10, 60})
    ->Args({1<<10, 80})
    ->Args({3<<10, 80})
    ->Args({8<<10, 80});
```
<!-- {% endraw %} -->

针对最常见场景，本库提供了为给定稀疏或稠密范围创建整数列表的辅助方法。

```c++
BENCHMARK(BM_SetInsert)
    ->ArgsProduct({
      benchmark::CreateRange(8, 128, /*multi=*/2),
      benchmark::CreateDenseRange(1, 4, /*step=*/1)
    })
// would generate the same benchmark arguments as
BENCHMARK(BM_SetInsert)
    ->ArgsProduct({
      {8, 16, 32, 64, 128},
      {1, 2, 3, 4}
    });
```

对于更复杂的输入模式，向 `Apply` 传入自定义函数，即可通过编程方式指定运行基准测试的任意参数集合。下面的示例在第一个参数上枚举稠密范围，在第二个参数上枚举稀疏范围。

```c++
static void CustomArguments(benchmark::Benchmark* b) {
  for (int i = 0; i <= 10; ++i)
    for (int j = 32; j <= 1024*1024; j *= 8)
      b->Args({i, j});
}
BENCHMARK(BM_SetInsert)->Apply(CustomArguments);
```

### 为基准测试参数命名

当基准测试接受一个或多个数值参数时，为这些参数命名可以让生成的基准测试名称更易读。单参数用 `ArgName`，多参数用 `ArgNames`。

```c++
BENCHMARK(BM_memcpy)->Range(8, 512)->ArgName("bytes");
```

这会把 `BM_memcpy/8` 与 `BM_memcpy/512` 之类的名称变为 `BM_memcpy/bytes:8` 与 `BM_memcpy/bytes:512`。

对有多于一个参数的基准测试，每个名称标注对应的参数位置。

<!-- {% raw %} -->
```c++
BENCHMARK(BM_SetInsert)
    ->Args({100, 128})
    ->Args({200, 512})
    ->ArgNames({"size", "inserts"});
```
<!-- {% endraw %} -->

这会生成诸如 `BM_SetInsert/size:100/inserts:128` 与 `BM_SetInsert/size:200/inserts:512` 的名称。允许空参数名——此时该参数值不带标签，例如 `ArgNames({"size", ""})` 会生成 `BM_SetInsert/size:100/128` 之类的名称。

### 向基准测试传递任意参数

可以定义接受任意数量额外参数的基准测试。`BENCHMARK_CAPTURE(func, test_case_name, ...args)` 宏创建一个基准测试，它调用 `func`，以 `benchmark::State` 作为第一个参数，后接指定的 `args...`。`test_case_name` 会被附加到基准测试名称之后，应描述所传入的值。

```c++
template <class ...Args>
void BM_takes_args(benchmark::State& state, Args&&... args) {
  auto args_tuple = std::make_tuple(std::move(args)...);
  for (auto _ : state) {
    std::cout << std::get<0>(args_tuple) << ": " << std::get<1>(args_tuple)
              << '\n';
    [...]
  }
}
// Registers a benchmark named "BM_takes_args/int_string_test" that passes
// the specified values to `args`.
BENCHMARK_CAPTURE(BM_takes_args, int_string_test, 42, std::string("abc"));

// Registers the same benchmark "BM_takes_args/int_test" that passes
// the specified values to `args`.
BENCHMARK_CAPTURE(BM_takes_args, int_test, 42, 43);
```

注意 `...args` 的元素可以引用全局变量。用户应避免在基准测试内部修改全局状态。

### 在不捕获参数的情况下为基准测试命名

如果只需要给基准测试一个自定义名称（不传额外参数），请使用 `BENCHMARK_NAMED(func, test_case_name)`。与 `BENCHMARK_CAPTURE` 不同，该宏不会创建 lambda，从而在注册数千个基准测试时避免编译器与链接器的可扩展性问题。

```c++
void BM_Foo(benchmark::State& state) {
  for (auto _ : state) {}
}
// Registers a benchmark named "BM_Foo/my_variant"
BENCHMARK_NAMED(BM_Foo, my_variant);
```

需要传额外参数时使用 `BENCHMARK_CAPTURE`；只需要名称时使用 `BENCHMARK_NAMED`。

<a name="asymptotic-complexity" />

## 计算渐进复杂度（big-O）

可以为 benchmark 族计算渐进复杂度。下面的代码将计算运行时间最高阶项的系数，以及字符串比较的归一化均方根误差。

```c++
static void BM_StringCompare(benchmark::State& state) {
  std::string s1(state.range(0), '-');
  std::string s2(state.range(0), '-');
  for (auto _ : state) {
    auto comparison_result = s1.compare(s2);
    benchmark::DoNotOptimize(comparison_result);
  }
  state.SetComplexityN(state.range(0));
}
BENCHMARK(BM_StringCompare)
    ->RangeMultiplier(2)->Range(1<<10, 1<<18)->Complexity(benchmark::oN);
```

如下面的调用所示，渐进复杂度也可以自动计算。

```c++
BENCHMARK(BM_StringCompare)
    ->RangeMultiplier(2)->Range(1<<10, 1<<18)->Complexity();
```

下面的代码通过 lambda 函数指定渐进复杂度，可用于自定义最高阶项的计算。

```c++
BENCHMARK(BM_StringCompare)->RangeMultiplier(2)
    ->Range(1<<10, 1<<18)->Complexity([](benchmark::ComplexityN n)->double{return n; });
```

`BigO` 行以与该族其余部分相同的时间单位报告系数，因此以 `->Unit(benchmark::kMicrosecond)` 声明的族以微秒报告系数。`RMS` 行是归一化量，以百分比报告，与时间单位无关。

<a name="custom-benchmark-name" />

## 自定义基准测试名称 {#custom-benchmark-name}

可以按如下方式更改基准测试的名称：

```c++
BENCHMARK(BM_memcpy)->Name("memcpy")->RangeMultiplier(2)->Range(8, 8<<10);
```

该调用会照旧使用 `BM_memcpy` 执行基准测试，但把报告中的前缀更改为 `memcpy`。

<a name="templated-benchmarks" />

## 模板基准测试 {#templated-benchmarks}

本示例产生并消费大小为 `sizeof(v)`、共 `range_x` 次的消息。它还会在无多道程序设计的情况下输出吞吐量。

```c++
template <class Q> void BM_Sequential(benchmark::State& state) {
  Q q;
  typename Q::value_type v;
  for (auto _ : state) {
    for (int i = state.range(0); i--; )
      q.push(v);
    for (int e = state.range(0); e--; )
      q.Wait(&v);
  }
  // actually messages, not bytes:
  state.SetBytesProcessed(
      static_cast<int64_t>(state.iterations())*state.range(0));
}

// You can use the BENCHMARK macro with template parameters:
BENCHMARK(BM_Sequential<WaitQueue<int>>)->Range(1<<0, 1<<10);

// Old, legacy verbose C++03 syntax:
BENCHMARK_TEMPLATE(BM_Sequential, WaitQueue<int>)->Range(1<<0, 1<<10);

```

提供三个宏用于添加基准测试模板。

```c++
#define BENCHMARK(func<...>) // Takes any number of parameters.
#define BENCHMARK_TEMPLATE1(func, arg1)
#define BENCHMARK_TEMPLATE2(func, arg1, arg2)
```

<a name="templated-benchmarks-with-arguments" />

## 接受参数的模板基准测试

有时需要对基准测试模板化并向其提供参数。

```c++
template <class Q> void BM_Sequential_With_Step(benchmark::State& state, int step) {
  Q q;
  typename Q::value_type v;
  for (auto _ : state) {
    for (int i = state.range(0); i-=step; )
      q.push(v);
    for (int e = state.range(0); e-=step; )
      q.Wait(&v);
  }
  // actually messages, not bytes:
  state.SetBytesProcessed(
      static_cast<int64_t>(state.iterations())*state.range(0));
}

BENCHMARK_TEMPLATE1_CAPTURE(BM_Sequential, WaitQueue<int>, Step1, 1)->Range(1<<0, 1<<10);
```

<a name="fixtures" />

## Fixtures {#fixtures}

fixture 测试的创建方式：先定义一个派生自 `::benchmark::Fixture` 的类型，然后用以下宏创建并注册测试：

* `BENCHMARK_F(ClassName, Method)`
* `BENCHMARK_DEFINE_F(ClassName, Method)`
* `BENCHMARK_REGISTER_F(ClassName, Method)`

例如：

```c++
class MyFixture : public benchmark::Fixture {
public:
  void SetUp(::benchmark::State& state) {
  }

  void TearDown(::benchmark::State& state) {
  }
};

// Defines and registers `FooTest` using the class `MyFixture`.
BENCHMARK_F(MyFixture, FooTest)(benchmark::State& st) {
   for (auto _ : st) {
     ...
  }
}

// Only defines `BarTest` using the class `MyFixture`.
BENCHMARK_DEFINE_F(MyFixture, BarTest)(benchmark::State& st) {
   for (auto _ : st) {
     ...
  }
}
// `BarTest` is NOT registered.
BENCHMARK_REGISTER_F(MyFixture, BarTest)->Threads(2);
// `BarTest` is now registered.
```

### 模板化 Fixtures

也可以用以下宏创建模板化 fixture：

* `BENCHMARK_TEMPLATE_F(ClassName, Method, ...)`
* `BENCHMARK_TEMPLATE_DEFINE_F(ClassName, Method, ...)`

例如：

```c++
template<typename T>
class MyFixture : public benchmark::Fixture {};

// Defines and registers `IntTest` using the class template `MyFixture<int>`.
BENCHMARK_TEMPLATE_F(MyFixture, IntTest, int)(benchmark::State& st) {
   for (auto _ : st) {
     ...
  }
}

// Only defines `DoubleTest` using the class template `MyFixture<double>`.
BENCHMARK_TEMPLATE_DEFINE_F(MyFixture, DoubleTest, double)(benchmark::State& st) {
   for (auto _ : st) {
     ...
  }
}
// `DoubleTest` is NOT registered.
BENCHMARK_REGISTER_F(MyFixture, DoubleTest)->Threads(2);
// `DoubleTest` is now registered.
```

如果想为 fixture 使用方法模板、并在之后实例化它们，请使用以下宏：

* `BENCHMARK_TEMPLATE_METHOD_F(ClassName, Method)`
* `BENCHMARK_TEMPLATE_INSTANTIATE_F(ClassName, Method, ...)`

借助这些宏，可以为多个实例化定义同一个方法。示例（使用上面的 `MyFixture`）：

```c++
// Defines `Test` using the class template `MyFixture`.
BENCHMARK_TEMPLATE_METHOD_F(MyFixture, Test)(benchmark::State& st) {
   for (auto _ : st) {
     ...
  }
}

// Instantiates and registers the benchmark `MyFixture<int>::Test`.
BENCHMARK_TEMPLATE_INSTANTIATE_F(MyFixture, Test, int)->Threads(2);
// Instantiates and registers the benchmark `MyFixture<double>::Test`.
BENCHMARK_TEMPLATE_INSTANTIATE_F(MyFixture, Test, double)->Threads(4);
```

在 `BENCHMARK_TEMPLATE_METHOD_F` 的方法定义内部，类型 `Base` 指代实例化 fixture 的类型；访问 fixture 成员必须加 `this->` 前缀。

`BENCHMARK_TEMPLATE_METHOD_F` 与 `BENCHMARK_TEMPLATE_INSTANTIATE_F` 仅当 fixture 未使用非类型模板参数时才能使用。若想把值作为模板参数传递，可使用例如 `std::integral_constant`。例如：

```c++
template<typename Sz>
class SizedFixture : public benchmark::Fixture {
  static constexpr auto Size = Sz::value;
  int myValue;
};

BENCHMARK_TEMPLATE_METHOD_F(SizedFixture, Test)(benchmark::State& st) {
   for (auto _ : st) {
     this->myValue = Base::Size;
  }
}

BENCHMARK_TEMPLATE_INSTANTIATE_F(SizedFixture, Test, std::integral_constant<5>)->Threads(2);
```

<a name="custom-counters" />

## 自定义计数器 {#custom-counters}

可以添加自定义名称的计数器。下面的示例会在其输出中添加 "Foo"、"Bar" 和 "Baz" 列：

```c++
static void UserCountersExample1(benchmark::State& state) {
  double numFoos = 0, numBars = 0, numBazs = 0;
  for (auto _ : state) {
    // ... count Foo,Bar,Baz events
  }
  state.counters["Foo"] = numFoos;
  state.counters["Bar"] = numBars;
  state.counters["Baz"] = numBazs;
}
```

`state.counters` 对象是一个 `std::map`，以 `std::string` 为键、`Counter` 为值。后者是一个类似 `double` 的类，经由到 `double&` 的隐式转换。因此可以使用全部标准算术赋值运算符（`=,+=,-=,*=,/=`）修改每个计数器的值。

`Counter` 构造函数接受三个参数：以 `double` 给出的值；一个位标志，用于把计数器显示为速率、每线程迭代、每线程平均值、迭代不变量中的若干项，以及最终反转结果；还有一个指定“单位”的标志——即 1k 表示 1000（默认，`benchmark::Counter::OneK::kIs1000`）还是 1024（`benchmark::Counter::OneK::kIs1024`）？

```c++
  // sets a simple counter
  state.counters["Foo"] = numFoos;

  // Set the counter as a rate. It will be presented divided
  // by the duration of the benchmark.
  // Meaning: per one second, how many 'foo's are processed?
  state.counters["FooRate"] = Counter(numFoos, benchmark::Counter::kIsRate);

  // Set the counter as a rate. It will be presented divided
  // by the duration of the benchmark, and the result inverted.
  // Meaning: how many seconds it takes to process one 'foo'?
  state.counters["FooInvRate"] = Counter(numFoos, benchmark::Counter::kIsRate | benchmark::Counter::kInvert);

  // Set the counter as a thread-average quantity. It will
  // be presented divided by the number of threads.
  state.counters["FooAvg"] = Counter(numFoos, benchmark::Counter::kAvgThreads);

  // There's also a combined flag:
  state.counters["FooAvgRate"] = Counter(numFoos,benchmark::Counter::kAvgThreadsRate);

  // This says that we process with the rate of state.range(0) bytes every iteration:
  state.counters["BytesProcessed"] = Counter(state.range(0), benchmark::Counter::kIsIterationInvariantRate, benchmark::Counter::OneK::kIs1024);

  // Set the counter to stringify the exponent explicitly without SI prefixes (e.g. 1.2345e-04):
  state.counters["Error"] = Counter(absError, benchmark::Counter::kStringifyExponent);

  // Stringified exponents can also be combined with rates:
  state.counters["ErrorRate"] = Counter(absError, benchmark::Counter::kStringifyExponent | benchmark::Counter::kIsRate);
```

可以把 `insert()` 与 `std::initializer_list` 结合使用：

<!-- {% raw %} -->
```c++
  state.counters.insert({{"Foo", numFoos}, {"Bar", numBars}, {"Baz", numBazs}});
  // ... instead of:
  state.counters["Foo"] = numFoos;
  state.counters["Bar"] = numBars;
  state.counters["Baz"] = numBazs;
```
<!-- {% endraw %} -->

在多线程基准测试中，每个计数器只在调用线程上设置。基准测试结束时，来自各线程的计数器会被求和。配置了 `kIsRate` 的计数器将报告所有线程的平均速率，而 `kAvgThreadsRate` 计数器将报告每线程的平均速率。

### 计数器报告

使用 console 报告器时，默认情况下用户计数器打印在表格之后的末尾，方式与 ``bytes_processed`` 与 ``items_processed`` 相同。这最适合计数器较少、或每个基准测试只有几行的情形。下面是默认输出的示例：

```
------------------------------------------------------------------------------
Benchmark                        Time           CPU Iterations UserCounters...
------------------------------------------------------------------------------
BM_UserCounter/threads:8      2248 ns      10277 ns      68808 Bar=16 Bat=40 Baz=24 Foo=8
BM_UserCounter/threads:1      9797 ns       9788 ns      71523 Bar=2 Bat=5 Baz=3 Foo=1024m
BM_UserCounter/threads:2      4924 ns       9842 ns      71036 Bar=4 Bat=10 Baz=6 Foo=2
BM_UserCounter/threads:4      2589 ns      10284 ns      68012 Bar=8 Bat=20 Baz=12 Foo=4
BM_UserCounter/threads:8      2212 ns      10287 ns      68040 Bar=16 Bat=40 Baz=24 Foo=8
BM_UserCounter/threads:16     1782 ns      10278 ns      68144 Bar=32 Bat=80 Baz=48 Foo=16
BM_UserCounter/threads:32     1291 ns      10296 ns      68256 Bar=64 Bat=160 Baz=96 Foo=32
BM_UserCounter/threads:4      2615 ns      10307 ns      68040 Bar=8 Bat=20 Baz=12 Foo=4
BM_Factorial                    26 ns         26 ns   26608979 40320
BM_Factorial/real_time          26 ns         26 ns   26587936 40320
BM_CalculatePiRange/1           16 ns         16 ns   45704255 0
BM_CalculatePiRange/8           73 ns         73 ns    9520927 3.28374
BM_CalculatePiRange/64         609 ns        609 ns    1140647 3.15746
BM_CalculatePiRange/512       4900 ns       4901 ns     142696 3.14355
```

如果这不符合需求，可以通过向基准测试应用程序传入 flag `--benchmark_counters_tabular=true`，把每个计数器打印为表格的一列。这最适合计数器很多、或单个基准测试行数很多的情形。注意：每当计数器集合在各个基准测试之间发生变化，都会触发重新打印表头。传入 `--benchmark_counters_tabular=true` 时的对应输出示例如下：

```
---------------------------------------------------------------------------------------
Benchmark                        Time           CPU Iterations    Bar   Bat   Baz   Foo
---------------------------------------------------------------------------------------
BM_UserCounter/threads:8      2198 ns       9953 ns      70688     16    40    24     8
BM_UserCounter/threads:1      9504 ns       9504 ns      73787      2     5     3     1
BM_UserCounter/threads:2      4775 ns       9550 ns      72606      4    10     6     2
BM_UserCounter/threads:4      2508 ns       9951 ns      70332      8    20    12     4
BM_UserCounter/threads:8      2055 ns       9933 ns      70344     16    40    24     8
BM_UserCounter/threads:16     1610 ns       9946 ns      70720     32    80    48    16
BM_UserCounter/threads:32     1192 ns       9948 ns      70496     64   160    96    32
BM_UserCounter/threads:4      2506 ns       9949 ns      70332      8    20    12     4
--------------------------------------------------------------
Benchmark                        Time           CPU Iterations
--------------------------------------------------------------
BM_Factorial                    26 ns         26 ns   26392245 40320
BM_Factorial/real_time          26 ns         26 ns   26494107 40320
BM_CalculatePiRange/1           15 ns         15 ns   45571597 0
BM_CalculatePiRange/8           74 ns         74 ns    9450212 3.28374
BM_CalculatePiRange/64         595 ns        595 ns    1173901 3.15746
BM_CalculatePiRange/512       4752 ns       4752 ns     147380 3.14355
BM_CalculatePiRange/4k       37970 ns      37972 ns      18453 3.14184
BM_CalculatePiRange/32k     303733 ns     303744 ns       2305 3.14162
BM_CalculatePiRange/256k   2434095 ns    2434186 ns        288 3.1416
BM_CalculatePiRange/1024k  9721140 ns    9721413 ns         71 3.14159
BM_CalculatePi/threads:8      2255 ns       9943 ns      70936
```

注意上面当基准测试从 ``BM_UserCounter`` 变为 ``BM_Factorial`` 时额外打印的表头——因为 ``BM_Factorial`` 不具有与 ``BM_UserCounter`` 相同的计数器集合。

<a name="multithreaded-benchmarks"/>

## 多线程基准测试 {#multithreaded-benchmarks}

在多线程测试中（多个线程同时调用基准测试），保证没有任何线程会在全部线程到达基准测试循环起点之前启动，且在任一线程退出基准测试循环之前全部线程都已结束。（`KeepRunning()` API 也提供该行为）因此，任何全局 setup 或 teardown 都可以包裹在对线程索引的检查中：

```c++
static void BM_MultiThreaded(benchmark::State& state) {
  if (state.thread_index() == 0) {
    // Setup code here.
  }
  for (auto _ : state) {
    // Run the test as normal.
  }
  if (state.thread_index() == 0) {
    // Teardown code here.
  }
}
BENCHMARK(BM_MultiThreaded)->Threads(2);
```

要在一系列线程数上运行基准测试，用 `ThreadRange` 代替 `Threads`。它接受两个参数（`min_threads` 与 `max_threads`）和一个可选的几何乘数 `mult`（默认为 2），并对闭区间范围内的每个值各运行一次基准测试。例如：

```c++
BENCHMARK(BM_MultiThreaded)->ThreadRange(1, 8);
```

将以线程数 1、2、4、8 运行 `BM_MultiThreaded`，而：

```c++
BENCHMARK(BM_MultiThreaded)->ThreadRange(1, 16, 4);
```

将以线程数 1、4、16 运行 `BM_MultiThreaded`。

也可以用 `DenseThreadRange(min_threads, max_threads, stride = 1)` 以等差步长遍历：

```c++
BENCHMARK(BM_MultiThreaded)->DenseThreadRange(1, 4);
```

如果被测代码自身使用线程，而你想与单线程代码比较，可能需要用真实时间（“墙钟”）测量做延迟对比：

```c++
BENCHMARK(BM_test)->Range(8, 8<<10)->UseRealTime();
```

不指定 `UseRealTime` 时，默认使用 CPU 时间。

### 手动多线程基准测试

Google/benchmark 默认使用 `std::thread` 作为多线程环境。如果想使用其他多线程环境（例如 OpenMP），可以通过 `ThreadRunner` 函数为基准测试提供工厂函数。工厂函数接受线程数作为参数，并创建派生自 `benchmark::ThreadRunnerBase` 的自定义类。该自定义类必须重写 `void RunThreads(const std::function<void(int)>& fn)` 函数。`RunThreads` 由主线程调用，生成请求的线程数。每个被生成的线程必须调用 `fn(thread_index)`，其中 `thread_index` 是它自己的线程索引。在 `RunThreads` 返回之前，所有生成的线程必须被 join。

```c++
class OpenMPThreadRunner : public benchmark::ThreadRunnerBase
{
  OpenMPThreadRunner(int num_threads)
  : num_threads_(num_threads)
  {}

  void RunThreads(const std::function<void(int)>& fn) final
  {
#pragma omp parallel num_threads(num_threads_)
    fn(omp_get_thread_num());
  }

private:
  int num_threads_;
};

BENCHMARK(BM_MultiThreaded)
  ->ThreadRunner([](int num_threads) {
    return std::make_unique<OpenMPThreadRunner>(num_threads);
  })
  ->Threads(1)->Threads(2)->Threads(4);
```

上面的示例在进入 `BM_MultiThreaded` 之前创建并行 OpenMP 区域。实际的基准测试代码可以保持不变，因此不绑定到特定的线程运行器。测量不包含创建与 join 线程的时间。

<a name="cpu-timers" />

## CPU 计时器 {#cpu-timers}

默认情况下，CPU 计时器只测量主线程花费的时间。如果基准测试自身在内部使用线程，该测量可能不是你想要的。有一种方法可以测量进程内所有线程的总 CPU 占用：

```c++
void callee(int i);

static void MyMain(int size) {
#pragma omp parallel for
  for(int i = 0; i < size; i++)
    callee(i);
}

static void BM_OpenMP(benchmark::State& state) {
  for (auto _ : state)
    MyMain(state.range(0));
}

// Measure the time spent by the main thread, use it to decide for how long to
// run the benchmark loop. Depending on the internal implementation detail may
// measure to anywhere from near-zero (the overhead spent before/after work
// handoff to worker thread[s]) to the whole single-thread time.
BENCHMARK(BM_OpenMP)->Range(8, 8<<10);

// Measure the user-visible time, the wall clock (literally, the time that
// has passed on the clock on the wall), use it to decide for how long to
// run the benchmark loop. This will always be meaningful, and will match the
// time spent by the main thread in single-threaded case, in general decreasing
// with the number of internal threads doing the work.
BENCHMARK(BM_OpenMP)->Range(8, 8<<10)->UseRealTime();

// Measure the total CPU consumption, use it to decide for how long to
// run the benchmark loop. This will always measure to no less than the
// time spent by the main thread in single-threaded case.
BENCHMARK(BM_OpenMP)->Range(8, 8<<10)->MeasureProcessCPUTime();

// A mixture of the last two. Measure the total CPU consumption, but use the
// wall clock to decide for how long to run the benchmark loop.
BENCHMARK(BM_OpenMP)->Range(8, 8<<10)->MeasureProcessCPUTime()->UseRealTime();
```

### 控制计时器

通常，工作循环（`for (auto _ : state) {}`）的整个时长都会被测量。但有时需要在循环内每次迭代做一些工作，又不想把这段时间计入基准测试时间。这是可行的，但不推荐——开销很大。

<!-- {% raw %} -->
```c++
static void BM_SetInsert_With_Timer_Control(benchmark::State& state) {
  std::set<int> data;
  for (auto _ : state) {
    state.PauseTiming(); // Stop timers. They will not count until they are resumed.
    data = ConstructRandomSet(state.range(0)); // Do something that should not be measured
    state.ResumeTiming(); // And resume timers. They are now counting again.
    // The rest will be measured.
    for (int j = 0; j < state.range(1); ++j)
      data.insert(RandomNumber());
  }
}
BENCHMARK(BM_SetInsert_With_Timer_Control)->Ranges({{1<<10, 8<<10}, {128, 512}});
```
<!-- {% endraw %} -->

注意：只有计时器确实在运行时才能暂停计时；同样，只有计时器已暂停时才能恢复计时。若用户代码构建时未定义 `NDEBUG`，这类无效的暂停/恢复调用会被诊断。

为方便起见，提供了 `ScopedPauseTiming` 类在作用域内管理计时器的暂停与恢复。这比手动调用 `PauseTiming` 与 `ResumeTiming` 更不容易出错。

<!-- {% raw %} -->
```c++
static void BM_SetInsert_With_Scoped_Timer_Control(benchmark::State& state) {
  std::set<int> data;
  for (auto _ : state) {
    {
      benchmark::ScopedPauseTiming pause(state); // Pauses timing
      data = ConstructRandomSet(state.range(0));
    } // Timing resumes automatically when 'pause' goes out of scope

    // The rest will be measured.
    for (int j = 0; j < state.range(1); ++j)
      data.insert(RandomNumber());
  }
}
BENCHMARK(BM_SetInsert_With_Scoped_Timer_Control)->Ranges({{1<<10, 8<<10}, {128, 512}});
```
<!-- {% endraw %} -->

<a name="manual-timing" />

## 手动计时 {#manual-timing}

对于 CPU 时间和真实时间都不够正确或不够精确的测量对象，支持使用 `UseManualTime` 函数进行完全手动计时。

使用 `UseManualTime` 时，被测代码必须在基准测试循环的每次迭代中调用一次 `SetIterationTime`，报告手动测得的时间。

一个典型用例是 GPU 执行的基准测试（例如 OpenCL 或 CUDA kernel、OpenGL/Vulkan/Direct3D 的 draw call），它们无法用 CPU 时间或真实时间准确测量。改用专用 API 则可以准确测量，测量结果可通过 `SetIterationTime` 回报。

```c++
static void BM_ManualTiming(benchmark::State& state) {
  int microseconds = state.range(0);
  std::chrono::duration<double, std::micro> sleep_duration {
    static_cast<double>(microseconds)
  };

  for (auto _ : state) {
    auto start = std::chrono::high_resolution_clock::now();
    // Simulate some useful workload with a sleep
    std::this_thread::sleep_for(sleep_duration);
    auto end = std::chrono::high_resolution_clock::now();

    auto elapsed_seconds =
      std::chrono::duration_cast<std::chrono::duration<double>>(
        end - start);

    state.SetIterationTime(elapsed_seconds.count());
  }
}
BENCHMARK(BM_ManualTiming)->Range(1, 1<<17)->UseManualTime();
```

<a name="setting-the-time-unit" />

## 设置时间单位 {#setting-the-time-unit}

如果基准测试运行几毫秒，由于输出数据默认以纳秒给出，测得的时间很难直观比较。要手动设置时间单位，可显式指定：

```c++
BENCHMARK(BM_test)->Unit(benchmark::kMillisecond);
```

此外，可以用 `--benchmark_time_unit={ns|us|ms|s}` 命令行参数全局设置默认时间单位。该参数只影响未显式设置时间单位的基准测试。

<a name="preventing-optimization" />

## 防止优化 {#preventing-optimization}

为防止值或表达式被编译器优化掉，可以使用 `benchmark::DoNotOptimize(...)` 与 `benchmark::ClobberMemory()` 函数。

```c++
static void BM_test(benchmark::State& state) {
  for (auto _ : state) {
      int x = 0;
      for (int i=0; i < 64; ++i) {
        benchmark::DoNotOptimize(x += i);
      }
  }
}
```

`DoNotOptimize(<expr>)` 强制把 `<expr>` 的 *结果* 存入内存或寄存器。对 GNU 系编译器，它充当全局内存的读/写屏障。更具体地，它强制编译器把未决写入刷到内存，并按需重新加载其他值。

注意 `DoNotOptimize(<expr>)` 完全不会阻止对 `<expr>` 的优化。当结果已知时，`<expr>` 甚至可能被完全移除。例如：

```c++
  // Example 1: `<expr>` is removed entirely.
  int foo(int x) { return x + 42; }
  while (...) DoNotOptimize(foo(0)); // Optimized to DoNotOptimize(42);

  // Example 2: Result of '<expr>' is only reused.
  int bar(int) __attribute__((const));
  while (...) DoNotOptimize(bar(0)); // Optimized to:
  // int __result__ = bar(0);
  // while (...) DoNotOptimize(__result__);
```

由于这不是用户想要的行为，这类问题场景会在编译期产生诊断。对表达式结果而言，正确做法是使用中间局部变量：

```c++
  // Avoid: may call the deprecated const-reference overload.
  while (...) DoNotOptimize(foo(0));

  // Prefer: materialize the result, then pass the local lvalue.
  while (...) {
    auto result = foo(0);
    DoNotOptimize(result);
  }
```

第二个防止优化的工具是 `ClobberMemory()`。本质上 `ClobberMemory()` 强制编译器执行所有未决的全局内存写入。由块作用域对象管理的内存必须先用 `DoNotOptimize(...)` “逃逸”（escape），然后才能被 clobber。在下例中，`ClobberMemory()` 防止对 `v.push_back(42)` 的调用被优化掉。

```c++
static void BM_vector_push_back(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> v;
    v.reserve(1);
    auto data = v.data();           // Allow v.data() to be clobbered. Pass as non-const
    benchmark::DoNotOptimize(data); // lvalue to avoid undesired compiler optimizations
    v.push_back(42);
    benchmark::ClobberMemory(); // Force 42 to be written to memory.
  }
}
```

注意 `ClobberMemory()` 仅适用于 GNU 系或 MSVC 系编译器。

<a name="reporting-statistics" />

## 统计：报告重复基准测试的均值、中位数与标准差 / 变异系数

默认每个基准测试只运行一次并报告该单一结果。但基准测试常常有噪声，单一结果未必能代表整体行为。因此可以重复多次运行基准测试。

每个基准测试的运行次数由 `--benchmark_repetitions` flag 全局指定，或通过对注册的基准测试对象调用 `Repetitions` 逐个指定。当基准测试运行不止一次时，将报告各次运行的均值、中位数、标准差与变异系数。

此外，`--benchmark_report_aggregates_only={true|false}`、`--benchmark_display_aggregates_only={true|false}` flag 或 `ReportAggregatesOnly(bool)`、`DisplayAggregatesOnly(bool)` 函数可用于更改重复测试的报告方式。默认报告每次重复运行的结果。当 `report aggregates only` 选项为 `true` 时，只向两种报告器——标准输出（console）与文件——报告运行的聚合值（即均值、中位数、标准差与变异系数，若请求了复杂度测量则还包括它们）。而当仅 `display aggregates only` 选项为 `true` 时，标准输出只显示聚合值，文件输出仍包含全部内容。在注册的基准测试对象上调用 `ReportAggregatesOnly(bool)` / `DisplayAggregatesOnly(bool)` 会覆盖该基准测试对应 flag 的值。

<a name="custom-statistics" />

## 自定义统计 {#custom-statistics}

有这些聚合值固然好，但对所有人未必够用。例如你可能想知道最大观测值——比如有真实时间方面的约束时。这很简单。下面的代码指定一个自定义统计量，由 lambda 函数定义。

```c++
void BM_spin_empty(benchmark::State& state) {
  for (auto _ : state) {
    for (int x = 0; x < state.range(0); ++x) {
      benchmark::DoNotOptimize(x);
    }
  }
}

BENCHMARK(BM_spin_empty)
  ->Repetitions(3) // or add option --benchmark_repetitions=3
  ->ComputeStatistics("max", [](const std::vector<double>& v) -> double {
    return *(std::max_element(std::begin(v), std::end(v)));
  })
  ->Arg(512);
```

统计量通常产生时间单位的值，也可以产生百分比：

```c++
void BM_spin_empty(benchmark::State& state) {
  for (auto _ : state) {
    for (int x = 0; x < state.range(0); ++x) {
      benchmark::DoNotOptimize(x);
    }
  }
}

BENCHMARK(BM_spin_empty)
  ->Repetitions(3) // or add option --benchmark_repetitions=3
  ->ComputeStatistics("ratio", [](const std::vector<double>& v) -> double {
    return v.front() / v.back();
  }, benchmark::StatisticUnit::kPercentage)
  ->Arg(512);
```

<a name="memory-usage" />

## 内存用量 {#memory-usage}

除 CPU 性能之外，跟踪基准测试的内存用量也常常有用。为此，benchmark 提供了 `RegisterMemoryManager` 方法，允许注入自定义的 `MemoryManager`。

设置后，`MemoryManager::Start` 与 `MemoryManager::Stop` 方法会在基准测试运行的开始与结束时被调用，让用户代码填写分配次数、所用字节数等报告。

这些数据随后会与其他性能数据一起报告——目前仅 JSON 输出支持。

<a name="profiling" />

## 剖析

除 CPU 性能之外，以特定方式剖析基准测试也常常有用。为此，benchmark 提供了 `RegisterProfilerManager` 方法，允许注入自定义的 `ProfilerManager`。

设置后，`ProfilerManager::AfterSetupStart` 与 `ProfilerManager::BeforeTeardownStop` 方法会在一次单独的基准测试运行的开始与结束时被调用，让用户代码收集并报告用户提供的剖析指标。

如果你的剖析器需要当前基准测试名称或其他运行状态，请重写 `ProfilerManager::AfterSetupStartWithState(const State&)` 与 `ProfilerManager::BeforeTeardownStopWithState(const State&)`。旧式无参钩子仍然可用，并作为后备。

该剖析运行收集的输出必须单独报告。

<a name="using-register-benchmark" />

## 使用 RegisterBenchmark(name, fn, args...)

`RegisterBenchmark(name, func, args...)` 函数提供创建并注册基准测试的另一种方式。`RegisterBenchmark(name, func, args...)` 创建、注册并返回一个指针，指向新的基准测试，后者带指定的 `name` 并调用 `func(st, args...)`，其中 `st` 是一个 `benchmark::State` 对象。

`BENCHMARK` 注册宏只能在全局作用域使用；与之不同，`RegisterBenchmark` 可以在任何地方调用。这使得基准测试可以编程方式注册。

此外 `RegisterBenchmark` 允许注册任何可调用对象为基准测试，包括捕获型 lambda 与函数对象。

例如：

```c++
auto BM_test = [](benchmark::State& st, auto Inputs) { /* ... */ };

int main(int argc, char** argv) {
  benchmark::MaybeReenterWithoutASLR(argc, argv);
  for (auto& test_input : { /* ... */ })
      benchmark::RegisterBenchmark(test_input.name(), BM_test, test_input);
  benchmark::Initialize(&argc, argv);
  benchmark::RunSpecifiedBenchmarks();
  benchmark::Shutdown();
}
```

<a name="exiting-with-an-error" />

## 以错误退出 {#exiting-with-an-error}

当基准测试内部发生外部影响导致的错误（如文件 I/O 与网络通信）时，可用 `State::SkipWithError(const std::string& msg)` 函数跳过该次基准测试运行并报告错误。注意：只有 `KeepRunning()` 的后续迭代会被跳过；对基准测试循环的 ranged-for 版本，用户必须显式退出循环，否则所有迭代都会执行。用户也可以显式 return，立即退出基准测试。

`SkipWithError(...)` 函数可在基准测试内的任何时点使用，包括基准测试循环之前与之后。而且，如果已用过 `SkipWithError(...)`，则不必到达基准测试循环，可以从基准测试函数提前返回。

例如：

```c++
static void BM_test(benchmark::State& state) {
  auto resource = GetResource();
  if (!resource.good()) {
    state.SkipWithError("Resource is not good!");
    // KeepRunning() loop will not be entered.
  }
  while (state.KeepRunning()) {
    auto data = resource.read_data();
    if (!resource.good()) {
      state.SkipWithError("Failed to read data!");
      break; // Needed to skip the rest of the iteration.
    }
    do_stuff(data);
  }
}

static void BM_test_ranged_fo(benchmark::State & state) {
  auto resource = GetResource();
  if (!resource.good()) {
    state.SkipWithError("Resource is not good!");
    return; // Early return is allowed when SkipWithError() has been used.
  }
  for (auto _ : state) {
    auto data = resource.read_data();
    if (!resource.good()) {
      state.SkipWithError("Failed to read data!");
      break; // REQUIRED to prevent all further iterations.
    }
    do_stuff(data);
  }
}
```
<a name="a-faster-keep-running-loop" />

## 更快的 KeepRunning 循环

运行基准测试时，应优先使用基于范围的 for 循环，而非 `KeepRunning` 循环。例如：

```c++
static void BM_Fast(benchmark::State &state) {
  for (auto _ : state) {
    FastOperation();
  }
}
BENCHMARK(BM_Fast);
```

ranged-for 循环比 `KeepRunning` 快的原因在于：`KeepRunning` 每次迭代都要对迭代计数做一次内存加载与存储，而 ranged-for 变体能把迭代计数保持在寄存器中。

例如，基于范围 for 方法的空内循环如下：

```asm
# Loop Init
  mov rbx, qword ptr [r14 + 104]
  call benchmark::State::StartKeepRunning()
  test rbx, rbx
  je .LoopEnd
.LoopHeader: # =>This Inner Loop Header: Depth=1
  add rbx, -1
  jne .LoopHeader
.LoopEnd:
```

与之相比，空 `KeepRunning` 循环如下：

```asm
.LoopHeader: # in Loop: Header=BB0_3 Depth=1
  cmp byte ptr [rbx], 1
  jne .LoopInit
.LoopBody: # =>This Inner Loop Header: Depth=1
  mov rax, qword ptr [rbx + 8]
  lea rcx, [rax + 1]
  mov qword ptr [rbx + 8], rcx
  cmp rax, qword ptr [rbx + 104]
  jb .LoopHeader
  jmp .LoopEnd
.LoopInit:
  mov rdi, rbx
  call benchmark::State::StartKeepRunning()
  jmp .LoopBody
.LoopEnd:
```

除非需要 C++03 兼容，否则应优先使用 ranged-for 变体书写基准测试循环。

<a name="disabling-cpu-frequency-scaling" />

## 禁用 CPU 频率调节 {#disabling-cpu-frequency-scaling}

如果看到这个错误：

```
***WARNING*** CPU scaling is enabled, the benchmark real time measurements may
be noisy and will incur extra overhead.
```

你可能想在运行基准测试时禁用 CPU 频率调节，同时考虑其他让系统在基准测试期间保持稳定的办法。

更多信息参见[降低方差](reducing_variance.md)。
