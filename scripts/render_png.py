#!/usr/bin/env python3
"""iskill-app-icon · SVG → 多尺寸 PNG 派生件

用本机已装的 Chromium 系浏览器做**无头渲染**，不需要任何 Python 图形库。

产出（默认全部）：
    favicon-16.png / favicon-32.png / favicon-48.png   透明底，给浏览器标签页
    apple-touch-icon.png (180)                        不透明底（iOS 会盖自己的圆角遮罩）
    icon-192.png / icon-512.png                        透明底，给 PWA manifest
    maskable-512.png                                   满幅底 + 内容缩到 80%（Android 自适应图标）

用法：
    python3 render_png.py --svg favicon.svg --outdir public --color '#10C8A1'
    python3 render_png.py --svg favicon.svg --sheet                 # 只出多尺寸预览图
    CHROME=/path/to/chrome python3 render_png.py --svg icon.svg
"""
from __future__ import annotations

import argparse
import glob
import html
import os
import shutil
import subprocess
import sys
import tempfile

CANVAS = 512

CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    os.path.expanduser("~/.agent-browser/browsers/chrome-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
    os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"),
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]


def find_chrome() -> str | None:
    for c in CANDIDATES:
        if not c:
            continue
        for p in glob.glob(c):
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
    return None


def shoot(chrome: str, page: str, out: str, w: int, h: int, transparent: bool) -> None:
    cmd = [chrome, "--headless", "--disable-gpu", "--no-proxy-server",
           "--hide-scrollbars", "--force-device-scale-factor=1",
           "--virtual-time-budget=2500", "--window-size=%d,%d" % (w, h),
           "--screenshot=" + os.path.abspath(out)]
    if transparent:
        cmd.append("--default-background-color=00000000")
    cmd.append("file://" + os.path.abspath(page))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        raise SystemExit("截图失败（%dx%d）：\n%s\n%s" % (w, h, r.stdout[-800:], r.stderr[-800:]))


def page_for(svg: str, size: int, bg: str | None, scale: float = 1.0,
             pad: float = 0.0) -> str:
    """写一个只含单张图的最小 HTML 页。scale=内容占画布比例（maskable 用 0.8）。"""
    inner = size * scale
    off = (size - inner) / 2.0
    body_bg = bg if bg else "transparent"
    return """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;width:100%%;height:100%%;overflow:hidden;background:%s}
img{position:absolute;left:%.3fpx;top:%.3fpx;width:%.3fpx;height:%.3fpx;display:block}
</style></head><body><img src="%s"></body></html>
""" % (body_bg, off, off, inner, inner, html.escape(os.path.abspath(svg), quote=True))


