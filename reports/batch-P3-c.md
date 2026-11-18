# 批次报告：P3-c（bazel + dependencies + platform_specific_build_instructions + releasing 合批）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/bazel.md`（23 段）：Bazel 目标（`::benchmark` / `::benchmark_main`）、
  Bzlmod 与 WORKSPACE 两种接入、运行与传 flag、性能计数器启用
- `zh/dependencies.md`（7 段）：构建工具依赖策略（CMake 3.13 / Python 3.10+ / nanobind）
- `zh/platform_specific_build_instructions.md`（5 段）：CMake/Bazel 构建方式与
  pkg-config 回退路径
- `zh/releasing.md`（8 段）：发布流程（版本号文件清单、发布说明、标签、
  Python wheel action）
- 占位符合计 41 处全保真

## 2. 变更段清单

- 新译：四文件全文；bazel.md 的 Bzlmod/WORKSPACE 措辞与官方术语对齐
  （附注标签 annotated tag / 轻量标签 lightweight tag）
- 保留不译：全部 Bazel 目标名、文件名（MODULE.bazel、CMakeLists.txt 等）、
  workflow 名 "Build and upload Python wheels"

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| annotated tag → 附注标签 / lightweight tag → 轻量标签 | git 术语 |
| external repository → 外部仓库 | Bazel WORKSPACE 语境 |
| subproject → 子项目 | 构建语境 |
| pkg-config → pkg-config（不译） | 工具名 |

## 4. 遗留问题

- 无新增；四文件均无页内锚点，M5 锚点注入不涉及。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 41/41 |
| 结构对等 / 链接集合 | 全部一致 |
| `validate_zh.sh`（四文件） | 各 0 error / 0 warning |
| 全库单测 | 44 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
