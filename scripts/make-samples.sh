#!/usr/bin/env bash
# 重新生成 SKILL.md 里引用的样本图（assets/samples/*.svg + assets/*.png）。
#
# 用途：改动 GLYPHS、配色推导或底板算法后，跑一次让文档里的样本跟着更新。
# 用法：bash scripts/make-samples.sh [--svg-only]
#   --svg-only   只重出 SVG 源件，不渲染总览图（不需要浏览器）
#
# 幂等：覆盖 assets/samples/ 与 assets/*.png，不动其他文件。

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SAMPLES="$ROOT/assets/samples"
ASSETS="$ROOT/assets"

PY="${ISKILL_PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || {
  # 兜底候选：用 $HOME 展开，**不要写死 /Users/<name>**（写死过一次，换台机器就废）
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3 python3.13 python3 python; do
    command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
  done
}

SVG_ONLY=0
[ "${1:-}" = "--svg-only" ] && SVG_ONLY=1

mkdir -p "$SAMPLES"

echo "== 生成 SVG 源件 ==" "$SAMPLES"
gen() { "$PY" "$HERE/make_icon.py" "$@" -q; }

# 六个内置图形，各配一个合适的主色
gen --glyph whale --color '#10C8A1' --out "$SAMPLES/glyph-whale.svg"
gen --glyph cat   --color '#FF6B4A' --out "$SAMPLES/glyph-cat.svg"
gen --glyph leaf  --color '#22C55E' --out "$SAMPLES/glyph-leaf.svg"
gen --glyph bolt  --color '#7C5CFF' --out "$SAMPLES/glyph-bolt.svg"
gen --glyph orbit --color '#3B82F6' --out "$SAMPLES/glyph-orbit.svg"
gen --glyph hex   --color '#F59E0B' --out "$SAMPLES/glyph-hex.svg"

# 底板形状（同图形同色，只换 --tile）
for t in squircle circle square rect; do
  gen --glyph bolt --tile "$t" --color '#7C5CFF' --out "$SAMPLES/tile-$t.svg"
done
# none 底板：图形用主色，浅色背景上才看得见
gen --glyph bolt --tile none --color '#7C5CFF' --glyph-color '#7C5CFF' \
    --out "$SAMPLES/tile-none.svg"

# 配色玩法
gen --glyph leaf  --color '#0F172A' --glyph-color '#7CFFB2' --out "$SAMPLES/style-dark.svg"
gen --glyph orbit --color '#3B82F6' --flat --out "$SAMPLES/style-flat.svg"
gen --glyph cat   --color '#EC4899' --tile circle --out "$SAMPLES/style-circle.svg"

if [ "$SVG_ONLY" = "1" ]; then
  echo "完成（--svg-only，未渲染总览图）"
  exit 0
fi

