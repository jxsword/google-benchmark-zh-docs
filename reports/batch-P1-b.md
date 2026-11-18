# 批次报告：P1-b（user_guide.md 第二批）

> 日期: 2026-11-19 ｜ agent 会话: 远程建库 + P1-b 同会话 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/user_guide.md` 源文件 **L584–1201**（H2 三等分第二批，≈34%），共 8 个 H2 节：
  传递参数（3 个 H3：为参数命名 / 传递任意参数 / 不捕获参数命名）→
  计算渐进复杂度（big-O）→ 自定义基准测试名称 → 模板基准测试 →
  接受参数的模板基准测试 → Fixtures（含模板化 Fixtures）→ 自定义计数器（含计数器报告）
- 边界注记：计划以 L1201 为界，实测 L1200 的 `<a name="multithreaded-benchmarks"/>`
  锚点行落入本批并已保护，L1202 起为英文尾部（P1-c 范围），边界干净
- 未译段：L1202 起保留英文，文件 `status: partial`

## 2. 变更段清单

- 新译：传递参数节全节（Args/Ranges/RangeMultiplier/ArgsProduct/Combine/自定义函数）、
  参数命名节、BENCHMARK_NAMED 组、big-O 节（complexity/rms 报告语义）、
  自定义名称节、模板基准测试两节、Fixtures 两节（方法模板/非类型模板参数约束）、
  自定义计数器节（Counter 三参数构造/单位标志/多线程求和语义）、计数器报告节
- 占位符保护 105 处全保真（check 字面比对 0 missing / 0 extra）

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| sparse range → 稀疏范围 / dense range → 稠密范围 | 传递参数节成对术语 |
| range multiplier → 范围乘数 | `RangeMultiplier()` 语境 |
| asymptotic complexity → 渐进复杂度 | big-O 不译（glossary 已有） |
| normalized root-mean square error → 归一化均方根误差 | big-O 报告行 |
| multiprogramming → 多道程序设计 | 模板基准测试节（OS 术语） |
| iteration invariant → 迭代不变量 | Counter 位标志语境 |
| setup/teardown 回调语义 | 本批「invoke once per benchmark → 对每个基准测试各调用一次」沿用 |

## 4. 遗留问题

1. **protect 工具双反引号 bug（本批发现并修复，随批入库）**：源 L1197–1198 使用
   CommonMark 双反引号码段 `` ``X`` ``，旧 INLINE_CODE 正则 `` `[^`\n]+` `` 把跨段文本
   （" to " 等）误配为行内代码，产生幻影 token、还原错位与译文残留英文。
   修复：正则改为 `(?<!`)(`{1,3})(?!`)[^`\n]+?(?<!`)\1(?!`)`（1–3 反引号游程配对）。
   全库实测仅 user_guide.md 有 4 行真双反引号码段；roundtrip 复测通过（352→350 占位符，
   2 个幻影码段消失），新增回归用例 test_double_backtick_code_span。
2. **页内英文锚点断链**（承 P1-a）：本批新增锚点 `<a name="multithreaded-benchmarks"/>`
   等，M5 统一注入标题 ID 时一并处理。
3. 上游笔误照录：L1197–1198 句子本身语法断裂（"changes from X … does not have the same
   counter set as Y"），按语义译出；"``BM_Factorial``" 计数器集合对比句为最贴合意图的译法。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 105/105，0 missing / 0 extra |
| 结构对等 | 全部一致（H2 33 = 33） |
| 链接 URL 集合 | 归一后多重集相等 |
| glossary 禁用译名 | 0 命中 |
| `validate_zh.sh --file user_guide.md` | **0 error / 44 warning，exit 0**（44 条均为 P1-c 范围英文残留，预期） |
| 全库单测 | 42 passed（新增双反引号回归 + 单反引号行为保持用例） |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录于此备查。
