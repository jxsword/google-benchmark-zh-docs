# Agent 批次翻译 Prompt 模板（agent_prompt_template.md）

> 用途: 每个翻译批次生成一份 agent 翻译任务 prompt（批次表见 PLAN §6.1）。
> 使用: 复制下方模板，替换 `{{占位符}}` 后直接作为 agent prompt。
> 同一文件的多批次**严禁并发写**（P1-a/b/c 串行，PLAN §6.1）；跨文件批次可并行。

---

## 翻译任务：{{FILE}}（批次 {{BATCH_ID}}，{{SCOPE}}）

你是 google-benchmark-zh-docs 的批次翻译 agent。严格按以下要求完成**且仅完成**本任务。

### 输入（开工前依次通读）

1. 强制规范（全文遵守，冲突时以 STYLE_GUIDE 为准）:
   - `STYLE_GUIDE.md` —— 含 7 条硬性规则（结构不动 / 受保护内容不译 / 标识符不译 /
     术语与排版 / 不增不减 / stale 只动变更段 / 自检零错误）
   - `glossary.md` —— 术语表（统一译名 + 禁用译名 + 不译清单）
2. 上游原文: `source/{{FILE}}`（本批次 {{SCOPE}} 段落 + 前后段落上下文；
   段落定位见 `manifest.yml` 的 `paragraphs` 与 `reports/` 段落 diff）
3. 产出目标: `zh/{{FILE}}` —— 若文件已存在（partial），先读既有译文，
   **只写本批次段落，不动既有译文**；
4. 批次报告输出路径: `reports/batch-{{BATCH_ID}}.md`（完成后写入）

### 任务步骤

1. 通读 STYLE_GUIDE.md 与 glossary.md 全文；
2. 对本批次段落跑占位符保护:
   ```bash
   memgate 512 python3 scripts/protect_untranslatable.py --mode protect \
     --text-file source/{{FILE}} > workdir/protect-{{BATCH_ID}}.json
   ```
3. 按段落翻译（语义等价、不增不减；标识符 / 代码 / flag / URL / 占位符不译；
   中英文之间加空格、全角标点；术语以 glossary 为准）；
4. 译文写入 `zh/{{FILE}}` 对应段落位置；文件尚不存在时，
   按以下 front-matter 开头（`{{...}}` 按实际填）:
   ```yaml
   ---
   upstream_file: {{FILE}}
   upstream_commit: <source/_upstream_commit 的 40 位 sha>
   upstream_hash: <manifest 中该文件 blob_sha>
   status: partial
   generated_by: agent
   ---
   ```
5. 自检（全部通过才算完成）:
   ```bash
   bash scripts/validate_zh.sh --file {{FILE}}            # 必须 0 error
   memgate 512 python3 scripts/fix_links.py --file {{FILE}} --apply
   ```
6. stale 修订收尾：front-matter 的 `upstream_hash` **与** `upstream_commit` 必须同时
   更新为新快照值（hash=manifest `blob_sha`，commit=`source/_upstream_commit`），
   否则 `--mark-current` 校验拒绝——两者只更新其一将无法对齐账本；
7. 写批次报告 `reports/batch-{{BATCH_ID}}.md`，固定字段（PLAN §6.2 第 3 条）:
   - 批次范围（文件 + 段落区间）；
   - 变更段清单（本批新译段落定位）；
   - 术语新增与修订建议（未收录术语 + 建议译名 + 理由）；
   - 遗留问题（原文含糊 / 疑似上游笔误与处理方式）；
   - 自检与人工抽检结果（自检命令输出摘要；抽检节选待人工填写）。

### 硬性禁区

- 禁止改动文档结构：标题层级 / 列表嵌套 / 表格行列 / 段落边界与上游一致；
- 禁止翻译 / 改动代码块、行内代码、URL、HTML 块、`{% raw %}` 标签、占位符；
- 禁止翻译 / 改动 `--benchmark_*` flag、`BENCHMARK_*` 宏、`benchmark::` 标识符、文件名；
- 禁止增删段落、合并拆分段落、重排段落顺序；
- 禁止改动 front-matter 字段名；status 只允许批次属主按阶段推进（partial → current）；
- 禁止写成繁体或日文汉字变体；
- 禁止运行 sync_upstream.py --init/--apply、人工编辑 manifest.yml（账本只由脚本读写）；
- 若同文件存在并行批次会话，立即停止并上报（写权限唯一）。
