#!/usr/bin/env python3
"""iskill-app-icon · SVG → 多尺寸 PNG 派生件

用本机已装的 Chromium 系浏览器做**无头渲染**，不需要任何 Python 图形库。
跨平台：macOS / Windows / Linux 一份代码（浏览器路径按平台探测，见 browser_candidates()）。

产出（默认全部）：
    favicon-16.png / favicon-32.png / favicon-48.png   透明底，给浏览器标签页
    apple-touch-icon.png (180)                        不透明底（iOS 会盖自己的圆角遮罩）
    icon-192.png / icon-512.png                        透明底，给 PWA manifest
    maskable-512.png                                   满幅底 + 内容缩到 80%（Android 自适应图标）

用法：
    python3 render_png.py --svg favicon.svg --outdir public --color '#10C8A1'
    python3 render_png.py --svg favicon.svg --sheet                 # 只出多尺寸预览图
    CHROME=/path/to/chrome python3 render_png.py --svg icon.svg      # 手动指定浏览器
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
from urllib.request import pathname2url

CANVAS = 512

# ── 浏览器候选：按当前平台优先，再补通用名（macOS / Windows / Linux 三平台）──
_MAC_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "~/.agent-browser/browsers/chrome-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    "~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
]


def _win_paths() -> list:
    """Windows 上的常见安装位置（含 Edge —— 它随系统预装，通常不用额外装东西）。"""
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    la = os.environ.get("LOCALAPPDATA", "")
    out = [
        os.path.join(pf, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf86, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf86, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(la, r"ms-playwright\chromium-*\chrome-win\chrome.exe"),
        os.path.join(la, r".agent-browser\browsers\chrome-*\chrome-win\chrome.exe"),
    ]
    if la:
        out += [
            os.path.join(la, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(la, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(la, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
    return out


def browser_candidates() -> list:
    """按「平台专属路径 → PATH 里的通用名 → 通用缓存目录」排序，返回候选 glob 列表。"""
    out = [os.environ.get("CHROME", "")]
    if sys.platform == "darwin":
        out += [os.path.expanduser(p) for p in _MAC_PATHS]
    elif os.name == "nt":
        out += _win_paths()
    # PATH 里的可执行名（Windows 上 .exe 后缀必须显式写）
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                 "chrome", "msedge", "chrome.exe", "msedge.exe", "brave", "brave.exe"):
        out.append(shutil.which(name) or "")
    # 通用缓存（node 侧无头工具留下的浏览器）
    out += [
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        os.path.expanduser("~/.agent-browser/browsers/chrome-*/chrome-linux/chrome"),
    ]
    if sys.platform != "darwin":
        out += [os.path.expanduser(p) for p in _MAC_PATHS]
    return out


def find_chrome() -> str | None:
    for c in browser_candidates():
        if not c:
            continue
        for p in glob.glob(c):
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
    return None



def shoot(chrome: str, page: str, out: str, w: int, h: int, transparent: bool) -> None:
    """无头截一张图。**别加 --user-data-dir**（见下）。

    实测教训（2026-10-02，Chrome 154 for Testing / macOS）：
      · 裸 `--headless --disable-gpu` 不传 profile → 正常出图（只有无害的
        CVDisplayLink 警告），这是唯一稳的配方。
      · 加 `--user-data-dir=<临时目录>` → Chrome 截完**不退出**，进程挂死
        （同一条命令单跑超过 7 分钟未结束，只能 kill）。
      · 优先 `--headless=new` → 这部分 Chrome 上 GPU 进程直接 FATAL
        （`gpu_data_manager_impl_private.cc:417 GPU process isn't usable`，exit 6）。
    所以顺序是「先裸 --headless，再退到 --headless=new」，且**永远不带 profile**。
    """
    base = [chrome, "--disable-gpu", "--no-proxy-server",
            "--hide-scrollbars", "--force-device-scale-factor=1",
            "--virtual-time-budget=2500", "--window-size=%d,%d" % (w, h),
            "--screenshot=" + os.path.abspath(out)]
    if transparent:
        base.append("--default-background-color=00000000")
    base.append(file_uri(page))
    last = None
    for flag in ("--headless", "--headless=new"):
        if os.path.exists(out):
            try:
                os.remove(out)
            except OSError:
                pass
        r = subprocess.run([base[0], flag] + base[1:], capture_output=True, text=True)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return
        last = r
    raise SystemExit("截图失败（%dx%d）：\n%s\n%s"
                     % (w, h, last.stdout[-800:], last.stderr[-800:]))



def file_uri(p: str) -> str:
    """绝对路径 → 合法 file:// URI。

    必须走这一步：Windows 上直接写 src="C:\\a\\b.svg" 会被当成 scheme「c:」或相对路径，
    页面里根本加载不出图（macOS 上恰好能糊过去，所以这个坑只在 Windows 暴露）。
    """
    return "file://" + pathname2url(os.path.abspath(p))


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
""" % (body_bg, off, off, inner, inner, html.escape(file_uri(svg), quote=True))



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
            "没找到 Chromium 系浏览器。\n"
            "  · macOS：装 Chrome / Chromium / Edge / Brave 任一\n"
            "  · Windows：Edge 随系统预装，正常都能探到；装 Chrome 也行\n"
            "  · Linux：apt/dnf 装 chromium 或 google-chrome\n"
            "  · 或用 CHROME=/path/to/chrome 显式指定")
    if not args.quiet:
        print("浏览器：%s" % chrome)

    sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="iskill-icon-") as tmp:
        if args.sheet:
            page = write_page(tmp, "sheet.html",
                              SHEET_TPL % ((file_uri(svg),) * 5))
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
