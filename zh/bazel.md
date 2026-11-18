---
upstream_file: bazel.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: b5217a97e85bcdc2991b05d27f9e20a30443cf83
status: current
generated_by: agent
---

# Bazel

Google Benchmark 为基准测试库与可选的默认 `main` 函数提供 Bazel 目标：

* `@google_benchmark//:benchmark` 提供基准测试库。
* `@google_benchmark//:benchmark_main` 提供默认 `main` 函数并依赖 `@google_benchmark//:benchmark`。

当基准测试目标自定义了 `main` 函数（包括通过 `BENCHMARK_MAIN()`）时使用 `@google_benchmark//:benchmark`；当基准测试目标应使用默认 Google Benchmark 入口时使用 `@google_benchmark//:benchmark_main`。

## Bzlmod

启用 Bzlmod 后，把 Google Benchmark 加进你的 `MODULE.bazel` 文件：

```starlark
bazel_dep(name = "google_benchmark", version = "<VERSION>")
```

把 `<VERSION>` 替换为你想使用的 Google Benchmark 发布版本。

然后在 `cc_binary` 或 `cc_test` 中依赖该 Bazel 目标：

```starlark
load("@rules_cc//cc:defs.bzl", "cc_binary")

cc_binary(
    name = "string_benchmark",
    srcs = ["string_benchmark.cc"],
    deps = ["@google_benchmark//:benchmark_main"],
)
```

源文件应注册基准测试，但在链接 `@google_benchmark//:benchmark_main` 时不应调用 `BENCHMARK_MAIN()`：

```c++
#include <benchmark/benchmark.h>
#include <string>

static void BM_StringCreation(benchmark::State& state) {
  for (auto _ : state) {
    std::string empty_string;
  }
}
BENCHMARK(BM_StringCreation);
```

用 Bazel 运行基准测试：

```bash
bazel run //:string_benchmark
```

在 Bazel 的 `--` 分隔符之后传入 Google Benchmark 的 flag：

```bash
bazel run //:string_benchmark -- --benchmark_filter=StringCreation
```

## WORKSPACE

仍在使用 `WORKSPACE` 的项目可把 Google Benchmark 声明为外部仓库，并从 `bazel/benchmark_deps.bzl` 加载其依赖：

```starlark
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "google_benchmark",
    strip_prefix = "benchmark-<VERSION>",
    urls = ["https://github.com/google/benchmark/archive/refs/tags/v<VERSION>.tar.gz"],
    # Add sha256 for reproducible builds.
)

load("@google_benchmark//:bazel/benchmark_deps.bzl", "benchmark_deps")

benchmark_deps()
```

使用相同的 `<VERSION>` 值但去掉前导 `v`；归档 URL 会显式加上标签前缀。

声明仓库后，使用上文所示的目标标签：`@google_benchmark//:benchmark` 或 `@google_benchmark//:benchmark_main`。

## 性能计数器

使用 Bazel 时，在构建或运行命令中加入 `--define pfm=1` 以启用 libpfm 支持。更多细节见[性能计数器](perf_counters.md)。
