# google-benchmark-zh-docs 翻译计划

> 版本: v1.3（2026-11-19）— 决策项 D1–D4 已经用户确认采纳推荐方案（记录见 `docs/decision_log.md` DR-001～DR-004）；v1.1→v1.3 为连续三轮复审修订，修订处内联标注（R1/R2/R3 补）
> 仓库根: `/home/ssy/soft-tech-docs-translate/google-benchmark-zh-docs`（当前非 git 仓库，M0 执行 `git init`）
> 上游基线: google/benchmark `main @ 88e2febd38`（2026-11-18 push）；docs 最后改动 commit `f6c2cc6b`（2026-11-09, PR #2369）
> 上游当前版本: v1.10.0（2026-10-14 发布）

---

## 1. 项目概览

### 1.1 目标

将 Google Benchmark（C++ 微基准测试支持库）官方文档 `docs/` 目录全部 12 个 Markdown 页面翻译为中文：
- 用 git 仓库管理，独立于上游仓库；
- 跟随官方文档持续更新（增量同步，不整篇重译）；
- 由 ZCode agent 分批完成翻译，质量门禁自动化；
- 与同族项目（fmt-zh-docs / libuv-zh-docs / spdlog-zh-docs）的工程约定保持一致。

### 1.2 范围

只翻译上游 `docs/` 目录下的文档内容：
- 12 个 `.md` 文件（共约 106 KB，2026-11-19 gh api 实测 106,487 字节）+ `assets/images/`（实测 md 正文零图片引用，assets 目前仅被 `_config.yml` logo 使用；照搬以防上游未来新增）；
- 不翻译源码注释、`README.md`、CHANGELOG（如后续用户需要可再扩展）；
- `_config.yml` 为上游 Jekyll 站点配置，中文站不直接复用（见 D3）。

### 1.3 上游文档源（链接三件套，均于 2026-11-19 实测可达）

| 项 | URL | 核实 |
|---|---|---|
| 官方文档站 | https://google.github.io/benchmark/ | 2026-11-19 WebFetch 200，11 个导航页，无语言切换、无中文版 |
| 源码仓库（文档在其中） | https://github.com/google/benchmark | 2026-11-19 gh api 正常，10,530 stars，default branch main |
| 文档目录 | https://github.com/google/benchmark/tree/main/docs | 2026-11-19 gh api contents 正常 |

文档构建方式：GitHub Pages + Jekyll（`docs/_config.yml` → `theme: jekyll-theme-minimal`），不是 mkdocs；站点直接从仓库 `docs/` 目录渲染。**没有任何官方中文翻译**，官方也未提供 i18n 框架（无 locale 目录、无翻译贡献指南）。

### 1.4 非官方声明（照搬 libuv-zh-docs 约定）

本项目为社区中文翻译，非 Google 官方项目，与 Google 无任何隶属关系。译文仅供参考；如与官方英文文档有出入，一律以官方英文文档为准。

---

## 2. 已有项目搜索结论与借鉴分析

搜索时间 2026-11-19，通道：`gh search repos` ×5 组关键词、`gh search code` ×2 组关键词、Gitee 站内搜索、WebSearch ×2（GitHub 优先）。

### 2.1 直接同类项目（Google Benchmark 文档中文翻译仓库）：**不存在**

全部搜索通道零命中：无任何以翻译 `google/benchmark` 官方 `docs/` 为目标的 GitHub / Gitee 仓库（整仓或片段均未发现）。结论：本仓库将是首个系统性中文翻译项目。

### 2.2 最接近的中文资源（教程/博客，非逐句翻译）

