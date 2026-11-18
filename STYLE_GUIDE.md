# 翻译风格指南（STYLE_GUIDE.md）

> 版本: v1.0（2026-11-19，M2 定稿）
> 强制性: 每批次翻译 agent 开工前必读；本文件含 PLAN §6.3 的**全部 7 条 agent 硬性规则**，
> 违反任一条 → 该条目或批次不通过 `validate_zh.sh` 门禁与抽检验收。
> 本文件为 libuv-zh-docs STYLE_GUIDE 的 markdown→markdown 移植版。

## 1. Agent 硬性规则（PLAN §6.3，7 条）

1. **front-matter 之外不得改动文档结构**：标题层级、列表嵌套、表格行列与上游一致；
2. **代码块、行内代码、链接 URL、占位符原样保留**，一律不译；图片路径不改（alt 文本可译）；
3. **标识符不译**：函数 / 类型 / 宏 / 常量 / 文件名 / 命令行 flag / 环境变量（`BENCHMARK_TEMPLATE` 等）；
4. **术语以 `glossary.md` 为准**；中文与英文 / 数字之间加空格，使用全角标点；
5. **语义等价，不增不减**；上游的 Note/Warning/TODO 标记语义必须保留；
6. **stale 修订**：先读 `reports/` 中该文件的段落 diff，只动变更段，不动既有合格译文；
7. **完成后自跑 `scripts/validate_zh.sh --file <f>` 必须零错误**。

## 2. 标记保留细则（规则 2 展开）

| 标记形式 | 处理 | 示例 |
|---|---|---|
| 围栏代码块 ```…``` | 整块不译（含注释与输出示例）；fence 与语言标记不动 | |
| 行内代码 `` `…` `` | 内容整体不译 | `` `--benchmark_filter=BM_memcpy` `` |
| 链接 `[文本](URL)` | URL 原样保留，链接文本可译 | `[用户指南](user_guide.md)` |
| 图片 `![alt](路径)` | 路径不动，alt 文本可译 | |
| HTML 块（`<a name="…">`、`<!-- {% raw %} -->`） | 整行/整块原样保留不译 | 上游锚点行分布于 8 个文件 |
| Jekyll 标签 `{% raw %}` / `{% endraw %}` | 原样保留 | 常与代码块相邻出现 |
| `**加粗**` | 保留星号对数；内部普通词可译，内部标识符不译 | `**Note**` → `**注意**` |
| 斜体 `*…*` | 同加粗 | |
| front-matter（`---…---`） | 翻译批次新增/维护，字段名不译 | 见 PLAN §4.1 |

**邻接规则**：起始标记（`**`/`*`/`` ` ``）**前**与结束标记**后**必须是空白、行界或全角标点
（，。：；？！、——“”等）；结束后**不得紧跟全角开括号「（」**。违反 → 星号/反引号变字面量，
部分静默无警告。修法：标记两侧补半角空格。

**front-matter 规则**：只允许批次的属主 agent 修改本文件 front-matter；字段名
（`upstream_file`/`upstream_commit`/`upstream_hash`/`status`/`generated_by`）不译不改；
`status` 取值 `current`/`stale`/`partial`/`missing`；文件级收尾由 `sync_upstream.py
--mark-current` 校验对齐后置 manifest 为 current。

## 3. 文风细则（规则 4 展开）

1. **中英文之间加一个半角空格**：`创建 State 实例`；中文与数字之间按阅读习惯
   （`约 3 秒`、`2 个线程`——数字两侧邻接英文时各留一个空格）；
2. **全角标点**：句号「。」、逗号「，」、顿号「、」、分号「；」、冒号「：」、问号「？」、
   括号「（）」；**代码、行内代码、flag、占位符内**保持半角；
3. **列表与段落一比一**：上游一个列表项译一个列表项，不合并、不拆分、不改变嵌套深度；
4. **Note / Warning / TODO 语义保留**：`**Note:**` 译作 `**注意：**` 等，语气词不得省略；
5. **语气**：技术说明用陈述句；"Note that…" 译「注意……」「请注意……」视上下文取自然者；
   不添加原文没有的敬语或口语；
6. **英文术语夹用**：glossary §2 不译清单内的名词保留英文；其余普通词一律翻译，不中英混杂堆叠；
7. **不增不减**：不补「您」「我们」视角，不加解释性括注，不省略修饰从句；
   长句可拆中文短句但信息点一一对应；
8. **标题**：标题文本可译（如 `## Timing and Repetition Control` → `## 计时与重复控制`）；
   上游标题内代码字体部分（如 `` #### `--benchmark_dry_run` (BENCHMARK_DRY_RUN) ``）
   保留原样；`---` 分隔符译作中文破折号「——」；
9. **引号**：中文译文内引用统一用中文弯引号“”，不用「」（对齐 libuv 家族约定）。

## 4. 工作流提醒

- 翻译引擎：zcode agent；批次 prompt 用 `scripts/agent_prompt_template.md` 生成；
- 每批次一个 agent 任务；同一文件多批次**严禁并发写**（P1-a/b/c 必须串行，PLAN §6.1）；
  跨文件批次可并行；
- 批次步骤：`protect` 占位符保护 → 翻译 → `check` 占位符校验 → `restore` 还原 →
  写 `zh/<file>.md`（含 front-matter）→ `fix_links.py --apply` → 自检；
- 完成后自检命令（规则 7）：

```bash
bash scripts/validate_zh.sh --file <f>   # 必须零 error（warning 须在批次报告解释）
```

- 收尾由属主会话把 front-matter `status` 置为 `current` 后运行
  `memgate 2048 python3 scripts/sync_upstream.py --mark-current <f>` 对齐 manifest；
- 验收标准：批次报告 + validate 零 error + 人工抽检 1–2 节通过（PLAN §6.2 第 5 条）。
