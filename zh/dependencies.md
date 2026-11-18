---
upstream_file: dependencies.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: fdb7f19b2fe1719d8b48cbbb84d35384bce45725
status: current
generated_by: agent
---

# 构建工具依赖策略

我们的构建工具遵循 [Foundational C++ 支持策略](https://opensource.google/documentation/policies/cplusplus-support)。特别是其中的[“构建系统”一节](https://opensource.google/documentation/policies/cplusplus-support#build-systems)。

## CMake

截至 2024-10-24，当前支持的版本为 CMake 3.13。多数现代发行版带有更新的版本，例如：

* Ubuntu 20.04 提供 CMake 3.16.3
* Debian 11.4 提供 CMake 3.18.4
* Ubuntu 22.04 提供 CMake 3.22.1

## Python

自 v1.9.0（2024-08-16）起，从 PyPI 安装 Python 绑定要求 Python 3.10+。对更旧版本，从源码构建大概率仍然可行。如何从源码构建参见[用户指南](python_bindings.md)。
理论支持的最小版本为 Python 3.8，因为所用绑定生成器（nanobind）只支持 Python 3.8+。
