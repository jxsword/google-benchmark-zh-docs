---
upstream_file: platform_specific_build_instructions.md
upstream_commit: 88e2febd385d65ad3d43c9d7327d36f19f2727b4
upstream_hash: 675fd6bdf8c857c1999f946ff91233120b91dd3e
status: current
generated_by: agent
---

# 平台特定构建说明

本库可用 CMake 构建系统与 Bazel 构建系统构建。

它既可以作为父构建系统的子项目构建，也可以单独构建，然后使用构建系统产出的 pkg-config `.pc` 文件链接到生成的库。此外，CMake 构建系统还会产出 CMake config。

以上即全部受支持的方式。除非有特殊情况，你不需要使用任何替代方案。

如果因故无法使用上述任何方式，你需要手动查看 `.pc` 文件，并用其中编码的信息手动调整编译器调用。
