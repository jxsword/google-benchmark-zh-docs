# 决策记录（google-benchmark-zh-docs）

> 依据全局协作约定维护；编号递增，被替代条目不改旧文、只改状态。

## DR-001 2026-11-19 翻译资产采用 markdown→markdown（source/ 快照 + zh/ 同名译文） [状态: 生效]
- 背景: 上游 google/benchmark docs/ 为纯 markdown（12 文件约 110KB，Jekyll 直接渲染），需确定翻译资产的组织形式
- 选项与权衡: markdown→markdown(与上游同构、agent 直译、复用 fmt-zh-docs 现成脚本族，选它); gettext PO(段落级合并能力强，弃用理由: 需先为纯 markdown 上游造 pot 抽取器，工程开销大收益为负)
- 结论: 采用 markdown→markdown：`source/` 存上游逐字快照，`zh/` 存同名译文
- 理由: 与上游格式同构、与同族 fmt-zh-docs 机制完全对口，脚本现成
- 影响: 仓库骨架 source/、zh/、scripts/；不引入 locale/ 与 .po 文件
- 记录时间 / 会话: 2026-11-19 / google-benchmark-zh-docs 翻译计划会话

## DR-002 2026-11-19 增量同步采用文件 blob hash + 段落级 hash + manifest 状态机 [状态: 生效]
- 背景: user_guide.md 62.6KB 单文件过粗，需长期跟随上游只重译变更段
- 选项与权衡: 段落hash+manifest(blob hash 检测变更 + markdown-it-py 段落 hash + LCS 对齐产出工作项，状态机 current/stale/partial/missing，选它); 文件级快照+人工对照(spdlog 模式最简可靠，弃用理由: 62KB 文件整篇重译浪费大)
- 结论: 文件级 blob hash 检测 → 段落级 hash 对齐 → manifest/front-matter 状态机
- 理由: 长期维护成本最低，工作项自动产出、可认领
- 影响: scripts/sync_upstream.py、manifest.yml、front-matter schema、CI sync-upstream.yml
- 安全纪律: 移植 fmt-zh-docs 脚本前过 OOM 复盘审查（2026-11-18 事故），运行强制 memgate 包裹
- 记录时间 / 会话: 2026-11-19 / google-benchmark-zh-docs 翻译计划会话

## DR-003 2026-11-19 中文站采用 mkdocs Material + GitHub Actions 部署 Pages [状态: 生效]
- 背景: 需要对外阅读站点，上游为 Jekyll（jekyll-theme-minimal）直接渲染 docs/
- 选项与权衡: mkdocs Material(同族 fmt-zh-docs 已验证、自带搜索、可扩展双语对照页，选它); 镜像上游 Jekyll(需维护 Ruby 环境、无搜索/双语能力，弃用); 纯仓库不建站(省事但阅读体验差、失去 Pages 构建验证，弃用)
- 结论: mkdocs Material + deploy.yml 自动部署
- 理由: 同族已验证、功能承载能力最强、维护面最小
- 影响: mkdocs.yml、requirements.txt、.github/workflows/deploy.yml
- 记录时间 / 会话: 2026-11-19 / google-benchmark-zh-docs 翻译计划会话

## DR-004 2026-11-19 远程仓库建在 GitHub jxsword 名下并启用 Pages [状态: 生效]
- 背景: 需确定发布通道与自动同步检测的载体
- 选项与权衡: GitHub jxsword/google-benchmark-zh-docs(与 fmt/libuv 同族命名一致、CI 定时同步检测、Pages 发布，选它); 仅本地暂不建远程(省事，弃用理由: 失去自动同步检测与 Pages 验证，手动脚本易漏)
- 结论: git@github.com:jxsword/google-benchmark-zh-docs.git + GitHub Pages
- 理由: 与既有家族项目保持一致，基础设施可复用
- 影响: git remote 配置、Pages 设置、每周 sync-upstream cron 生效
- 记录时间 / 会话: 2026-11-19 / google-benchmark-zh-docs 翻译计划会话
