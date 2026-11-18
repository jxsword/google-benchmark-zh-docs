# 批次报告：P2-b（reducing_variance.md 全文）

> 日期: 2026-11-19 ｜ agent 会话: 同前 ｜ 状态: 用户已指示抽检忽略（2026-11-19）

## 1. 批次范围

- `zh/reducing_variance.md` 全文翻译（54 段，9.5KB）：禁用 CPU 频率调节 / 禁用 ASLR /
  降低基准测试中的方差（噪声来源 6 项 + 降方差手段 7 项 + 延伸资料）/ 降低 Android 上的
  方差（6 项实测经验，含后台编译、忙占比采样、电源模式、重启稳定、核心数、温度）
- 占位符保护 46 处全保真（check 0 missing / 0 extra；1 处凭记忆抄错的 token 被校验器
  当场拦截修正——占位符 hash 机制的直接收益）

## 2. 变更段清单

- 新译：governor/performance 设置与验证、ASLR 禁用（全局/单次/Docker 注意）、
  方差来源清单、七项降方差手段（含 boost.txt/taskset/chrt/nice 语义）、
  Android 六项（后台编译对内存带宽的 32% 影响、负载均值陷阱、电源模式记录、
  核心数取舍、温度传感器语义）
- 保留不译：*stop*/*wait* 斜体强调、Intel/AMD/LLVM/Arch Wiki/SoC/AOSP 等专名、
  全部命令与代码块

## 3. 术语新增与修订建议

| 提议 | 说明 |
|---|---|
| governor → 调节器（governor） | CPU 频率调节器，首现括注 |
| ASLR → ASLR（不译） | 安全机制专名 |
| boosting → 加速（boosting） | 处理器加速特性 |
| task affinity → 任务亲和性 | |
| busy fraction → 忙占比 | Android 采样语境 |
| power mode → 电源模式 | |
| harness → 测试框架（harness） | 首现括注 |
| descheduled → 取消调度 | barrier 语境 |
| barrier → barrier（不译） | 同步原语 |

## 4. 遗留问题与门禁修复（随批入库）

1. **validate 残留启发式 URL 误报修复**：链接续行的 URL 字母把合法中文行的 CJK 占比
   拉低（实测「技巧](https://llvm.org/docs/Benchmarking.html)」续行触发）；修复为扫描前
   剥离 URL，新增回归用例 test_residue_strips_urls（真英文段落仍被检出）。
2. **glossary 子串误报第二例**：「发行」是「发行版」（distribution 正译）的子串——与
   「实时⊂真实时间」同类；按既有屏蔽机制在 glossary 增加 distribution 行解决。
3. 本文件无页内锚点，M5 锚点注入不涉及。

## 5. 自检结果

| 检查 | 结果 |
|---|---|
| 占位符完整性 | 46/46 |
| 结构对等 / 链接集合 | 全部一致 |
| glossary 禁用译名 | 0 命中 |
| `validate_zh.sh --file reducing_variance.md` | **0 error / 0 warning，exit 0** |
| 全量 validate（12 文件） | exit 0 |
| 全库单测 | 43 passed |

### 人工抽检

- 用户指示抽检忽略（2026-11-19 会话指令），记录备查。
