# 批次报告：P1-c（user_guide.md 第三批 + index.md）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）
> 本批完成后 **M3 里程碑达成**：user_guide.md 三批串行合入，全文 568 段中的
> user_guide（350 段）与 index（2 段）全部译出，status=current

## 1. 批次范围

- `zh/user_guide.md` 源文件 **L1202–末尾**（H2 三等分第三批，≈33%），共 12 个 H2 节：
  多线程基准测试（含手动多线程）→ CPU 计时器（含控制计时器）→ 手动计时 →
  设置时间单位 → 防止优化 → 统计（均值/中位数/标准差/变异系数）→ 自定义统计 →
  内存用量 → 剖析 → 使用 RegisterBenchmark → 以错误退出 → 更快的 KeepRunning 循环 →
  禁用 CPU 频率调节
- `zh/index.md`：全文翻译（H1 + 11 个导航链接），随本批入库
- 结构注记：源 L1751 的「# Loop Init」位于代码块内部（汇编示例注释），非独立标题，
  随代码块整体保留 ✓

## 2. 变更段清单

- 新译：多线程语义保证段（线程屏障行为）、ThreadRange/EnumRange/DenseRange 系列、
  手动多线程环境（工厂函数/ThreadRunner 语义）、CPU 计时器与 PauseTiming/ResumeTiming/
  ScopedPause 语义、UseManualTime/GPU 计时用例、SetTimeUnit、DoNotOptimize/ClobberMemory/
  escape 语义、Statistics 全节（Repetitions/ReportAggregatesOnly/DisplayAggregatesOnly）、
  自定义统计、ManagerMemoryProfiler 注入、Profiler 注入（含新版带名钩子）、
  RegisterBenchmark（可编程注册/可调用对象）、SkipWithError（含 ranged-for 语义）、
  ranged-for vs KeepRunning 性能说明、CPU 频率调节禁用
- index.md：11 个导航链接文本对齐 PLAN 附录 B nav 命名
- 占位符保护 102 处全保真（check 0 missing / 0 extra）

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| ranged-for / ranged-based for loop → 基于范围的 for 循环 | 保留 ranged-for 派生词 |
| profiling → 剖析 | 章节标题「剖析」 |
| thread runner → 线程运行器 | 手动多线程节 |
| escape → “逃逸”（escape） | ClobberMemory 语境，首现括注原文 |
| clobber → clobber（不译） | 库专有动词，保留原文 |
| coefficient of variation → 变异系数 | 统计节 |
| draw call → draw call（不译） | GPU 节 |
| kernel → kernel（不译） | OpenCL/CUDA 语境 |

## 4. 遗留问题

1. **页内英文锚点断链**（承 P1-a/P1-b）：本批含 `<a name>` 锚点行多处，M5 统一注入标题 ID。
2. validate 残留误报 1 条（user_guide 第 61 行起：Setup/Teardown 的 benchmark 族名列表，
   正确保留的标识符），与 P1-a 报告同一处，维持 warning 级。
3. 「## 使用 RegisterBenchmark(name, fn, args...)」标题中函数签名保留原样（规则 3），
   M5 锚点注入时该标题 slug 需一并处理。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 102/102 |
| 结构对等（H2 33 = 33；fence/表格/列表/链接全对齐） | 通过 |
| 链接 URL 集合 | 归一后多重集相等 |
| glossary 禁用译名 | 0 命中 |
| `validate_zh.sh`（全量） | **exit 0**：user_guide 0 error / 1 warning（已知误报）；index 0 error / 0 warning |
| manifest 对齐 | `sync_upstream.py --mark-current user_guide.md / index.md` 均 current（front-matter hash 校验通过） |
| 全库单测 | 42 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