| 资源 | 简介 | 优点 | 缺点 | 可用性 |
|---|---|---|---|---|
| [Bencher 中文教程：Google Benchmark](https://bencher.dev/zh/learn/benchmarking/cpp/google-benchmark) | 第三方基准平台 Bencher 出的中文教程 | 实测可达（2026-11-19, HTTP 200）；结构清晰，覆盖核心用法 | 单篇教程，非完整文档翻译；带第三方平台推广色彩 | 术语参考语料 |
| [GoHalo：Google Benchmark 使用详解](https://gohalo.github.io/cn/blog/cpp-google-benchmark) | 社区博客详解 | 实测可达（2026-11-19，经代理 200；直连域名 `gohalo.com` 不可达） | 非官方、时效无保障、覆盖不全 | 术语参考语料 |
| CSDN《Google Benchmark 性能测试实战手册》等系列（apocelipes 等） | 博客园/CSDN 系列入门到进阶 | 中文社区最成体系的参考 | 实测直连 521（反爬，浏览器可访问）；非翻译，仅讲解；版权不可复制 | 仅人工参考，不进语料 |

**适用场景**：它们是"讲解类"资源，不能替代逐句翻译；借鉴价值 = 术语译法（benchmark→基准、state→状态机/迭代器状态等）作 glossary 初版语料。**选择策略**：术语分歧时以官方文档上下文自译并登记 glossary 为准，不迁就任一博客。

### 2.3 机制借鉴对象（有成熟增量同步机制的翻译工程）

| 对象 | 简介 | 优缺点 | 借鉴点 |
|---|---|---|---|
| [jxsword/fmt-zh-docs](https://github.com/jxsword/fmt-zh-docs)（自有） | mkdocs + markdown→markdown 翻译，段落级 hash 增量，全套脚本（segment/protect/translate/validate/bilingual/build）+ 4 条 CI | 优：与上游同为纯 markdown，机制完全对口；脚本可直接复用。劣：`sync_docs.py` 曾发生 2026-11-18 死循环 OOM 事故（12.4GB），复用前必须加固 | 仓库骨架、脚本族、CI 四件套、双语对照、多版本思想 |
| [jxsword/libuv-zh-docs](https://github.com/jxsword/libuv-zh-docs)（自有） | gettext PO + Sphinx 工作流，validate_po.sh 门禁，STYLE_GUIDE + glossary + 批次报告 + agent prompt 模板 | 优：治理件（风格指南/术语表/批次报告/署名）最完备。劣：PO 流程针对 Sphinx 生成源，benchmark 是纯 markdown，PO 属杀鸡用牛刀 | STYLE_GUIDE 七条硬性规则、glossary 格式、reports/ 批次报告、`agent_prompt_template.md` |
| [jxsword/spdlog-zh-docs](https://github.com/jxsword/spdlog-zh-docs)（自有，未建远程） | upstream 快照 commit + 翻译板，reports/sync-*.md | 优：快照式同步最简单可靠。劣：无段落级增量 | 快照 commit 纪律（`sync: upstream snapshot @<sha>`）、sync 报告落盘 |
| [kubernetes/website](https://github.com/kubernetes/website) `content/zh-cn/`（2026-11-19 核实，5,435 stars） | 官方 i18n：每篇 front-matter 记录上游状态，定时任务对上游 diff 开 issue | 优：front-matter 元数据模型成熟。劣：体量大、工具链重 | 每文件 front-matter 记录 `上游文件 hash + 翻译状态` 的状态机模型 |
| [mdn/translated-content](https://github.com/mdn/translated-content) `files/zh-cn/`（2026-11-19 核实） | 按 locale 目录镜像上游结构，页面元数据记录翻译质量等级 | 优：目录镜像 + 元数据的设计直观。劣：其工具链绑定 MDN 平台 | `zh/` 目录镜像上游文件名、页面级元数据 |
| [KaiserY/trpl-zh-cn](https://github.com/KaiserY/trpl-zh-cn)（2026-11-19 核实，5,673 stars） | Rust Book 中文，长期跟随上游逐章更新 | 优：证明"长期人工+工具跟随上游"可行。劣：无自动化 hash 机制，靠人工对照 | 章节批次推进的节奏感 |

**选择策略矩阵**：目标是纯 markdown 上游 + 增量同步 + agent 翻译 → **fmt-zh-docs 机制为主干**（同为 markdown、脚本现成），**libuv 治理件为补充**（风格/术语/报告/署名），**k8s front-matter 状态机做增量账本**；PO 流程（libuv 主体）不采用。

---

## 3. 核心架构决策（已确认生效，详见 docs/decision_log.md DR-001～DR-004）

| # | 决策项 | 候选 | 推荐 | 核心理由 |
|---|---|---|---|---|
| D1 | 翻译资产格式 | A. markdown→markdown（`source/` + `zh/`） B. gettext PO | **A** | 上游就是纯 markdown，A 与 fmt-zh-docs 同构、agent 直译、diff 直观；PO 需要先造 pot 抽取器，收益为负 |
| D2 | 增量同步机制 | A. 文件级 blob hash + 段落级 hash（manifest 状态机） B. 纯快照+人工对照 | **A** | 12 个文件里 user_guide 62KB，文件级粒度太粗；段落 hash 才能只重译变更段；脚本从 fmt 移植并按 §5 加固 |
| D3 | 中文站构建 | A. mkdocs Material + GitHub Actions 部署 Pages B. 镜像上游 Jekyll C. 纯仓库不建站 | **A** | 同族 fmt/libuv 已验证；上游 Jekyll 主题无法承载双语对照与搜索；B 需要维护 Ruby 环境，C 眉毛胡子一把抓 |
| D4 | 远程仓库与发布 | A. GitHub `jxsword/google-benchmark-zh-docs`（SSH）+ Pages B. 仅本地 | **A** | 与同族一致（fmt/libuv 均在 jxsword 名下且 Pages 可访问）；纯本地无法自动同步检测 |

---

## 4. 仓库结构设计

```
google-benchmark-zh-docs/
├── PLAN.md                      # 本计划
├── README.md                    # 项目说明 + 非官方声明 + 署名（M0 建）
├── LICENSE                      # Apache-2.0（与上游文档一致）
├── STYLE_GUIDE.md               # 翻译风格指南（agent 硬性规则，M2 建）
├── glossary.md                  # 术语表：统一译名/禁用译名/不译清单（M2 建）
├── mkdocs.yml                   # 中文站配置（nav 见附录 B）
├── requirements.txt             # 站点构建：mkdocs-material 等
├── requirements-dev.txt         # 脚本/测试：markdown-it-py、pyyaml、pytest
├── .gitignore                   # workdir/、site/、__pycache__/、.venv/、*.sqlite
├── manifest.yml                 # 增量账本主档（schema 见 §4.2）
├── source/                      # 上游 docs/ 逐字快照（唯一对照真相）
│   ├── _upstream_commit         # 快照对应的上游 commit（纯文本，一行 sha）
│   └── *.md …                   # 与上游 docs/ 同名同结构
├── zh/                          # 中文译文（文件名与上游一致）
│   └── *.md …                   # 每文件头部带 front-matter（见 4.1）
├── scripts/                     # 从 fmt-zh-docs 移植 + benchmark 化改造
│   ├── sync_upstream.py         # 同步：拉上游→文件级 diff→段落级 diff→生成工作项（§5）
│   ├── protect_untranslatable.py# 代码块/占位符保护
│   ├── validate_zh.sh           # 质量门禁聚合入口（§7）
│   ├── gen_bilingual.py         # 双语对照页（可选）
│   ├── fix_links.py             # 跨目录链接规范化：../README.md → 上游 GitHub 绝对 URL（借 fmt-zh-docs）
│   ├── agent_prompt_template.md # 每批次 agent 提示词模板（移植 libuv，M2 产出）
│   ├── rollback_translation.py  # 译文回滚（可选，借 fmt-zh-docs）
│   └── build_site.py            # 站点构建包装
├── tests/                       # sync/段落diff/fix_links/validate 单元测试（pytest，§5.2 第 6 条）
├── reports/                     # 每次同步/批次报告（sync-<date>-<sha>.md、batch-*.md）
├── workdir/                     # agent 批次工作区 + 上游克隆缓存（.gitignore，不入库）
└── .github/workflows/
    ├── sync-upstream.yml        # 定时同步检测（§9）
    ├── validate.yml             # PR 门禁
    └── deploy.yml               # Pages 部署
```

### 4.1 译文 front-matter（增量账本的文件内部分）

```yaml
---
upstream_file: user_guide.md        # 上游相对路径
upstream_commit: 88e2febd38         # 译文对齐的上游 commit
upstream_hash: <blob-sha1>          # 该文件快照内容的 sha
status: current                     # current | stale | partial | missing
generated_by: agent                 # 翻译方式（agent / human）
---
```

`manifest.yml` 汇总同字段（账本主档，脚本读写；front-matter 供人读与 CI 双向校验，两处不一致 → 门禁失败）。

### 4.2 manifest.yml 主档 schema（R1 补）

```yaml
schema: v1
upstream:
  remote: https://github.com/google/benchmark
  baseline_commit: 88e2febd38     # M1 首次快照时的 main HEAD
  snapshot_date: 2026-11-19
files:
  - file: user_guide.md           # 上游 docs/ 相对路径；source/ 与 zh/ 同名对应
    blob_sha: "<git blob sha1>"   # git hash-object(source/user_guide.md)，文件级变更检测依据
    size: 62568
    status: missing               # current | stale | partial | missing
    zh: zh/user_guide.md
    paragraphs: 0                 # 最近一次段落级解析分段数（示例值，M1 解析后回填）
    updated_at: 2026-11-19
  # ……其余 11 个文件同构
```

规则：`blob_sha` 与 front-matter `upstream_hash` 必须一致（不一致 → validate 门禁失败）；`status: current` 当且仅当 blob_sha 等于上游当前文件 hash；manifest 只由脚本读写，人工直改视为账本损坏、门禁报错；`about.md` 等本站自建页不进 manifest。

---

## 5. 上游同步与增量翻译机制（核心）

### 5.1 数据模型

- **文件级检测**：以 `git blob sha` 比较上游 `docs/*.md` 与 `source/*.md`——哈希不同 = 上游有变；新增/删除/改名直接识别。
- **段落级定位**：`sync_upstream.py` 用 markdown-it-py 解析新旧快照为 AST，按标题+段落顺序号生成分段 hash（移植 fmt 的 segment 思路）。新旧段落 hash 序列做 **LCS 对齐**，产出三类工作项：`新增段`（待译）、`修改段`（旧译文 + 新原文 → 复译）、`删除段`（同步删除）。
- **状态机**（写回 manifest + front-matter）：
  - `current`：upstream_hash 一致；
  - `stale`：上游变了，zh 需要修订（列出段落工作项）；
  - `partial`：批次进行中；
  - `missing`：新增文件未开译。

### 5.2 同步脚本安全纪律（吸取 2026-11-18 fmt sync_docs.py OOM 事故）

1. **必须用 `memgate` 包裹运行**（全局规则）：`memgate 2048 python3 scripts/sync_upstream.py …`——上限按最坏文件 62KB × 常数预留 2G 足够，失控只损失被限进程；
2. 输入规模硬上限：单文件 >2MB 或总解析段数 >50k 直接报错退出（上游 12 文件合计 110KB，正常永远触不到）；
3. 解析按文件分块，不把全仓库 AST 驻留内存；LCS 用 O(n·m) 以内的逐文件对齐，不做全库全对全比对；
4. 脚本自带 `--dry-run`（只打印工作项不写盘）与 `--file <name>`（单文件调试）；
5. 单元测试覆盖：新增/修改/删除/改名/乱序五种 diff 用例（写入 `tests/`，借 fmt 的 tests/ 约定）；
6. 移植自 fmt-zh-docs 的任何脚本先过一遍事故复盘审查（死循环/无界列表/递归解析三个模式），再入库。

### 5.3 同步操作流程（长期循环，§8-M6）

```
CI 每周 cron（或手动）→ sync-upstream.yml：
  1) git fetch 上游 main，检出 docs/ 到临时区
  2) 文件级 blob diff → 无变化：写一行 reports/ 即结束
  3) 有变化：更新 source/ 快照（commit: "sync: upstream snapshot @<sha>"）
     运行段落 diff → 更新 manifest（stale/missing 清单）
     生成 reports/sync-<date>-<sha>.md（含每文件变更段落清单）
     开一个 issue + 同步分支（供翻译批次认领）
人工/agent 领 issue → 按 §6 批次复译 → PR 过 §7 门禁 → manifest 回写 current
上游发新版（tag push）→ 同一流程自然覆盖，不区分"版本同步"与"日常同步"
```

改名/移动文件：blob sha 相同的删除+新增自动识别为 rename，zh/ 同步改名并保留译文，不重译。

### 5.4 同步取数与产物约定（R2 补）

- **取数方式**：`workdir/upstream/` 缓存克隆（首次 `git clone --depth 1 --single-branch https://github.com/google/benchmark`，后续 `git fetch --depth 1 origin main` 更新），文件级检测用 `git hash-object <file>` 与 manifest `blob_sha` 比对——不依赖 GitHub contents/raw API（2026-11-19 实测：本机 raw.githubusercontent.com 直连不可达、代理可达；CI 环境无此限制；本地开发取数对齐全局网络回退规则）；
- **非 md 资产**：`docs/assets/` 递归镜像进 `source/assets/`（md 正文实测零图片引用，assets 现仅 logo 使用，照搬以防上游新增），不参与段落 diff；
- **产物命名**：同步分支 `sync/<yyyymmdd>-<短sha>`；issue 标题 `[upstream-sync] <短sha>: N 文件变更（M 段新增 / K 段修订）`，正文附 `reports/sync-*.md` 摘要与批次认领清单；
- **cron**：`0 2 * * 1`（每周一 UTC 02:00）+ `workflow_dispatch` 手动触发兜底；
- **标题重组退化策略**：上游重排/合并标题导致段落 hash 序列无法对齐时，不做模糊匹配，整节退化为 delete+add 工作项（宁多译不误译）。

---

## 6. 翻译工作流（agent 批次）

### 6.1 批次划分（按优先级与单次 agent 上下文安全容量）

| 批次 | 文件（大小） | 说明 |
|---|---|---|
| P1-a | `user_guide.md` §1–3（约 1/3） | 62.6KB 巨型文件按 H2 标题切 3 批，防上下文溢出 |
| P1-b | `user_guide.md` §4–6 | 同上 |
| P1-c | `user_guide.md` §7–末尾 + `index.md`(432B) | 同上 |
| P2-a | `tools.md`（19.2KB） | 命令行工具文档，flag 多，术语密集 |
| P2-b | `reducing_variance.md`（9.5KB） | 含统计术语（variance/outlier 等，glossary 重点） |
| P3-a | `AssemblyTests.md`（5.3KB） | x86 汇编断言，技术名词密集 |
| P3-b | `perf_counters.md` + `python_bindings.md` + `random_interleaving.md`（合计 3.7KB） | 小文件合并一批 |
| P3-c | `bazel.md` + `dependencies.md` + `platform_specific_build_instructions.md` + `releasing.md`（合计 5.6KB） | 小文件合并一批 |

共 8 个 agent 批次。全文约 106 KB markdown，扣代码块后纯文本约 5–6 万字符（≈1.2–1.5 万汉字译文量）。

**执行顺序约束（R1 补）**：P1-a/b/c 三批作用于同一文件 `zh/user_guide.md`，必须**串行**执行（前一批合入并回写 manifest 后才可开下一批）；跨文件批次（P2-a/b、P3-a/b/c）彼此独立可并行。任一时刻同一文件只允许一个 agent 会话持有写权限。多批同文件期间 `zh/user_guide.md` 始终保持完整文档结构（未译段暂留英文原文，status=partial），validate 在 partial 状态下对英文残留项降级为 warning。

### 6.2 批次执行协议（每批次一个 agent 会话）

1. **开工必读**（prompt 模板固定注入）：`STYLE_GUIDE.md` 全文 + `glossary.md` 相关条目 + 本批次源文件段落 + 前后段落上下文；
2. **保护先行**：`protect_untranslatable.py` 先跑——代码块、行内代码、链接 URL、HTML 标签、命令行 flag（`--benchmark_filter` 等）替换为占位符，译文产出后还原校验；
3. **产出**：直接写 `zh/<file>.md`（含 front-matter）；每批次结束写 `reports/batch-<id>.md`，固定字段（R1 补）：批次范围 / 变更段清单 / 术语新增与修订建议 / 遗留问题 / 自检与人工抽检结果；stale 修订类批次额外附段级修订说明（改了哪些段、为什么）；
4. **自检**：批次内 agent 自跑 `validate_zh.sh --file <f>`，零错误才算完成；
5. **人工抽检**：每批次抽 1–2 节人工核对（同 libuv 抽检验收约定），记录进批次报告。

### 6.3 agent 硬性规则（写入 STYLE_GUIDE，与 libuv 七条对齐的 markdown 版）

1. front-matter 之外不得改动文档结构：标题层级、列表嵌套、表格行列与上游一致；
2. 代码块、行内代码、链接 URL、占位符原样保留，一律不译；图片路径不改（alt 文本可译）；
3. 标识符不译：函数/类型/宏/常量/文件名/命令行 flag/环境变量（`BENCHMARK_TEMPLATE` 等）；
4. 术语以 `glossary.md` 为准；中文与英文/数字之间加空格，使用全角标点；
5. 语义等价，不增不减；上游的 Note/Warning/TODO 标记语义必须保留；
6. stale 修订：先读 `reports/` 中该文件的段落 diff，只动变更段，不动既有合格译文；
7. 完成后自跑 `scripts/validate_zh.sh --file <f>` 必须零错误。

---

## 7. 质量门禁（validate_zh.sh 聚合，全部可自动执行）

| # | 检查项 | 手段 |
|---|---|---|
| 1 | front-matter schema 与 manifest 一致性 | YAML 解析比对 |
| 2 | markdown 结构对等：代码块数量与 fence 类型、标题层级序列、列表项数、表格行列 | markdown-it-py AST 对比 source/ 与 zh/ |
| 3 | 占位符完整性（保护后无丢失/新增） | 占位符集合比对 |
| 4 | 链接 URL 集合一致（仅链接文本可译）；`.md` 互链保留相对路径（zh/ 同名镜像下 mkdocs 天然解析）；`../README.md` 类跨目录链接由 fix_links.py 映射为上游 GitHub 绝对 URL（实测共 2 处，2026-11-19） | 提取比对 + fix_links 差异报告 |
| 5 | 术语扫描：禁用译名零出现、统一译名正确 | glossary.md 正则表 |
| 6 | 未翻译残留：连续英文长句启发式 + `TODO`/`FIXME` 标记 | 启发式阈值可调，报告为 warning |
| 7 | 排版：行尾空格、全角空格、中英文间距 | 正则 |
| 8 | 站点构建冒烟：mkdocs build 零 error | deploy 前置 |

双语对照页（`gen_bilingual.py`，借 fmt）为可选增强：段落级英中对照，便于人工抽检与读者对照。

---

## 8. 里程碑

| 里程碑 | 内容 | 完成判据 |
|---|---|---|
| **M0 仓库初始化** | `git init` + 按 D1–D4 建骨架目录；README（章节：项目简介 / 在线阅读 / 非官方声明 / 署名块 / 参与翻译 / 本地构建复现）+ LICENSE + .gitignore + requirements 双件；决策写入 `docs/decision_log.md` | 仓库结构落盘；首次 commit 信息尾行 `Decision: DR-001~004` |
| **M1 上游基线** | 克隆上游 docs/ 快照至 `source/`（含 `assets/`），写入 `_upstream_commit` 与 manifest 全量 `missing`；移植并加固 sync/protect/fix_links 脚本（§5.2 六条纪律 + OOM 复盘审查），`tests/` 单测就绪，跑通 dry-run | 快照 commit + 单测全绿 + dry-run 报告 |
| **M2 术语与风格** | STYLE_GUIDE.md + glossary.md 初版（种子条目见附录 A；自译定稿 + Bencher/GoHalo 术语语料参考 + 上游 flag/函数名不译清单）；`agent_prompt_template.md` 定稿；validate_zh.sh 就绪 | 三件套定稿 commit + validate 冒烟全绿 |
| **M3 翻译批次 P1** | user_guide.md 三批 + index.md | validate 全绿 + 抽检通过 |
| **M4 翻译批次 P2/P3** | 其余 5 批 | 全部文件 status=current，manifest 无 stale |
| **M5 站点与 CI** | mkdocs.yml + deploy/validate 工作流 + Pages 首次部署 | https://jxsword.github.io/google-benchmark-zh-docs/ 可访问 |
| **M6 长期同步运营** | sync-upstream.yml 周期任务启用 + 演练一次"上游改动→issue→复译→合入"全链路 | 演练报告入 reports/ |

节奏建议：M0–M2 一次会话可完成；M3–M4 按批次推进（每批次一个 agent 会话，人工抽检穿插）；M5–M6 收尾一次会话。跨会话切换时按全局「会话连续性」约定产出交接文档（落 `docs/`）与新会话启动提示词（R3 补）。

---

## 9. CI/CD（借 fmt-zh-docs 四件套裁剪为三件）

| Workflow | 触发 | 职责 |
|---|---|---|
| `sync-upstream.yml` | cron `0 2 * * 1`（周一 UTC 02:00）+ `workflow_dispatch` 手动触发 | §5.3 全流程；无变化静默，有变化开 issue + 同步分支；Actions 定时不保证准点，手动触发为常规兜底（R3 补） |
| `validate.yml` | PR / push | validate_zh.sh 全部门禁 + manifest 一致性 |
| `deploy.yml` | main push（zh/** 或站点配置变更） | mkdocs build → 部署 GitHub Pages |

注意：CI 内运行同步脚本同样受 5.2 纪律约束（规模上限、超时 step、不留无界内存增长空间）。

---

## 10. 版权与署名

- 上游 `google/benchmark` 整仓 Apache-2.0（2026-11-19 gh api 核实，`LICENSE` 位于仓库根），文档同受其约束；
- 本仓库译文按 **Apache-2.0** 发布：附 `LICENSE` 副本 + README 署名段（标题、作者=benchmark contributors、来源 URL + 基线 commit、许可）；
- 非 TASL 表（那是 libuv CC BY 4.0 的要求），但 README 保留同款署名信息块，格式对齐家族习惯；
- 教程类资源（Bencher/GoHalo/CSDN）只作术语参考，不复制其文字，无署名义务。

---

## 11. 风险与对策

| 风险 | 对策 |
|---|---|
| sync 脚本重蹈 OOM 覆辙 | §5.2 六条纪律（memgate 强制、规模上限、分块、dry-run、单测、移植审查） |
| user_guide 62KB 超 agent 上下文 | 按 H2 切 3 批 + protect 占位符压缩上下文 |
| agent 术语漂移/同词异译 | glossary + validate 术语扫描 + 人工抽检 |
| 上游迁移文档体系（换 mkdocs/拆站） | 同步脚本只依赖 `docs/*.md` 路径；每周 CI 检测天然暴露结构变化；真发生时属重大决策，走决策记录流程 |
| 上游 docs 存在 15 处 `.md` 互链 + 2 处 `../README.md` 跨目录引用（2026-11-19 经 gh api 实测修正；此前「0 互链」结论系本机 raw.githubusercontent.com 直连失败、静默空下载所致） | 互链相对路径在 zh/ 同名镜像下由 mkdocs 天然解析；跨目录链接由 fix_links.py 统一映射为上游 GitHub 绝对 URL（§7 第 4 项） |
| 长期维护断档 | manifest 状态机让任何一次同步都产出可认领的工作项清单，接手成本低（同族三仓已有先例） |
| 上游 docs 目录结构大改（新增子目录/拆站） | sync 以 `docs/*.md` + `assets/` **递归**为准（吸取 libuv-zh-docs「glob 不递归 guide/ 子目录」修复教训）；结构突变时脚本报错停下、人工介入 |
| 本机网络环境（raw.githubusercontent.com 直连不可达，2026-11-19 实测，代理可达） | 本地开发取数走 gh api / 代理（对齐全局网络回退规则）；同步脚本按 §5.4 用 git 克隆，绕开 raw 依赖；CI 环境无此问题 |

---

## 附录 A 术语表种子条目（R2 补；M2 结合全文定稿增删）

原则：技术标识符一律不译；同一英文词全文只用一个译名；社群无共识的词以官方文档语境自译并在此登记。

| 英文 | 统一译名 | 备注 |
|---|---|---|
| benchmark / microbenchmark | 基准测试 / 微基准测试 | 函数 `Benchmark()` 与类名保留原样 |
| state（`benchmark::State`） | 迭代状态 | 类名不译 |
| iteration | 迭代 | 控制台输出列 `iterations` 不译 |
| fixture | fixture | 不译（对齐 Google Test 社区习惯） |
| reporter | reporter | 类名不译；泛指时可写「报告器（reporter）」 |
| counter（`Counter`） | 计数器 | 类名不译 |
| warmup | 预热 | |
| pause / resume timing | 暂停计时 / 恢复计时 | `PauseTiming()` 等函数名不译 |
| random interleaving | 随机交错 | 上游特性专有名 |
| perf counter | 性能计数器 | |
| variance / outlier | 方差 / 离群值 | 统计语境 |
| complexity / big-O | 复杂度 / big-O | |
| throughput | 吞吐量 | |
| family / aggregation | benchmark 族 / 聚合 | 表格聚合语境 |
| command-line flag | 命令行 flag | `--benchmark_filter` 等一律不译 |
| user guide | 用户指南 | |
| dependency | 依赖 | |
| release | 发布 | |
| custom counters | 自定义计数器 | 对应上游 README §Custom Counters 锚点 |

## 附录 B mkdocs nav 映射（R1 补，M5 实施）

上游 11 页为 Jekyll 按文件名字母序排列；中文站按学习路径重排，文件名与上游保持一致：

```yaml
nav:
  - 首页: index.md
  - 用户指南: user_guide.md
  - 命令行工具: tools.md
  - 降低方差: reducing_variance.md
  - 随机交错: random_interleaving.md
  - 性能计数器: perf_counters.md
  - 汇编测试: AssemblyTests.md
  - Python 绑定: python_bindings.md
  - Bazel: bazel.md
  - 依赖: dependencies.md
  - 平台特定构建说明: platform_specific_build_instructions.md
  - 发布流程: releasing.md
  - 关于本翻译: about.md   # 本站自建页：署名/许可/基线版本；front-matter 标 generated: local，不进 manifest
```
