# 批次报告：P1-a（user_guide.md 第一批）

> 日期: 2026-11-19 ｜ agent 会话: M0–M2 基建 + P1-a 同会话 ｜ 状态: 待人工抽检

## 1. 批次范围

- `zh/user_guide.md` 源文件 **L1–583**（按 H2 三等分，本批 ≈32%），共 14 个 H2 节：
  命令行 / 库 / 基准测试技巧（TOC 三节）→ 命令行选项（6 个 H3 小节全部 flag 文档）→
  输出格式 / 输出文件 / 运行基准测试 / 运行基准测试子集 / 禁用基准测试 / 结果比较 /
  额外上下文 / 运行与报告注意事项 / Setup/Teardown
- **PLAN §6.1 批次表记「§1–3」为 H2 三等分估测标记**；实际边界以 H2 三等分为准：
  P1-a = L1–583，P1-b = L584–1201（传递参数 → 自定义计数器），P1-c = L1202–末尾 + index.md
- 未译段：L584 起保留英文原文，文件 `status: partial`（PLAN §6.1 R1 完整结构纪律）

## 2. 变更段清单

- 新译：TOC 三节全部链接文本、命令行选项节 18 个 flag 条目（含 6 个 H3 小节）、
  输出格式节（console/JSON/CSV 三格式说明）、输出文件节、运行基准测试与试运行节、
  运行子集/禁用/结果比较/额外上下文节、运行与报告注意事项节（MinTime/MinWarmUpTime/
  Repetitions 交互语义）、Setup/Teardown 节
- 保留英文（按纪律）：L584 起全部段落；占位符保护覆盖 154 处
  （代码块 44 / 链接 URL 37 / 行内代码 66 / HTML 标签 7 等），还原后逐字回填

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| dry run → 试运行 | 本批新译词（`### Dry runs` 标题），建议登记 glossary |
| Loop → 循环 | 「A Faster KeepRunning Loop」语境下「循环」正确；已修正 glossary：iteration 行的禁用项「循环（指迭代次数时）」降为备注（机器不扫，抽检把关） |
| reporter 泛指 → 报告器 | 输出格式/报告选项节按 glossary 使用（类名 BenchmarkReporter 不译） |
| real time → 真实时间 | BENCHMARK_MIN_TIME 语境按 glossary；发现「实时」是「真实时间」子串，validate 已加合法词屏蔽机制（tests/test_validate.py 回归） |
| CLI switch → 命令行 flag | 避免「开关」（glossary 禁用项） |
| benchmark family → benchmark 族 | Setup/Teardown 节 |
| 「跑」单字禁用取消 | 子串误伤复合词，机器仅禁「跑分」，动词靠抽检（M2 已改） |

## 4. 遗留问题

1. **页内英文锚点将断链（M5 统一处理）**：user_guide 头部 TOC 为同页锚点
   （如 `#disabling-cpu-frequency-scaling`、`#command-line-options`），标题译后 mkdocs
   slug 改变。方案（fmt 家族同款）：M5 在 fix_links.py 增加标题 ID 注入
   （attr_list `{#英文slug}`），对全部含锚点文件一次性机械化处理；届时补 validate 检查项。
2. **上游笔误照录**：「Benchmarks binaries」「exist and is used…prevails」等语法瑕疵按
   语义翻译，未在上游开 issue（不向上游提交翻译 PR，纪律 9）。
3. **validate 残留启发式误报 1 条**：「BM_func_Arg_1_Threads_16, …」标识符列表行被记为
   未译残留（warning 级，人工确认为正确的标识符保留）。可选改进：标识符密集行（无空格
   token 占比高）跳过扫描，留待后续批次合并处理。
4. **`**Default:** (empty, uses automatic selection)`** 译作「默认值：（空，自动选择）」；
   `**Example:**`/`**Default:**` 全文统一译「**示例：**」「**默认值：**」。

## 5. 自检与人工抽检结果

### 自检（全部通过）

| 检查 | 结果 |
|---|---|
| 占位符完整性（protect check，中间产物字面比对） | 154/154，0 missing / 0 extra |
| restore 还原 | 代码块/URL/HTML 锚点逐字回填 |
| 结构对等（markdown-it：标题层级/fence/表格/列表/链接/图片/行内代码） | 全部一致 |
| 链接 URL 集合 | 与 source 归一后多重集相等 |
| glossary 禁用译名 | 0 命中 |
| `validate_zh.sh --file user_guide.md` | **0 error / 82 warning，exit 0** |
| 警告构成 | 81 条未译英文残留（partial 预期）+ 1 条标识符列表误报 |
| 全库单测 | 40 passed（新增 test_validate.py 4 用例 + protect 中间产物回归） |

### 批次期间门禁工具修复（随本批入库）

- protect `check` 模式：区分「受保护中间产物」（含占位符字面量→字面比对）与「已还原
  终稿」（重新 protect 派生比对）——修复 `[文本]({{占位符}})` 被二次包裹的假差异；
- protect `restore` 模式：兼容 `--map` 传入完整 protect JSON（自动解包 map 字段）；
- validate 术语扫描：统一译名 CJK 片段（≥3 字）先屏蔽再比对禁用词；
- glossary：iteration 行禁用项调整（见 §3）。

### 人工抽检（待填写）

- 建议抽检节：「命令行选项 → 计时与重复控制」（术语密度高）与
  「运行与报告注意事项」（长句多，语义易漂）；
- 抽检记录：＿＿＿＿（抽检人 / 节选 / 结论）
