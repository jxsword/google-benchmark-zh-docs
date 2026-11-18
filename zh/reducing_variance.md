---
upstream_file: reducing_variance.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 6af53228d42c15d6810fbeaf1568cf15bfbd252b
status: current
generated_by: agent
---

# 降低方差

<a name="disabling-cpu-frequency-scaling" />

## 禁用 CPU 频率调节

如果看到这个错误：

```
***WARNING*** CPU scaling is enabled, the benchmark real time measurements may be noisy and will incur extra overhead.
```

你可能想在运行基准测试时禁用 CPU 频率调节，同时考虑其他让系统在基准测试期间保持稳定的办法。

具体做法取决于 Linux 发行版、桌面环境与已安装的程序。细节会随时间漂移，因此我们不打算在此穷尽记录。

一个简单的选项是用 `cpupower` 程序把性能调节器（governor）改为 "performance"。该工具与 Linux 内核一同维护，由你的发行版提供。

必须以 root 运行，如下：

```bash
sudo cpupower frequency-set --governor performance
```

之后可以运行以下命令验证所有 CPU 都在使用 performance 调节器：

```bash
cpupower frequency-info -o proc
```

此后运行的基准测试方差会更小。

<a name="reducing-variance" />

## 禁用 ASLR

如果看到这个错误：

```
***WARNING*** ASLR is enabled, the results may have unreproducible noise in them.
```

你可能想在运行基准测试时禁用 ASLR 安全加固特性。

最简单的方式是把
```
benchmark::MaybeReenterWithoutASLR(argc, argv);
```
加为你的 `main()` 函数的第一行。它会尝试为当前处理器禁用 ASLR，成功后重新执行该二进制。注意 `personality(2)` 可能被例如 seccomp 禁止（在 Docker 容器中运行时默认如此）。

注意：如果你链接了 `benchmark_main`，它已为你完成此事。

要在 Linux 上全局禁用 ASLR，运行
```
echo 0 > /proc/sys/kernel/randomize_va_space
```

要在 Linux 上以禁用 ASLR 的方式运行单个基准测试，执行：
```
setarch `uname -m` -R ./a_benchmark
```

至于其他操作系统上如何禁用 ASLR，请参考其各自的文档。

## 降低基准测试中的方差

