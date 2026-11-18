---
upstream_file: tools.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 411f41d405ffc8c4bf513c50f1396e160a6fe254
status: current
generated_by: agent
---

# 基准测试工具

## compare.py

`compare.py` 可用于比较基准测试的结果。

### 依赖
本工具依赖 [scipy](https://www.scipy.org) 包，可用 pip 安装：
```bash
pip3 install -r requirements.txt
```

### 仅显示聚合结果

flag `-a` / `--display_aggregates_only` 可用于控制普通迭代与聚合结果的显示方式。传入时会透传给被运行的基准测试可执行文件，同时本工具自身也会考虑它：只显示聚合结果，不显示普通运行。它只影响显示；各次独立运行仍会用于计算 U 检验。

### 运行模式

共有三种运行模式：

1. 仅比较两个基准测试
程序调用方式如下：

``` bash
$ compare.py benchmarks <benchmark_baseline> <benchmark_contender> [benchmark options]...
```
其中 `<benchmark_baseline>` 与 `<benchmark_contender>` 用于指定基准测试可执行文件或 JSON 输出文件。输入文件类型会自动检测。若指定基准测试可执行文件，则运行基准测试获取结果；否则直接从输出文件加载结果。

`[benchmark options]` 会传给基准测试调用。它们可以是该二进制接受的任何内容——既可以是普通的 `--benchmark_*` 参数，也可以是你的二进制特有的自定义参数。

示例输出：
```
$ ./compare.py benchmarks ./a.out ./a.out
RUNNING: ./a.out --benchmark_out=/tmp/tmprBT5nW
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:16:44
------------------------------------------------------
Benchmark               Time           CPU Iterations
------------------------------------------------------
BM_memcpy/8            36 ns         36 ns   19101577   211.669MB/s
BM_memcpy/64           76 ns         76 ns    9412571   800.199MB/s
BM_memcpy/512          84 ns         84 ns    8249070   5.64771GB/s
BM_memcpy/1024        116 ns        116 ns    6181763   8.19505GB/s
BM_memcpy/8192        643 ns        643 ns    1062855   11.8636GB/s
BM_copy/8             222 ns        222 ns    3137987   34.3772MB/s
BM_copy/64           1608 ns       1608 ns     432758   37.9501MB/s
BM_copy/512         12589 ns      12589 ns      54806   38.7867MB/s
BM_copy/1024        25169 ns      25169 ns      27713   38.8003MB/s
BM_copy/8192       201165 ns     201112 ns       3486   38.8466MB/s
RUNNING: ./a.out --benchmark_out=/tmp/tmpt1wwG_
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:16:53
------------------------------------------------------
Benchmark               Time           CPU Iterations
------------------------------------------------------
BM_memcpy/8            36 ns         36 ns   19397903   211.255MB/s
BM_memcpy/64           73 ns         73 ns    9691174   839.635MB/s
BM_memcpy/512          85 ns         85 ns    8312329   5.60101GB/s
BM_memcpy/1024        118 ns        118 ns    6438774   8.11608GB/s
BM_memcpy/8192        656 ns        656 ns    1068644   11.6277GB/s
BM_copy/8             223 ns        223 ns    3146977   34.2338MB/s
BM_copy/64           1611 ns       1611 ns     435340   37.8751MB/s
BM_copy/512         12622 ns      12622 ns      54818   38.6844MB/s
BM_copy/1024        25257 ns      25239 ns      27779   38.6927MB/s
BM_copy/8192       205013 ns     205010 ns       3479    38.108MB/s
Comparing ./a.out to ./a.out
Benchmark                 Time             CPU      Time Old      Time New       CPU Old       CPU New
------------------------------------------------------------------------------------------------------
BM_memcpy/8            +0.0020         +0.0020            36            36            36            36
BM_memcpy/64           -0.0468         -0.0470            76            73            76            73
BM_memcpy/512          +0.0081         +0.0083            84            85            84            85
BM_memcpy/1024         +0.0098         +0.0097           116           118           116           118
BM_memcpy/8192         +0.0200         +0.0203           643           656           643           656
BM_copy/8              +0.0046         +0.0042           222           223           222           223
BM_copy/64             +0.0020         +0.0020          1608          1611          1608          1611
BM_copy/512            +0.0027         +0.0026         12589         12622         12589         12622
BM_copy/1024           +0.0035         +0.0028         25169         25257         25169         25239
BM_copy/8192           +0.0191         +0.0194        201165        205013        201112        205010
```

它的工作方式是：对第一次运行中的每个基准测试，在第二次运行中查找名称完全相同的基准测试，然后比较结果。若名称不同，该基准测试不会进入 diff。
注意，`Time` 与 `CPU` 列的值按 `(new - old) / |old|` 计算。

2. 比较同一基准测试的两个不同 filter
程序调用方式如下：

``` bash
$ compare.py filters <benchmark> <filter_baseline> <filter_contender> [benchmark options]...
```
其中 `<benchmark>` 用于指定基准测试可执行文件或 JSON 输出文件。输入文件类型会自动检测。若指定基准测试可执行文件，则运行基准测试获取结果；否则直接从输出文件加载结果。

其中 `<filter_baseline>` 与 `<filter_contender>` 与传给基准测试二进制 `[--benchmark_filter=<regex>]` 参数的正则 filter 相同。

`[benchmark options]` 会传给基准测试调用。它们可以是该二进制接受的任何内容——既可以是普通的 `--benchmark_*` 参数，也可以是你的二进制特有的自定义参数。

示例输出：
```
$ ./compare.py filters ./a.out BM_memcpy BM_copy
RUNNING: ./a.out --benchmark_filter=BM_memcpy --benchmark_out=/tmp/tmpBWKk0k
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:37:28
------------------------------------------------------
Benchmark               Time           CPU Iterations
------------------------------------------------------
BM_memcpy/8            36 ns         36 ns   17891491   211.215MB/s
BM_memcpy/64           74 ns         74 ns    9400999   825.646MB/s
BM_memcpy/512          87 ns         87 ns    8027453   5.46126GB/s
BM_memcpy/1024        111 ns        111 ns    6116853    8.5648GB/s
BM_memcpy/8192        657 ns        656 ns    1064679   11.6247GB/s
RUNNING: ./a.out --benchmark_filter=BM_copy --benchmark_out=/tmp/tmpAvWcOM
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:37:33
----------------------------------------------------
Benchmark             Time           CPU Iterations
----------------------------------------------------
BM_copy/8           227 ns        227 ns    3038700   33.6264MB/s
BM_copy/64         1640 ns       1640 ns     426893   37.2154MB/s
BM_copy/512       12804 ns      12801 ns      55417   38.1444MB/s
BM_copy/1024      25409 ns      25407 ns      27516   38.4365MB/s
BM_copy/8192     202986 ns     202990 ns       3454   38.4871MB/s
Comparing BM_memcpy to BM_copy (from ./a.out)
Benchmark                               Time             CPU      Time Old      Time New       CPU Old       CPU New
--------------------------------------------------------------------------------------------------------------------
[BM_memcpy vs. BM_copy]/8            +5.2829         +5.2812            36           227            36           227
[BM_memcpy vs. BM_copy]/64          +21.1719        +21.1856            74          1640            74          1640
[BM_memcpy vs. BM_copy]/512        +145.6487       +145.6097            87         12804            87         12801
[BM_memcpy vs. BM_copy]/1024       +227.1860       +227.1776           111         25409           111         25407
[BM_memcpy vs. BM_copy]/8192       +308.1664       +308.2898           657        202986           656        202990
```

可以看到，无论在运行基准测试时还是在做 diff 之前，都会对基准测试应用 filter。为了让 diff 可用，匹配项会被替换为某个公共字符串。因此可以在同一个基准测试二进制内比较两个不同的 benchmark 族。
注意，`Time` 与 `CPU` 列的值按 `(new - old) / |old|` 计算。

3. 将基准测试一的 filter 一与基准测试二的 filter 二进行比较：
程序调用方式如下：

``` bash
$ compare.py filters <benchmark_baseline> <filter_baseline> <benchmark_contender> <filter_contender> [benchmark options]...
```

其中 `<benchmark_baseline>` 与 `<benchmark_contender>` 用于指定基准测试可执行文件或 JSON 输出文件。输入文件类型会自动检测。若指定基准测试可执行文件，则运行基准测试获取结果；否则直接从输出文件加载结果。

其中 `<filter_baseline>` 与 `<filter_contender>` 与传给基准测试二进制 `[--benchmark_filter=<regex>]` 参数的正则 filter 相同。

`[benchmark options]` 会传给基准测试调用。它们可以是该二进制接受的任何内容——既可以是普通的 `--benchmark_*` 参数，也可以是你的二进制特有的自定义参数。

示例输出：
```
$ ./compare.py benchmarksfiltered ./a.out BM_memcpy ./a.out BM_copy
RUNNING: ./a.out --benchmark_filter=BM_memcpy --benchmark_out=/tmp/tmp_FvbYg
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:38:27
------------------------------------------------------
Benchmark               Time           CPU Iterations
------------------------------------------------------
BM_memcpy/8            37 ns         37 ns   18953482   204.118MB/s
BM_memcpy/64           74 ns         74 ns    9206578   828.245MB/s
BM_memcpy/512          91 ns         91 ns    8086195   5.25476GB/s
BM_memcpy/1024        120 ns        120 ns    5804513   7.95662GB/s
BM_memcpy/8192        664 ns        664 ns    1028363   11.4948GB/s
RUNNING: ./a.out --benchmark_filter=BM_copy --benchmark_out=/tmp/tmpDfL5iE
Run on (8 X 4000 MHz CPU s)
2017-11-07 21:38:32
----------------------------------------------------
Benchmark             Time           CPU Iterations
----------------------------------------------------
BM_copy/8           230 ns        230 ns    2985909   33.1161MB/s
BM_copy/64         1654 ns       1653 ns     419408   36.9137MB/s
BM_copy/512       13122 ns      13120 ns      53403   37.2156MB/s
BM_copy/1024      26679 ns      26666 ns      26575   36.6218MB/s
BM_copy/8192     215068 ns     215053 ns       3221   36.3283MB/s
Comparing BM_memcpy (from ./a.out) to BM_copy (from ./a.out)
Benchmark                               Time             CPU      Time Old      Time New       CPU Old       CPU New
--------------------------------------------------------------------------------------------------------------------
[BM_memcpy vs. BM_copy]/8            +5.1649         +5.1637            37           230            37           230
[BM_memcpy vs. BM_copy]/64          +21.4352        +21.4374            74          1654            74          1653
[BM_memcpy vs. BM_copy]/512        +143.6022       +143.5865            91         13122            91         13120
[BM_memcpy vs. BM_copy]/1024       +221.5903       +221.4790           120         26679           120         26666
[BM_memcpy vs. BM_copy]/8192       +322.9059       +323.0096           664        215068           664        215053
```
这是前两种模式的混合：运行两个（可能不同的）基准测试二进制，并对每个应用不同的 filter。
注意，`Time` 与 `CPU` 列的值按 `(new - old) / |old|` 计算。

### 注意：解读输出

性能测量是一门艺术，性能比较更是如此。结果往往有噪声，绝对差异不一定大——仅凭肉眼观察，根本看不出两个测量是否真的显示了性能变化。多次重复基准测试时更加令人困惑。

所幸我们可以对结果做统计检验，判断性能是否发生了统计显著的变化。`compare.py`
使用 [Mann–Whitney U
检验](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test)，零假设为性能没有差异。

**下面的输出是一个基准测试比较的摘要，附带多线程进程的统计数据。**
```
Benchmark                                               Time        CPU    Time Old      Time New       CPU Old       CPU New
-----------------------------------------------------------------------------------------------------------------------------
benchmark/threads:1/process_time/real_time_pvalue     0.0000     0.0000    U Test, Repetitions: 27 vs 27
benchmark/threads:1/process_time/real_time_mean      -0.1442    -0.1442          90            77            90            77
benchmark/threads:1/process_time/real_time_median    -0.1444    -0.1444          90            77            90            77
benchmark/threads:1/process_time/real_time_stddev    +0.3974    +0.3933           0             0             0             0
benchmark/threads:1/process_time/real_time_cv        +0.6329    +0.6280           0             0             0             0
OVERALL_GEOMEAN                                      -0.1442    -0.1442           0             0             0             0
```
--------------------------------------------
以下是各行的解读：

**benchmark/threads:1/process_time/real_time_pvalue**：显示统计检验的 _p 值_，比较以单线程运行的进程的性能。0.0000 的值表明性能存在统计显著的差异。比较使用 U 检验（Mann-Whitney U 检验），每种情形各 27 次重复。

**benchmark/threads:1/process_time/real_time_mean**：显示两种情形间平均执行时间的相对差异。负值（-0.1442）表明新进程快约 14.42%。旧时间为 90 个单位，新时间为 77 个单位。

**benchmark/threads:1/process_time/real_time_median**：类似地，显示中位数执行时间的相对差异。同样，新进程快 14.44%。

**benchmark/threads:1/process_time/real_time_stddev**：这是执行时间标准差的相对差异——标准差衡量相对均值的变异或离散程度。正值（+0.3974）表明新进程的执行时间方差更大。

**benchmark/threads:1/process_time/real_time_cv**：CV 即变异系数（Coefficient of Variation），是标准差与均值之比，提供标准化的离散程度度量。增大（+0.6329）表明新进程的相对波动更大。

**OVERALL_GEOMEAN**：Geomean 即几何平均数，是一种不易受离群值影响的平均数。负值表明新进程总体有所改进。但鉴于新旧时间的值全为零，这似乎是输出中的错误或占位符。

-----------------------------------------

先来看上面 `compare.py` 基准测试输出中各列的含义：

  1. **Benchmark:** 被测函数的名称，连同输入尺寸（斜杠之后）。

  2. **Time:** 所有迭代中每次操作的平均耗时。

  3. **CPU:** 所有迭代中每次操作的平均 CPU 时间。

  4. **Iterations:** 为得到稳定估计而运行的迭代次数。

  5. **Time Old and Time New:** 表示函数在两种不同场景或版本下运行所需的平均时间。例如，可以比较对函数做某些修改前后的运行速度。

  6. **CPU Old and CPU New:** 显示函数在两种不同场景或版本下使用的平均 CPU 时间。与 Time Old and Time New 类似，但关注 CPU 占用而非整体时间。

比较部分会针对每个输入尺寸显示时间与 CPU 时间的相对差异。

统计显著的差异由 **p 值**（p-value）判定——它度量所观测到的差异仅凭随机巧合出现的概率。p 值越小，反对零假设的证据越强。

**因此：**
  1. 若 p 值小于所选的显著性水平（alpha），我们拒绝零假设，并得出基准测试显著不同的结论。
  2. 若 p 值大于等于 alpha，我们无法拒绝零假设，将两个基准测试视为相似。

该统计检验的结果还通过颜色编码传达：
```diff
+ Green:
```
  这些基准测试 _**在统计上不同**_。这可能意味着性能 **显著改进** 或 **显著退化**。应查看实际性能数字判断是哪种情况。
```diff
- Red:
```
  这些基准测试 _**在统计上相似**_。这意味着性能 **没有显著变化**。

用统计术语说，**“green”** 表示我们拒绝“性能没有差异”的零假设，**“red”** 表示我们无法拒绝零假设。如果你期待“green”表示“性能改进”、“red”表示“性能恶化”，这可能显得违反直觉。
```bash
  But remember, in this context:

    'Success' means 'successfully finding a difference'.
    'Failure' means 'failing to find a difference'.
```

另请注意：**即使**我们判定两次测量之间存在统计显著的差异，也 _未必_ 意味着被测的基准测试 **确实** 不同；反之，即使我们判定两者之间 **没有** 统计显著的差异，也未必意味着被测的基准测试 **确实没有** 不同。

### U 检验

当基准测试的重复次数足够时，工具可以进行 [U
检验](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test)——零假设为：从一个样本中随机选取的值小于或大于从第二个样本中随机选取的值的可能性相等。

若计算出的 p 值低于显著性水平 alpha，则称结果在统计上显著，拒绝零假设。换言之，两个基准测试并不相同。

**警告**：要有意义，需要 **大量**（不少于 9）次重复！
