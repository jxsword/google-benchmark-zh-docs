# 批次报告：P3-a（AssemblyTests.md 全文）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/AssemblyTests.md` 全文翻译（30 段，5.3KB）：汇编测试文档——测试剖析、
  LLVM Filecheck、技巧与窍门（前缀机制）、可移植性问题（捕获变量/正则匹配）、
  现有要求与限制
- 占位符保护 32 处全保真（0 missing / 0 extra）

## 2. 变更段清单

- 新译：全文（含 Filecheck 指令语义、`CHECK_*` 前缀对 Clang/GCC 的区分、
  名字修饰禁用、x86_64 限定说明）
- 保留不译：CHECK/PCRE 指令名、`benchmark::DoNotOptimize` 等标识符、x86_64/GCC/Clang

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| name mangling → 名字修饰（name mangling） | 首现括注 |
| assembler directive → 汇编器指令 | |
| stack frame address → 栈帧地址 | |
| codegen → 代码生成 | |

## 4. 遗留问题

- 无新增；页内无 `#anchor` 互链（仅文档站间相对链接），M5 锚点注入不涉及。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 32/32 |
| 结构对等 / 链接集合 | 全部一致 |
| `validate_zh.sh --file AssemblyTests.md` | 0 error / 0 warning |
| 全库单测 | 44 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