[上文讨论](user_guide#disabling-cpu-frequency-scaling)的 Linux CPU 频率调节器并非基准测试中唯一的噪声来源。本节的建议以桌面机或服务器为前提；在移动设备上大多不适用，且主要的方差来源也不同——参见[降低 Android 上的方差](#reducing-variance-on-android)。方差的来源包括但不限于：

1. 在多核机器上，并非所有 CPU/CPU 核心/CPU 线程都以相同速度运行，因此同一基准测试先后运行两次可能得到不同结果，取决于它运行在哪个 CPU 上。
2. 运行于 CPU 上的调节特性（如 Intel Turbo Boost、AMD Turbo Core 与 Precision Boost）即使在使用 Linux "performance" 调节器时也可能临时改变 CPU 频率。
3. CPU 间的上下文切换，或基准测试所在 CPU 上的调度竞争。
4. Intel 超线程或 AMD SMT 造成与上一条相同的问题。
5. 其他 CPU 上运行的代码造成的缓存效应。
6. 非一致性内存架构（NUMA）。

这些因素可能在单次运行内部（`--benchmark_repetitions=N`）或基准测试程序的多次运行之间造成结果方差。

降低方差来源的办法依赖操作系统与架构——这也是一些公司维护专用性能测试机器的原因之一。

一些在典型 Linux 工作站上较为容易且有效的降方差手段：

1. 按[上文讨论](user_guide#disabling-cpu-frequency-scaling)使用 performance 调节器。
2. 禁用处理器加速（boosting），方法如下：
   ```sh
   echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
   ```
   详见 Linux 内核的
   [boost.txt](https://www.kernel.org/doc/Documentation/cpu-freq/boost.txt)。
3. 把基准测试程序的任务亲和性固定到某个 CPU。例如：
   ```sh
   taskset -c 0 ./mybenchmark
   ```
4. 用 `nice` 或 `chrt` 提高程序的调度优先级以减少上下文切换：
   ```sh
   sudo nice -n -20 ./mybenchmark
   sudo chrt -f 80 ./mybenchmark
   ```
5. 禁用超线程/SMT。可在 BIOS 中进行，或使用 `/sys` 文件系统（参见 LLVM 项目的[基准测试
技巧](https://llvm.org/docs/Benchmarking.html)）。
6. 关闭其他基于定时器做重要工作的程序，例如你的浏览器、桌面环境等。
7. 把基准测试的工作集缩小到能装进 L1 缓存，但要意识到这可能导致你针对不现实的情况做优化。

关于本主题的更多资料：

1. LLVM 项目的[基准测试
   技巧](https://llvm.org/docs/Benchmarking.html)。
1. Arch Wiki 的 [CPU 频率
调节](https://wiki.archlinux.org/title/CPU_frequency_scaling)页面。

<a name="reducing-variance-on-android" />

## 降低 Android 上的方差

在 Android 上没有 `cpupower`，`scaling_governor` 通常对 `shell` 用户不可读也不可写，也没有可禁用 SMT 的 BIOS。以下操作均无需 root。

1. **等待后台应用编译结束。** Android 会在后台任务中提前编译已安装的应用，该任务以设备空闲并充电为闸条件——这正是你为做基准测试而制造的状态。该任务以 nice 值 `nice` 10 运行多个编译线程，因此很容易让出 CPU、看似无害，但 nice 过的进程不会让出内存带宽或缓存。在一台设备上，内存带宽微基准测试在该任务运行期间测得 6.35 GB/s，结束后测得 9.32 GB/s，低了 32%，两种情形下重复之间的波动均为 15%。由于该任务在整个测量期间都在运行，它会把每次重复同幅压低，基于重复间离散度的检查无法发现它。要显式检查并记录结果：
   ```sh
   adb shell pgrep dex2oat
   ```
   如果命令有输出，就等待。这里特意使用 `pgrep`：在拥有数千线程的设备上，用 `ps -A -T` 列出每个线程的开销之大，足以让 `adbd` 失去响应——以这种方式发现设备繁忙可不是什么好的体验。编译线程属于 `dex2oat`，因此按进程匹配即可。

   在零售设备上没有可靠的 *停止* 它的办法：`cmd package cancel-bg-dexopt-job` 与 `cmd package bg-dexopt-job --disable` 并非每个构建都提供，而 `cmd jobscheduler cancel android 800` 取消的是 AOSP 任务，厂商调度的编译仍在继续。`userdebug` 构建或已 root 的设备可以用 `adb shell stop` 彻底停止框架——在可用的地方这是更强的手段。

   不过可以 *等待* 它结束——这正是测试框架（harness）应该做的事，而不是靠操作者记住。下面这段会阻塞直到设备连续三次检查都安静，并与下文第 2 条结合使用：
   ```sh
   adb shell '
     busy() {  # percentage of total CPU capacity busy over a 3 second window
       set -- $(head -1 /proc/stat); t0=$(($2+$3+$4+$5+$6+$7+$8+$9)); i0=$(($5+$6))
       sleep 3
       set -- $(head -1 /proc/stat); t1=$(($2+$3+$4+$5+$6+$7+$8+$9)); i1=$(($5+$6))
       d=$((t1-t0)); echo $(( 100 * (d - (i1-i0)) / d ))
     }
     n=0
     while [ $n -lt 3 ]; do
       if [ -z "$(pgrep dex2oat)" ] && [ "$(busy)" -le 10 ]; then n=$((n+1)); else n=0; fi
     done'
   ```
2. **测量设备是否安静，而不是假设它安静。** 对 `/proc/stat` 采样两次，计算窗口内 CPU 容量的忙占比。不要用负载均值：在 Android 上它会把处于 `D` 状态的阻塞线程计入，在一台实测忙占比只有 3% 的设备上它读数却是 19 到 21。
3. **记录设备电源模式，不要臆测其作用。**
   `settings put global low_power 1` 可能把 `scaling_max_freq` 保持在满值，因此读取频率上限并不能说明该模式开启：
   ```sh
   adb shell settings get global low_power
   ```
   记录并与实际效果比对，而不是假设方向。在上面那台设备上，在空闲机器上测量、每次运行前后都采集状态，该模式没有值得报告的差异——尽管在同一部手机上更早的运行似乎显示它带来 33% 的损失，直到排除后台编译与开机后的稳定过程才澄清。
4. **重启后让设备稳定下来。** 重启四分钟后做的测量，明显不如之后在同一设备上的相同测量可复现。
5. **不要用满所有核心。** Android 自己需要核心：每核一线程的基准测试会与系统竞争，而线程在 barrier 处同步的负载在某个线程被取消调度时会急剧劣化。在一台八核设备上，内存受限的基准测试在六线程时达到峰值。
6. **小心温度。** `/sys/class/thermal` 通常需要 root，这样就只剩 `dumpsys battery`，而电池温度不能很好地代表 SoC 温度。满电设备上它跟踪的是电池充电收尾：六分钟全核计算期间它持续下降，而吞吐量保持平稳。如果要报告温度，请注明是哪个传感器。