def write_page(tmpdir: str, name: str, content: str) -> str:
    p = os.path.join(tmpdir, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


SHEET_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#F8FAFC;font:13px -apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
color:#334155;padding:26px;display:flex;align-items:flex-end;gap:26px}
.cell{display:flex;flex-direction:column;align-items:center;gap:8px}
.lbl{font-size:11px;color:#94A3B8;letter-spacing:.05em}
.row{display:flex;align-items:flex-end;gap:12px}
</style></head><body>
<div class="cell"><img src="%s" style="width:160px;height:160px"><div class="lbl">160</div></div>
<div class="cell"><img src="%s" style="width:96px;height:96px"><div class="lbl">96</div></div>
<div class="cell"><img src="%s" style="width:64px;height:64px"><div class="lbl">64</div></div>
<div class="cell"><img src="%s" style="width:32px;height:32px"><div class="lbl">32</div></div>
<div class="cell"><img src="%s" style="width:16px;height:16px"><div class="lbl">16</div></div>
</body></html>
"""

MANIFEST_TPL = """{
  "name": "%(name)s",
  "short_name": "%(short)s",
  "start_url": "./",
  "display": "standalone",
  "background_color": "%(color)s",
  "theme_color": "%(color)s",
  "icons": [
    { "src": "./icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "./icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "./maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="render_png.py",
                                 description="把 SVG 图标渲染成各尺寸 PNG")
    ap.add_argument("--svg", default="favicon.svg", help="SVG 文件")
    ap.add_argument("--outdir", default=".", help="PNG 输出目录")
    ap.add_argument("--color", default="#10C8A1",
                    help="不透明派生件（apple-touch / maskable）的底色")
    ap.add_argument("--sizes", default="16,32,48,180,192,512",
                    help="要生成的 favicon/通用 PNG 尺寸，逗号分隔")
    ap.add_argument("--prefix", default="favicon", help="小尺寸文件名前缀")
    ap.add_argument("--name", default="My App", help="生成 manifest 时的应用名")
    ap.add_argument("--short", default=None, help="manifest short_name")
    ap.add_argument("--manifest", action="store_true", help="顺手写一个 site.webmanifest")
    ap.add_argument("--sheet", action="store_true", help="只出多尺寸预览图（校验用）")
    ap.add_argument("--sheet-out", default="icon-sheet.png", help="预览图输出路径")
    ap.add_argument("--maskable-svg", default=None,
                    help="专门用于 Android 自适应图标的 SVG（建议用 "
                         "make_icon.py --tile rect --inset 0 --scale 0.76 生成）。"
                         "不给则退回「缩放 80%% + 纯色底」，底板圆角会露接缝。")
    ap.add_argument("--no-touch", action="store_true", help="跳过 apple-touch-icon")
    ap.add_argument("--no-maskable", action="store_true", help="跳过 maskable")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args(argv)

    svg = os.path.abspath(args.svg)
    if not os.path.isfile(svg):
        raise SystemExit("找不到 SVG：%s" % svg)
    chrome = find_chrome()
    if not chrome:
        raise SystemExit(
            "没找到 Chromium 系浏览器。装一个 Chrome/Chromium/Edge，"
            "或用 CHROME=/path/to/chrome 指定。")
    if not args.quiet:
        print("浏览器：%s" % chrome)

    sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="iskill-icon-") as tmp:
        if args.sheet:
            page = write_page(tmp, "sheet.html",
                              SHEET_TPL % ((svg,) * 5))
            shoot(chrome, page, args.sheet_out, 640, 250, transparent=False)
            if not args.quiet:
                print("预览图：%s" % os.path.abspath(args.sheet_out))
            return 0

        made = []
        for s in sizes:
            page = write_page(tmp, "p%d.html" % s, page_for(svg, s, None))
            # 小尺寸是给浏览器标签页的 favicon-*，大尺寸是给 PWA manifest 的 icon-*
            stem = "%s-%d" % (args.prefix, s) if s <= 64 else "icon-%d" % s
            out = os.path.join(outdir, stem + ".png")
            shoot(chrome, page, out, s, s, transparent=True)
            made.append(out)

        if not args.no_touch:
            page = write_page(tmp, "touch.html", page_for(svg, 180, args.color))
            out = os.path.join(outdir, "apple-touch-icon.png")
            shoot(chrome, page, out, 180, 180, transparent=False)
            made.append(out)

        if not args.no_maskable:
            if args.maskable_svg:
                msrc = os.path.abspath(args.maskable_svg)
                if not os.path.isfile(msrc):
                    raise SystemExit("找不到 --maskable-svg：%s" % msrc)
                page = write_page(tmp, "mask.html", page_for(msrc, 512, None))
            else:
                # 退化方案：底板缩到 80% 叠在纯色上，圆角与底色之间会有可见接缝
                page = write_page(tmp, "mask.html",
                                  page_for(svg, 512, args.color, scale=0.80))
            out = os.path.join(outdir, "maskable-512.png")
            shoot(chrome, page, out, 512, 512, transparent=False)
            made.append(out)

    if args.manifest:
        mp = os.path.join(outdir, "site.webmanifest")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(MANIFEST_TPL % {
                "name": args.name, "short": args.short or args.name,
                "color": args.color})
        made.append(mp)

    if not args.quiet:
        print("已生成 %d 个文件 → %s" % (len(made), outdir))
        for m in made:
            print("  %-26s %7d B" % (os.path.basename(m), os.path.getsize(m)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
