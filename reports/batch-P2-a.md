# 批次报告：P2-a（tools.md 全文）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/tools.md` 全文翻译（68 段，19.2KB，命令行工具文档）：compare.py 三种运行模式、
  输出解读（pvalue/mean/median/stddev/cv/GEOMEAN 逐行）、列含义六项、U 检验两节
- 占位符保护 33 处全保真（check 0 missing / 0 extra）

## 2. 变更段清单

- 新译：compare.py 依赖/仅显示聚合/三种模式全节（含 invocations 透传语义）、
  「注意：解读输出」全节（六列含义、p 值判定、颜色编码语义、统计显著性双注意）、
  U 检验节（零假设表述 + WARNING 保留）
- 保留不译：列名标签 **Benchmark:**/**Time:**/**CPU:**/**Iterations:** 等输出列名、
  行名 **benchmark/threads:1/...**、Mann–Whitney U（人名）、分隔虚线行（thematic break 原样）

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| U test → U 检验 | Mann–Whitney U 检验（人名保留） |
| null hypothesis → 零假设 | 统计语境 |
| p-value → p 值 | 首现括注 p-value |
| significance level (alpha) → 显著性水平（alpha） | |
| geometric mean → 几何平均数 | OVERALL_GEOMEAN 行 |
| statistically significant → 统计显著 | |
| filter → filter（不译） | compare.py 语境高频词，保留原文 |
| passthrough → 透传 | |
| 「switch」→ flag | glossary 禁用「开关」，tools.md 的 switch 一律译 flag |

## 4. 遗留问题

1. **protect 工具 INDENTED_CODE 模式移除（本批发现并修复）**：tools.md 编号列表的
   4–5 空格缩进正文续行（6 处）被误保护为不可译"代码"。语料实测零独立缩进代码块，
   移除该保险模式；新增回归用例 test_indented_prose_not_protected。
2. 上游笔误照录：displayment（→显示方式）、"result of said the statistical test"
   （→该统计检验的结果）、"If the calculated p-value is below this value is lower
   than…"（→若计算出的 p 值低于…）按语义译出。
3. tools.md 无页内锚点问题（无 TOC），M5 锚点注入不涉及本文件。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 33/33 |
| 结构对等 | 全部一致 |
| 链接 URL 集合 | 相等（scipy/U Test 两处，文本可译目标不变） |
| glossary 禁用译名 | 0 命中 |
| `validate_zh.sh --file tools.md` | **0 error / 0 warning，exit 0** |
| 全库单测 | 42 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
