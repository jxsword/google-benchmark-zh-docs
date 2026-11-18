---
upstream_file: random_interleaving.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: c083036841480796c0565ffa36c7e02bd32e06b2
status: current
generated_by: agent
---

<a name="interleaving" />

# 随机交错

[随机交错](https://github.com/google/benchmark/issues/1051)是一种降低运行间方差的技术。它把一个微基准测试的重复与同一基准测试程序中其他微基准测试的重复随机交错。数据显示它平均能把运行间方差降低
[40%](https://github.com/google/benchmark/issues/1051)。

使用时主要需要设置 `--benchmark_enable_random_interleaving=true`，
并可选地指定非零重复次数 `--benchmark_repetitions=9`，
还可选地缩短每次重复的时间 `--benchmark_min_time=0.1`。
