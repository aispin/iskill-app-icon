#!/usr/bin/env bash
# iskill-app-icon · macOS / Linux 入口（薄壳）
#
# ⚠️ 这里**不实现任何逻辑** —— 真源是 scripts/make_all.py（macOS / Windows / Linux 同一份代码）。
#    在 bash 里再实现一遍，两份必然漂移。
#
# 用法：
#   bash scripts/make-all.sh --glyph whale --color '#10C8A1' --outdir public --name "我的应用" --sheet
#
# Windows 上用同目录的 make-all.ps1（或双击 make-all.cmd）。
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 找 python3：环境变量 → PATH → 常见安装位（不要写死 /Users/<name>）
PY="${ISKILL_PYTHON:-}"
if [ -z "$PY" ] || [ ! -x "$PY" ]; then
  PY="$(command -v python3 || command -v python || true)"
fi
if [ -z "$PY" ]; then
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3 \
           /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    [ -x "$c" ] && { PY="$c"; break; }
  done
fi
[ -n "$PY" ] || {
  echo "找不到 python3；可用 ISKILL_PYTHON=/path/to/python3 指定" >&2
  exit 1
}

exec "$PY" "$HERE/make_all.py" "$@"
