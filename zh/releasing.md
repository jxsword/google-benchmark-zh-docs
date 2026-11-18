---
upstream_file: releasing.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: b8ea84a0b92f2d5dec833fa3a52ba4564d80b612
status: current
generated_by: agent
---

# 如何发布

* 确认在 main 分支且已同步到 HEAD
* 确认项目可构建且测试运行
    * `parallel -j0 exec ::: test/*_test` 可以帮助确保一切至少通过
* 准备发布说明
    * `git log $(git describe --abbrev=0 --tags)..HEAD` 给出上一个附注标签到 HEAD 之间的提交列表
    * 挑最有意思的。
* 创建最后一个提交，把保存在 `CMakeLists.txt`、`MODULE.bazel`、
  `bindings/python/google_benchmark/__init__.py`、`bindings/rust/Cargo.toml` 与
  `bindings/rust/Cargo.lock` 中的版本更新为你正在创建的发布版本。
  （如果 benchmark 从你下一步创建的归档安装，将使用该版本。）

```
# CMakeLists.txt
project (benchmark VERSION 1.9.0 LANGUAGES CXX)
```

```
# MODULE.bazel
module(name = "com_github_google_benchmark", version="1.9.0")
```

```
# google_benchmark/__init__.py
__version__ = "1.9.0"
```

```toml
# bindings/rust/Cargo.toml
version = "1.9.0"
```

```toml
# bindings/rust/Cargo.lock
[[package]]
name = "google-benchmark-rs"
version = "1.9.0"
```

* 通过 GitHub 界面创建发布
    * 注意这会创建轻量标签（lightweight tag）。
    * 把它更新为附注标签（annotated tag）：
      * `git pull --tags`
      * `git tag -a -f <tag> <tag>`
      * `git push --force --tags origin`
* 确认 “Build and upload Python wheels” action 运行完成
    * 若尚未运行，请手动运行。
