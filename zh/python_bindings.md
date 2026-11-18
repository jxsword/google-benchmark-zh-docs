---
upstream_file: python_bindings.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 718d1079ff64bb2111cd5d63e1a997fa1b98f7ff
status: current
generated_by: agent
---

# 构建并安装 Python 绑定

Python 绑定已以 wheel 形式发布在 [PyPI](https://pypi.org/project/google-benchmark/) 上，可在 Python 中直接导入并使用 Google Benchmark。
目前提供 macOS（ARM64 与 Intel x86 两种）、Linux x86-64 与 64 位 Windows 的预构建 wheel。
支持的 Python 版本为 Python 3.10 - 3.15，包括 Python 3.14t 与 3.15t 的自由线程构建。

安装 Google Benchmark 的 Python 绑定，运行：

```bash
python -m pip install --upgrade pip  # for manylinux2014 support
python -m pip install google-benchmark
```

为保持系统 Python 解释器干净，建议在虚拟环境中执行这些命令。如何创建虚拟环境，参见 [Python 官方文档](https://docs.python.org/3/library/venv.html)。

要直接从源码构建 wheel，可按以下步骤操作：
```bash
git clone https://github.com/google/benchmark.git
cd benchmark
# create a virtual environment and activate it
python3 -m venv venv --system-site-packages
source venv/bin/activate  # .\venv\Scripts\Activate.ps1 on Windows

# upgrade Python's system-wide packages
python -m pip install --upgrade pip build
# builds the wheel and stores it in the directory "dist".
python -m build
```

注意：从源码构建 wheel 需要 Bazel。各平台安装 Bazel 的说明，参见 [Bazel 安装文档](https://bazel.build/install)。
