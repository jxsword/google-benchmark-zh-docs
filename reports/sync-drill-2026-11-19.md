# 同步演练报告：上游变更 → issue → 复译 → 合入（M6）

> 日期: 2026-11-19 ｜ 方式: /tmp 沙箱复刻仓库结构 + file:// 注入模拟上游变更
> （真上游无变更且不可等待 cron；真实 source/manifest 未受影响）
> 结论: **全链路 8 步全部跑通**，演练驱动的脚本化复现见本报告 §2

## 1. 演练范围与判据

M6 判据：「演练一次『上游改动 → issue → 复译 → 合入』全链路，报告落 reports/」。
本演练以最小仓库（单文件 random_interleaving.md）复刻 manifest/source/zh/reports 结构，
上游为本地 file:// 仓库两版（v1 原文 → v2 新增一节），驱动脚本调用与生产 workflow
完全相同的 `scripts/sync_upstream.py` API（sync_init / sync_check_or_apply / mark_current）。

## 2. 链路证据（8 步）

| # | 环节 | 结果 |
|---|---|---|
| 1 | 上游 file:// 仓库 v1 提交 | `e0880f2d` |
| 2 | `sync_init` 快照 + manifest 全量 missing | 1 文件 1 段，报告落盘 |
| 3 | 译文入库 + `mark_current` | → current（front-matter 校验通过） |
| 4 | 上游 v2（新增一节）+ `--check` | 检出 M：新增段 2/修改 0/删除 0，dry-run 未写盘 ✓ |
| 5 | `--apply` | manifest → stale ✓；工作项 + `reports/sync-2026-11-19-2ab2d37a.md` 产出 ✓ |
| 6 | 模拟 issue | 标题 `[upstream-sync] 2ab2d37a: 同步待处理`（workflow 同款格式） |
| 7 | 复译变更段 + front-matter 双字段更新 + `mark_current` | → current ✓ |
| 8 | 终态核对 | manifest 无 stale ✓ |

CI 层面的对应物是 `.github/workflows/sync-upstream.yml`（周一 UTC 02:00 cron +
workflow_dispatch），其 check → apply → commit `sync: upstream snapshot @<sha>` →
分支 `sync/<date>-<sha>` → issue 的流程与本演练逐环对应。

## 3. 演练发现的流程缺口（已修复）

1. **stale 复译收尾必须双字段更新**：front-matter 的 `upstream_hash` 与
   `upstream_commit` 需同时更新为新快照值，只更新 hash 会被 `--mark-current`
   校验拒绝（演练第 7 步首跑即触发）。已把该要求写入
   `scripts/agent_prompt_template.md` 任务步骤第 6 条。
2. 演练报告名取法瑕疵（`sorted()[-1]` 可能取到 init 报告）：仅影响演示输出，
   真实 workflow 的 issue 正文包含完整工作项清单，不受影响；记录备查。

## 4. 残余风险与运维提示

- 首次真实触发时建议用 `workflow_dispatch` 手动跑一轮，核对 issue 分支/正文格式；
- `sync-upstream.yml` 的 `GBZD_UPSTREAM_CACHE=/tmp/upstream-cache`，CI 环境无
  raw.githubusercontent.com 限制（§5.4）；
- 上游删除/结构突变按设计「报错停下、人工介入」——issue 不会自动生成，需看
  Actions 失败日志（PLAN §11 既有对策）。

## 5. 最终状态

- 全库 12 文件 `status: current`，validate 全量 0 error；
- 站点 https://jxsword.github.io/google-benchmark-zh-docs/ 在线；
- 全库单测 48 passed；三条 CI workflow 已在远程仓库生效。
