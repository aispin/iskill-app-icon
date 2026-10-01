#!/usr/bin/env python3
"""iskill-app-icon · 零依赖图标生成器

一块圆角底板 + 一枚手绘图形 → 干净的矢量图标（SVG），再派生出各种尺寸的 PNG。

设计原则（踩过的坑，别重犯）：
  1. **不要描摹位图**。把 PNG 转成矢量会得到几千个点、几十 KB 的路径，
     还要为亚像素缝隙反复调参；手写几条贝塞尔，3~4 KB 就能更干净。
  2. **底板用超椭圆（squircle）**，不是圆角矩形。指数 n=5 最接近 iOS 连续圆角。
  3. **镂空细节（眼睛/嘴）要用"该处底板的等效色"**，才读得出是镂空而不是贴上去的。
     本脚本会按渐变轴投影自动算出来，不用手调。
  4. **细节尺度按 512 画布算**：缩到 32px 时 512 里的 16 单位只有 1px。
     想让某条线在 32px 下还看得见，它在 512 里至少要 20 单位粗。

用法：
    python3 make_icon.py --list                       # 看有哪些图形
    python3 make_icon.py --glyph whale --color '#10C8A1' --out favicon.svg
    python3 make_icon.py --glyph cat --tile circle --color '#7C5CFF' --out cat.svg
    python3 make_icon.py --glyph leaf --tile none --glyph-color '#10C8A1' --out mark.svg
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

# ─────────────────────────────────────────────────────────────
# 画布与底板几何
# ─────────────────────────────────────────────────────────────
CANVAS = 512.0
TILE_INSET = 30.0          # 底板四周留白（512 画布下），约 6%
SQUIRCLE_N = 5.0           # 超椭圆指数：2=圆，5≈iOS 连续圆角，9≈接近直角
SQUIRCLE_SAMPLES = 32      # 采样点数量；32 点已完全看不出折线

TILE_PRESETS = {
    "squircle": 5.0,
    "circle": 2.0,
    "square": 9.0,
    "rect": "rect",     # 直角矩形（--inset 0 即满幅，做 maskable 自适应图标用）
    "none": None,
}


def tile_path(n, inset: float = TILE_INSET,
              canvas: float = CANVAS, samples: int = SQUIRCLE_SAMPLES) -> str:
    """底板路径。n 为超椭圆指数（|x/a|^n + |y/b|^n = 1 → 闭合三次贝塞尔）；
    n == "rect" 返回直角矩形。"""
    if n == "rect":
        a, b = inset, canvas - inset
        return "M%s %sH%sV%sH%sZ" % (_fmt(a), _fmt(a), _fmt(b), _fmt(b), _fmt(a))

    cx = cy = canvas / 2.0
    r = canvas / 2.0 - inset
    pts = []
    for i in range(samples):
        t = 2.0 * math.pi * i / samples
        c, s = math.cos(t), math.sin(t)
        pts.append((
            cx + r * math.copysign(abs(c) ** (2.0 / n), c),
            cy + r * math.copysign(abs(s) ** (2.0 / n), s),
        ))
    return catmull_to_path(pts)


def _fmt(v: float, prec: int = 2) -> str:
    s = ("%.*f" % (prec, v)).rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def catmull_to_path(pts, prec: int = 2) -> str:
    """闭合点列 → 向心 Catmull-Rom(α=0.5) 三次贝塞尔。

    为什么必须用**向心**参数化：点距不均匀时（手工取样常这样），
    均匀参数化会在尖角处产生自交小环，渲染出洋红/白色细刺。
    """
    n = len(pts)

    def d(a, b):
        return max(math.hypot(b[0] - a[0], b[1] - a[1]), 1e-9) ** 0.5

    out = ["M%s %s" % (_fmt(pts[0][0], prec), _fmt(pts[0][1], prec))]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        d1, d2, d3 = d(p0, p1), d(p1, p2), d(p2, p3)
        d1_2, d2_2, d3_2 = d1 * d1, d2 * d2, d3 * d3
        c1 = tuple((d1_2 * p2[k] - d2_2 * p0[k] + (2 * d1_2 + 3 * d1 * d2 + d2_2) * p1[k])
                   / (3 * d1 * (d1 + d2)) for k in (0, 1))
        c2 = tuple((d3_2 * p1[k] - d2_2 * p3[k] + (2 * d3_2 + 3 * d3 * d2 + d2_2) * p2[k])
                   / (3 * d3 * (d3 + d2)) for k in (0, 1))
        out.append("C%s %s %s %s %s %s" % (
            _fmt(c1[0], prec), _fmt(c1[1], prec),
            _fmt(c2[0], prec), _fmt(c2[1], prec),
            _fmt(p2[0], prec), _fmt(p2[1], prec)))
    out.append("Z")
    return "".join(out)


# ─────────────────────────────────────────────────────────────
# 颜色工具（纯标准库，无 colour 依赖）
# ─────────────────────────────────────────────────────────────
def hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError("颜色要写成 #RGB 或 #RRGGBB：%r" % h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in rgb)


def mix(a, b, t: float):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def rgb_to_hsl(rgb):
    r, g, b = [v / 255.0 for v in rgb]
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2.0
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60.0, s, l


def hsl_to_rgb(h, s, l):
    h = (h % 360.0) / 360.0
    if s == 0:
        v = l * 255.0
        return (v, v, v)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    def hue(t):
        t = t % 1.0
        if t < 1 / 6: return p + (q - p) * 6 * t
        if t < 1 / 2: return q
        if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
        return p

    return (hue(h + 1 / 3) * 255.0, hue(h) * 255.0, hue(h - 1 / 3) * 255.0)


#: 渐变三档的锚点位置：0 → 0.52 为亮部，0.52 → 1 为暗部
STOP_MID = 0.52


def derive_stops(base_hex: str):
    """从一个主色推出一组耐看的渐变（左上提亮 → 右下压暗）。"""
    base = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(base)
    light = hsl_to_rgb(h, s * 0.99, min(0.92, l * 1.14 + 0.05))
    dark = hsl_to_rgb(h, s * 1.02, max(0.06, l * 0.60))
    return rgb_to_hex(light), rgb_to_hex(base), rgb_to_hex(dark)


def color_on_gradient(x, y, stops, bbox) -> str:
    """算出 (x,y) 处底板渐变上的等效色 —— 用作镂空细节色。

    渐变是 objectBoundingBox 的 (0,0)→(1,1) 对角，所以把点投影到对角线上取 t。
    """
    light, base, dark = stops
    x0, y0, w, h = bbox
    t = ((x - x0) / w + (y - y0) / h) / 2.0
    t = max(0.0, min(1.0, t))
    if t <= STOP_MID:
        return rgb_to_hex(mix(hex_to_rgb(light), hex_to_rgb(base), t / STOP_MID))
    return rgb_to_hex(mix(hex_to_rgb(base), hex_to_rgb(dark), (t - STOP_MID) / (1 - STOP_MID)))


# ─────────────────────────────────────────────────────────────
# 图形库
#   {G} = 图形主色（默认白）      {C} = 镂空细节色（自动按底板算）
#   每条都画在 512×512 画布上；安全区大约 x/y ∈ [96, 416]
# ─────────────────────────────────────────────────────────────
GLYPHS = {
    "whale": {
        "desc": "白鲸（头朝右、尾鳍在左、头顶气泡）",
        "cutout_at": (384, 284),
        "svg": """
    <g fill="{G}">
      <path d="M120 208C170 206 212 222 240 262C252 226 278 202 308 194C360 188 406 212 432 256C456 292 450 330 416 348C386 364 358 372 324 368C282 364 248 350 222 328C188 364 148 392 118 388C152 364 186 342 208 316C192 282 168 234 120 208Z"/>
      <circle cx="342" cy="152" r="14"/>
      <circle cx="376" cy="114" r="10"/>
      <circle cx="402" cy="80" r="7"/>
    </g>
    <circle cx="384" cy="284" r="14" fill="{C}"/>
    <path d="M344 322C368 342 398 340 416 322" fill="none" stroke="{C}" stroke-width="12" stroke-linecap="round"/>""",
    },
    "cat": {
        "desc": "猫头（两只尖耳 + 眼睛 + 鼻子）",
        "cutout_at": (256, 300),
        "svg": """
    <path fill="{G}" d="M156 166C160 210 166 240 172 268C172 330 206 372 256 372C306 372 340 330 340 268C346 240 352 210 356 166C336 190 314 206 288 212C278 206 268 202 256 202C244 202 234 206 224 212C198 206 176 190 156 166Z"/>
    <ellipse cx="214" cy="284" rx="15" ry="20" fill="{C}"/>
    <ellipse cx="298" cy="284" rx="15" ry="20" fill="{C}"/>
    <path d="M256 306L272 324L256 336L240 324Z" fill="{C}"/>""",
    },
    "leaf": {
        "desc": "叶片（尖端朝上，带主脉与侧脉）",
        "cutout_at": (256, 300),
        "svg": """
    <path fill="{G}" d="M256 128C374 186 402 314 256 384C110 314 138 186 256 128Z"/>
    <path d="M256 156L256 358" fill="none" stroke="{C}" stroke-width="11" stroke-linecap="round"/>
    <g fill="none" stroke="{C}" stroke-width="8" stroke-linecap="round">
      <path d="M256 214L206 244"/><path d="M256 214L306 244"/>
      <path d="M256 272L208 300"/><path d="M256 272L304 300"/>
    </g>""",
    },
    "bolt": {
        "desc": "闪电（能量 / 加速）",
        "cutout_at": (256, 260),
        "svg": """
    <path fill="{G}" d="M292 108L164 292L238 292L208 404L340 220L262 220Z"/>""",
    },
    "orbit": {
        "desc": "轨道环 + 卫星点（网关 / 链路）",
        "cutout_at": (256, 256),
        "svg": """
    <g transform="rotate(-24 256 256)">
      <circle cx="256" cy="256" r="146" fill="none" stroke="{G}" stroke-width="30"/>
      <circle cx="256" cy="110" r="40" fill="{G}"/>
      <circle cx="256" cy="402" r="22" fill="{G}"/>
    </g>""",
    },
    "hex": {
        "desc": "六边形环（抽象 / 科技）",
        "cutout_at": (256, 256),
        "svg": """
    <path fill="{G}" fill-rule="evenodd" d="M256 78L104 166L104 346L256 434L408 346L408 166ZM256 166L176 212L176 300L256 346L336 300L336 212Z"/>""",
    },
}


# ─────────────────────────────────────────────────────────────
# 组装
# ─────────────────────────────────────────────────────────────
def bbox_of(tile: str | None, inset: float, canvas: float):
    if tile is None:
        return (0.0, 0.0, canvas, canvas)
    return (inset, inset, canvas - 2 * inset, canvas - 2 * inset)


def build_svg(glyph: str, base: str, glyph_color: str = "#FFFFFF",
              tile: str = "squircle", inset: float = TILE_INSET,
              gradient: bool = True, cutout: str | None = None,
              clip_glyph: bool = True, title: str | None = None,
              stops_override=None, scale: float = 1.0) -> str:
    if glyph not in GLYPHS:
        raise SystemExit("未知图形 %r；可用：%s" % (glyph, ", ".join(GLYPHS)))
    if tile not in TILE_PRESETS:
        raise SystemExit("未知底板 %r；可用：%s" % (tile, ", ".join(TILE_PRESETS)))

    spec = GLYPHS[glyph]
    n = TILE_PRESETS[tile]
    d = tile_path(n, inset) if n is not None else None

    stops = stops_override or (derive_stops(base) if gradient else (base, base, base))
    box = bbox_of(d, inset, CANVAS)
    cut = cutout or (color_on_gradient(spec.get("cutout_at", (256, 256))[0],
                                       spec.get("cutout_at", (256, 256))[1], stops, box)
                     if d is not None else base)

    body = spec["svg"].replace("{G}", glyph_color).replace("{C}", cut)
    if scale != 1.0:
        h = CANVAS / 2.0
        body = ('\n      <g transform="translate(%.3f %.3f) scale(%.4f) '
                'translate(%.3f %.3f)">%s\n      </g>' % (h, h, scale, -h, -h, body))
    if clip_glyph and d is not None:
        body = '\n    <g clip-path="url(#tile)">%s\n    </g>' % body

    defs = []
    if d is not None:
        defs.append("""    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="%s"/>
      <stop offset="%s" stop-color="%s"/>
      <stop offset="1" stop-color="%s"/>
    </linearGradient>""" % (stops[0], STOP_MID, stops[1], stops[2]))
        defs.append("""    <clipPath id="tile">
      <path d="%s"/>
    </clipPath>""" % d)

    tile_el = '\n  <path d="%s" fill="url(#bg)"/>' % d if d is not None else ""
    label = title or ("%s icon" % glyph)

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="%s">
  <title>%s</title>
  <defs>
%s
  </defs>%s
  <g>%s
  </g>
</svg>
""" % (label, label, "\n".join(defs), tile_el, body)


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="make_icon.py",
        description="零依赖图标生成器：超椭圆底板 + 手绘图形 → 矢量 SVG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  %(prog)s --glyph whale --color '#10C8A1' --out favicon.svg\n"
               "  %(prog)s --glyph cat --tile circle --color '#7C5CFF' --out cat.svg\n"
               "  %(prog)s --glyph leaf --tile none --glyph-color '#10C8A1' --out mark.svg\n")
    ap.add_argument("--glyph", default="whale", help="图形名（--list 查看）")
    ap.add_argument("--color", default="#10C8A1", help="底板主色，默认 #10C8A1")
    ap.add_argument("--glyph-color", default="#FFFFFF", help="图形颜色，默认白")
    ap.add_argument("--cutout", default=None,
                    help="镂空细节色；不给则按底板渐变自动推导（推荐）")
    ap.add_argument("--tile", default="squircle", choices=list(TILE_PRESETS),
                    help="底板形状，默认 squircle")
    ap.add_argument("--inset", type=float, default=TILE_INSET,
                    help="底板四周留白，默认 30（512 画布）")
    ap.add_argument("--scale", type=float, default=1.0,
                    help="图形缩放（绕画布中心），做 maskable 时用 0.76 左右")
    ap.add_argument("--flat", action="store_true", help="底板用纯色，不加渐变")
    ap.add_argument("--no-clip", action="store_true", help="图形不被底板裁切")
    ap.add_argument("--title", default=None, help="无障碍标题（默认用图形名）")
    ap.add_argument("--theme", default=None, help="JSON 文件：{color, light, mid, dark, glyph_color}")
    ap.add_argument("--out", "-o", default="favicon.svg", help="输出 SVG 路径")
    ap.add_argument("--list", action="store_true", help="列出内置图形后退出")
    ap.add_argument("--quiet", "-q", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        print("内置图形：")
        for k, v in GLYPHS.items():
            print("  %-8s %s" % (k, v["desc"]))
        print("\n底板：%s" % " / ".join(TILE_PRESETS))
        return 0

    color, glyph_color = args.color, args.glyph_color
    stops = None
    if args.theme:
        t = json.load(open(args.theme, encoding="utf-8"))
        color = t.get("color", color)
        glyph_color = t.get("glyph_color", glyph_color)
        if "light" in t and "dark" in t:
            stops = (t["light"], t.get("mid", color), t["dark"])

    svg = build_svg(args.glyph, color, glyph_color, args.tile, args.inset,
                    gradient=not args.flat, cutout=args.cutout,
                    clip_glyph=not args.no_clip, title=args.title,
                    stops_override=stops, scale=args.scale)

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)

    if not args.quiet:
        print("已生成 %s（%d 字节）" % (out, len(svg.encode("utf-8"))))
        print("  图形 %s · 底板 %s · 主色 %s" % (args.glyph, args.tile, color))
    return 0


if __name__ == "__main__":
    sys.exit(main())
