#!/usr/bin/env python3
"""iskill-app-icon · 一条命令出整套图标（跨平台真源）

    python3 scripts/make_all.py --glyph cat --color '#FF6B4A' --outdir public --name "我的应用"

做四件事：
  1) 生成矢量主件            <outdir>/favicon.svg
  2) 生成 maskable 专用源件  <outdir>/.maskable.svg（满幅底 + 内容 76%，不留接缝）
  3) 派生各尺寸 PNG          favicon-32/48 · apple-touch-icon · icon-192/512 · maskable-512
                             + favicon.ico（内嵌 16/32/48，老浏览器兼容）
  4) 生成 site.webmanifest   并打印要贴进 <head> 的片段

为什么是 .py 而不是 .sh：
  这是**唯一真源**，macOS / Windows / Linux 跑的是同一份代码 —— bash 在 Windows 上不可用，
  而在 bash 里再实现一遍逻辑必然与这份漂移。scripts/make-all.sh / make-all.ps1 / make-all.cmd
  都只是「找到解释器 → 转参数」的薄壳。

依赖：Python 3.9+，纯标准库（渲染 PNG 时另需要本机 Chromium 系浏览器，见 render_png.py）。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, os.path.join(HERE, script)] + list(args)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit("✖ %s 退出码 %d" % (script, r.returncode))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="make_all.py",
        description="一个图形 + 一个主色 → 整套可直接用的图标（SVG + 多尺寸 PNG + manifest）",
        add_help=True,
    )
    ap.add_argument("--glyph", default="whale", help="内置图形名（--list 看全部）")
    ap.add_argument("--color", default="#10C8A1", help="底板主色，明暗自动推导")
    ap.add_argument("--glyph-color", default="#FFFFFF", help="图形颜色")
    ap.add_argument("--tile", default="squircle",
                    help="底板形状：squircle / circle / square / rect / none")
    ap.add_argument("--inset", default="30", help="底板四周留白（512 画布下的单位）")
    ap.add_argument("--name", default="My App", help="应用名（写进 manifest 与 SVG title）")
    ap.add_argument("--short", default="", help="manifest short_name，缺省同 --name")
    ap.add_argument("-o", "--outdir", default="./icon-out", help="输出目录")
    ap.add_argument("--sheet", action="store_true", help="额外出一张多尺寸预览图")
    ap.add_argument("--list", action="store_true", help="列出全部内置图形后退出")
    # 其余未知参数原样透传给 make_icon.py（--flat / --scale / --cutout / --theme …）
    args, extra = ap.parse_known_args(argv)

    if args.list:
        return subprocess.run(
            [sys.executable, os.path.join(HERE, "make_icon.py"), "--list"]).returncode

    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    short = args.short or args.name
    svg = os.path.join(outdir, "favicon.svg")
    msrc = os.path.join(outdir, ".maskable.svg")

    print("▸ 1/4  生成矢量主件")
    run("make_icon.py", "--glyph", args.glyph, "--color", args.color,
        "--glyph-color", args.glyph_color, "--tile", args.tile, "--inset", args.inset,
        "--title", args.name, "--out", svg, *extra)

    print("▸ 2/4  生成 maskable 源件（满幅 rect + 内容 76%）")
    run("make_icon.py", "--glyph", args.glyph, "--color", args.color,
        "--glyph-color", args.glyph_color, "--tile", "rect", "--inset", "0",
        "--scale", "0.76", "--title", args.name, "--out", msrc, "-q")

    print("▸ 3/4  派生 PNG")
    run("render_png.py", "--svg", svg, "--maskable-svg", msrc, "--outdir", outdir,
        "--color", args.color, "--name", args.name, "--short", short, "--manifest")

    if args.sheet:
        print("▸ 额外  多尺寸预览图")
        run("render_png.py", "--svg", svg, "--sheet",
            "--sheet-out", os.path.join(outdir, "icon-sheet.png"), "-q")

    print("""
▸ 4/4  贴进 <head>：

<link rel="icon" href="/favicon.ico" sizes="48x48" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="theme-color" content="%s" />

完成后：
  · %s       ← 主件（想改图形就改 make_icon.py 里的 GLYPHS，重跑本脚本）
  · %s    ← 加 --sheet 才有，用来核对小尺寸是否还看得清
  · %s     ← 中间件，可保留供将来重新派生
""" % (args.color, svg, os.path.join(outdir, "icon-sheet.png"), msrc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