CHROME="${CHROME:-$(ISKILL_ICON_HERE="$HERE" "$PY" -c "
import os, sys
sys.path.insert(0, os.environ['ISKILL_ICON_HERE'])
import render_png as R
print(R.find_chrome() or '')
" 2>/dev/null || true)}
if [ -z "$CHROME" ]; then
  echo "找不到 Chromium 系浏览器，跳过总览图（SVG 已生成）。" >&2
  echo "可用 CHROME=/path/to/chrome 指定后重跑。" >&2
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ── 总览图 1：六个内置图形（大图 + 32/16 缩略）──────────────────
cat > "$TMP/glyphs.html" <<HTML
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#F8FAFC;font:12px -apple-system,"PingFang SC",sans-serif;color:#475569}
.wrap{padding:28px 32px 30px}
h3{margin:0 0 4px;font-size:13px;color:#0F172A;font-weight:650;letter-spacing:.02em}
p.sub{margin:0 0 18px;font-size:11.5px;color:#94A3B8}
.row{display:flex;gap:26px;align-items:flex-start}
.c{display:flex;flex-direction:column;align-items:center;gap:8px}
.c img.big{width:112px;height:112px;display:block}
.mini{display:flex;gap:9px;align-items:flex-end}
.mini img{display:block}
.m32{width:32px;height:32px}.m16{width:16px;height:16px}
.l{font-size:11px;color:#64748B;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
</style></head><body><div class="wrap">
<h3>内置图形（默认 squircle 底板，主色各不同）</h3>
<p class="sub">主体按 512 画布设计；右下小样是同一张图缩到 32px / 16px 的样子 —— 缩到这个尺寸还认得出，才算合格。</p>
<div class="row">
HTML
for g in whale cat leaf bolt orbit hex; do
  cat >> "$TMP/glyphs.html" <<HTML
  <div class="c"><img class="big" src="file://$SAMPLES/glyph-$g.svg"><div class="l">$g</div><div class="mini"><img class="m32" src="file://$SAMPLES/glyph-$g.svg"><img class="m16" src="file://$SAMPLES/glyph-$g.svg"></div></div>
HTML
done
cat >> "$TMP/glyphs.html" <<'HTML'
</div>
</div></body></html>
HTML

# ── 总览图 2：底板形状 + 配色玩法 + 多尺寸 ─────────────────────
cat > "$TMP/tiles.html" <<HTML
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#F8FAFC;font:12px -apple-system,"PingFang SC",sans-serif;color:#475569}
.wrap{padding:28px 32px 30px}
h3{margin:0 0 4px;font-size:13px;color:#0F172A;font-weight:650;letter-spacing:.02em}
p.sub{margin:0 0 16px;font-size:11.5px;color:#94A3B8}
.row{display:flex;gap:24px;align-items:flex-start;margin-bottom:22px}
.c{display:flex;flex-direction:column;align-items:center;gap:8px}
.c img{width:100px;height:100px;display:block}
.l{font-size:11px;color:#64748B;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.lc{font-size:10px;color:#94A3B8}
.hr{height:1px;background:#E2E8F0;margin:0 0 22px}
.sz{display:flex;gap:14px;align-items:flex-end}
.sz img{display:block}.s128{width:128px;height:128px}.s64{width:64px;height:64px}.s32{width:32px;height:32px}.s16{width:16px;height:16px}
</style></head><body><div class="wrap">
<h3>底板形状</h3>
<p class="sub">同一个 bolt + 同一个主色，只换 --tile。</p>
<div class="row">
  <div class="c"><img src="file://$SAMPLES/tile-squircle.svg"><div class="l">squircle</div><div class="lc">默认</div></div>
  <div class="c"><img src="file://$SAMPLES/tile-circle.svg"><div class="l">circle</div><div class="lc">&nbsp;</div></div>
  <div class="c"><img src="file://$SAMPLES/tile-square.svg"><div class="l">square</div><div class="lc">&nbsp;</div></div>
  <div class="c"><img src="file://$SAMPLES/tile-rect.svg"><div class="l">rect</div><div class="lc">maskable 用</div></div>
  <div class="c"><img src="file://$SAMPLES/tile-none.svg"><div class="l">none</div><div class="lc">无底板</div></div>
</div>
<div class="hr"></div>
<h3>配色与叠加玩法</h3>
<p class="sub">主色只给一个，明暗两档自动推导；镂空色自动取该处底板色。</p>
<div class="row">
  <div class="c"><img src="file://$SAMPLES/style-dark.svg"><div class="l">深底 + 亮图形</div><div class="lc">--glyph-color</div></div>
  <div class="c"><img src="file://$SAMPLES/style-flat.svg"><div class="l">纯色底（无渐变）</div><div class="lc">--flat</div></div>
  <div class="c"><img src="file://$SAMPLES/style-circle.svg"><div class="l">圆形 + 换主色</div><div class="lc">--tile circle</div></div>
</div>
<div class="hr"></div>
<h3>同一张图的多尺寸表现</h3>
<p class="sub">右侧是它在 64 / 32 / 16 px 下的真实渲染 —— 这是标签页里你实际会看到的大小。</p>
<div class="sz">
  <img class="s128" src="file://$SAMPLES/glyph-whale.svg">
  <img class="s64"  src="file://$SAMPLES/glyph-whale.svg">
  <img class="s32"  src="file://$SAMPLES/glyph-whale.svg">
  <img class="s16"  src="file://$SAMPLES/glyph-whale.svg">
</div>
</div></body></html>
HTML

echo "== 渲染总览图 =="
# 只用裸 --headless：**别加 --user-data-dir**（会让 Chrome 截完不退出、挂死），
# 也别优先 --headless=new（部分 Chrome 上 GPU 进程直接 FATAL）。详见 render_png.py::shoot()。
shoot() { # page out w h
  "$CHROME" --headless --disable-gpu --no-proxy-server --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="$3,$4" \
    --screenshot="$2" "$1" >/dev/null 2>&1
}
shoot "file://$TMP/glyphs.html" "$ASSETS/sample-glyphs.png" 880 272
shoot "file://$TMP/tiles.html"  "$ASSETS/sample-tiles.png"  760 762

echo "完成："
ls -la "$ASSETS"/*.png "${SAMPLES}"/*.svg | sed 's/^/  /'
