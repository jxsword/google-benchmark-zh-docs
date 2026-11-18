#!/usr/bin/env bash
# 译文质量门禁聚合入口（PLAN §7；逻辑实现见同目录 validate_zh.py）
# 用法:
#   bash scripts/validate_zh.sh                # 校验全部已开译文件
#   bash scripts/validate_zh.sh --file user_guide.md
#   bash scripts/validate_zh.sh --smoke        # 追加 mkdocs 构建冒烟（§7 第 8 项，deploy 前置）
# 退出码: 0 无 error；1 有 error。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# memgate 包裹为安全纪律（PLAN §5.2 第 1 条）；memgate 缺失时退化为直接运行
if command -v memgate >/dev/null 2>&1; then
  RUNNER=(memgate 2048)
else
  RUNNER=()
fi

SMOKE=0
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--smoke" ]]; then
    SMOKE=1
  else
    ARGS+=("$arg")
  fi
done

"${RUNNER[@]}" python3 "$SCRIPT_DIR/validate_zh.py" "${ARGS[@]+"${ARGS[@]}"}"

if [[ "$SMOKE" -eq 1 ]]; then
  if ! command -v mkdocs >/dev/null 2>&1; then
    echo "validate_zh: --smoke 需要 mkdocs（pip install -r requirements.txt）" >&2
    exit 2
  fi
  echo "validate_zh: mkdocs 构建冒烟…" >&2
  (cd "$SCRIPT_DIR/.." && mkdocs build --strict --site-dir site)
fi
