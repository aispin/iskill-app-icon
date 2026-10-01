#!/usr/bin/env bash
# iskill-app-icon · 一条命令出整套图标
#
#   bash make-all.sh --glyph cat --color '#FF6B4A' --outdir public --name "我的应用"
#
# 做四件事：
#   1) 生成矢量主件            <outdir>/favicon.svg
#   2) 生成 maskable 专用源件  <outdir>/.maskable.svg（满幅底 + 内容 76%，不留接缝）
#   3) 派生各尺寸 PNG          favicon-16/32/48 · apple-touch-icon · icon-192/512 · maskable-512
#   4) 生成 site.webmanifest   并打印要贴进 <head> 的片段
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Python：纯标准库，任意 python3 都行 ───────────────────────
PY="${ISKILL_PYTHON:-}"
if [ -z "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="python3"
  else
    for c in "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3; do
      [ -x "$c" ] && PY="$c"
    done
  fi
fi
[ -n "$PY" ] || { echo "找不到 python3；可用 ISKILL_PYTHON=/path/to/python3 指定" >&2; exit 1; }

# ── 默认值 ────────────────────────────────────────────────────
GLYPH="whale"; COLOR="#10C8A1"; GLYPH_COLOR="#FFFFFF"; TILE="squircle"
INSET="30"; NAME="My App"; SHORT=""; OUTDIR="./icon-out"; SHEET=""
ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --glyph)       GLYPH="$2"; shift 2 ;;
    --color)       COLOR="$2"; shift 2 ;;
    --glyph-color) GLYPH_COLOR="$2"; shift 2 ;;
    --tile)        TILE="$2"; shift 2 ;;
    --inset)       INSET="$2"; shift 2 ;;
    --name)        NAME="$2"; shift 2 ;;
    --short)       SHORT="$2"; shift 2 ;;
    --outdir|-o)   OUTDIR="$2"; shift 2 ;;
    --sheet)       SHEET="1"; shift ;;
    --list)        exec "$PY" "$HERE/make_icon.py" --list ;;
    -h|--help)     sed -n '2,10p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)             ARGS+=("$1"); shift ;;
  esac
done
[ -n "$SHORT" ] || SHORT="$NAME"
mkdir -p "$OUTDIR"

echo "▸ 1/4  生成矢量主件"
"$PY" "$HERE/make_icon.py" --glyph "$GLYPH" --color "$COLOR" \
  --glyph-color "$GLYPH_COLOR" --tile "$TILE" --inset "$INSET" \
  --title "$NAME" --out "$OUTDIR/favicon.svg" "${ARGS[@]+"${ARGS[@]}"}"

echo "▸ 2/4  生成 maskable 源件（满幅 rect + 内容 76%）"
"$PY" "$HERE/make_icon.py" --glyph "$GLYPH" --color "$COLOR" \
  --glyph-color "$GLYPH_COLOR" --tile rect --inset 0 --scale 0.76 \
  --title "$NAME" --out "$OUTDIR/.maskable.svg" -q

echo "▸ 3/4  派生 PNG"
"$PY" "$HERE/render_png.py" --svg "$OUTDIR/favicon.svg" \
  --maskable-svg "$OUTDIR/.maskable.svg" --outdir "$OUTDIR" --color "$COLOR" \
  --name "$NAME" --short "$SHORT" --manifest

if [ -n "$SHEET" ]; then
  echo "▸ 额外  多尺寸预览图"
  "$PY" "$HERE/render_png.py" --svg "$OUTDIR/favicon.svg" \
    --sheet --sheet-out "$OUTDIR/icon-sheet.png" -q
fi

cat <<EOF

▸ 4/4  贴进 <head>：

<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="alternate icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="theme-color" content="$COLOR" />

完成后：
  · $OUTDIR/favicon.svg       ← 主件（想改就改 make_icon.py 里对应图形，重跑本脚本）
  · $OUTDIR/icon-sheet.png    ← 加 --sheet 才有，用来核对小尺寸是否还看得清
  · $OUTDIR/.maskable.svg     ← 中间件，可保留供将来重新派生
EOF
