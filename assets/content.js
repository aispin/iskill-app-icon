window.PROMO = {
  name: "ISKILL-APP-ICON",
  brand: "#10c8a1",
  brand2: "#7c5cff",
  repo: "https://github.com/aispin/iskill-app-icon",
  repoLabel: "aispin/iskill-app-icon",
  license: "MIT",

  platform: "macos",

  lang: {
    /* ── 中文 ───────────────────────────────────────────────────────── */
    zh: {
      meta: {
        title: "ISKILL-APP-ICON · 一个图形一个色，吐出整套图标",
        description: "零依赖 Python 生成超椭圆底板 + 手绘矢量 SVG，再用本机 Chromium 无头渲染出 favicon / apple-touch-icon / PWA 全套 PNG 与 manifest。"
      },
      a11y: { skip: "跳到主要内容" },
      ui: { copy: "复制", copied: "已复制", failed: "复制失败" },
      nav: { features: "能力", shots: "截图", how: "上手", faq: "问答" },

      hero: {
        badge: "AI 技能",
        titlePre: "一个图形一个色，",
        titleAccent: "吐出整套图标",
        titlePost: "",
        sub: "零依赖 Python 画出超椭圆底板 + 手绘矢量 SVG，再用本机 Chromium 无头渲染出 favicon、apple-touch-icon、PWA 全套 PNG 与 manifest，最后打印要贴进 head 的接入片段。",
        ctaPrimary: "复制安装提示词",
        ctaSecondary: "看源码",
        meta1: "零第三方依赖",
        meta2: "6 种内置图形",
        meta3: "只出 SVG 不需要浏览器"
      },
      terminal: {
        title: "zsh — iskill-app-icon",
        lines: [
          [{ t: "$ ", c: "p" }, { t: "python3 scripts/make_icon.py --glyph leaf --color '#10C8A1' --out favicon.svg", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "已写出 favicon.svg（手绘矢量，约 3–4 KB）", c: "s" }],
          [{ t: "$ ", c: "p" }, { t: "bash scripts/make-all.sh --glyph orbit --color '#3B82F6' --outdir public --name \"网关控制台\" --sheet", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "favicon.svg · favicon-16/32/48.png · apple-touch-icon.png · icon-192/512.png · maskable-512.png · site.webmanifest", c: "s" }],
          [{ t: "→ ", c: "p" }, { t: "已打印要贴进 <head> 的接入片段", c: "" }]
        ]
      },

      stats: [
        { value: "6", label: "内置手绘图形", note: "白鲸 / 猫 / 叶片 / 闪电 / 轨道环 / 六边形，另有字母 S" },
        { value: "9", label: "一条命令的产物件数", note: "favicon.svg + 3 档 PNG + apple-touch-icon + 192/512 + maskable + manifest" },
        { value: "29 → 3.9 KB", label: "单图体积（描摹 → 手绘）", note: "手写 5~10 条贝塞尔，不描摹位图" },
        { value: "0", label: "第三方依赖", note: "纯标准库，不需要 Pillow / cairosvg" }
      ],

      compare: {
        eyebrow: "对比",
        title: "以前 vs 现在",
        sub: "",
        before: { title: "没有这个技能", items: ["favicon / apple-touch-icon / maskable 的尺寸与底色要反复试", "描摹位图得到几十 KB 的矢量，边缘还有缺口", "maskable 直接把小圆角图标缩小，圆角外露出一圈接缝"] },
        after: { title: "有了这个技能", items: ["一条命令出齐 9 个产物件", "手绘 5~10 条贝塞尔，3~4 KB 干净矢量", "maskable 单独出源件（满幅 rect + 内容缩到 0.76）"] }
      },

      features: {
        eyebrow: "能力",
        title: "它能做什么",
        sub: "",
        items: [
          { icon: "bolt", title: "一行出全套", desc: "<code>make-all.sh</code> 串起 SVG → PNG → manifest，并打印接入片段。" },
          { icon: "grid", title: "6 图形 × 4 底板", desc: "<code>--glyph</code> 与 <code>--tile</code> 任意组合，先并排比选再定稿。" },
          { icon: "layers", title: "自动推导配色", desc: "只给一个主色，亮部/暗部/镂空色会自动重算，不用自己配三档。" },
          { icon: "shield", title: "maskable 规范", desc: "满幅底板 + 内容缩到 0.76 单独渲染，避免圆角外露接缝。" },
          { icon: "gauge", title: "按 32px 验收", desc: "<code>--sheet</code> 出多尺寸预览图，确认缩到 16/32px 还认得出。" },
          { icon: "monitor", title: "无头渲染", desc: "用本机 Chromium 渲染 PNG，不需要 Pillow / cairosvg / librsvg。" }
        ]
      },

      showcase: {
        eyebrow: "实拍",
        title: "看一眼真东西",
        sub: "下列图片由本技能现场生成，源件在仓库 assets/samples/ 目录。",
        items: [
          { src: "assets/shots/sample-glyphs.png", alt: "六个内置图形样本", caption: "六个内置图形，右下角是缩到 32px / 16px 的真实样子" },
          { src: "assets/shots/sample-tiles.png", alt: "底板与配色样本", caption: "同一个图形只换 --tile，或只换一个主色" }
        ]
      },

      steps: {
        eyebrow: "上手",
        title: "三步跑起来",
        sub: "命令由 agent 跑，你只说要什么、看结果。",
        items: [
          { title: "交给 AI 装", desc: "把这句话粘进对话框，agent 会自己拉代码、读文档，再告诉你用法。", codeKey: "install" },
          { title: "说清要什么图标", desc: "图形、主色、要不要全套，一句话说完；命令与参数由 agent 决定。", codeName: "prompt", code: "帮我给这个项目做一套图标，主色 #10C8A1，先出一个 SVG 我确认图形，再出全套 PNG 和 manifest。" },
          { title: "看预览图定稿", desc: "它会出一张多尺寸预览图，你只要确认 16px 还认得出；不满意换个图形重来，同参数永远同图。" }
        ]
      },


      faq: {
        eyebrow: "问答",
        title: "常见问题",
        items: [
          { q: "Windows / Linux 上能用吗？", a: "分两步看：生成 SVG 是纯标准库 Python，任何平台都能跑；渲染 PNG 需要本机 Chromium，而 render_png.py 的浏览器候选全是 macOS 的 /Applications/*.app 路径，Windows 上会报「没找到 Chromium 系浏览器」。替代方案：用 CHROME=/path/to/chrome.exe 指定 Windows 的 Chrome，或只出 SVG（只出 SVG 时不需要浏览器）。" },
          { q: "需要装 Pillow / cairosvg 吗？", a: "不需要。PNG 走无头浏览器渲染，脚本只用标准库：math / argparse / json / subprocess。" },
          { q: "想换图标主色怎么办？", a: "换 --color 即可，渐变与镂空色会跟着重算；想完全自己控色用 --theme 传入 {color, light, mid, dark, glyph_color}。" },
          { q: "能加自己的图形吗？", a: "能。往 scripts/make_icon.py 的 GLYPHS 字典加一段画在 512×512 画布上的 SVG，--glyph 加名字立刻可用。" },
          { q: "怎么确认小尺寸还看得清？", a: "加 --sheet 出多尺寸预览图，肉眼确认缩到 16px / 32px 还认得出；规则是细节按 512 画、按 32px 验收。" }
        ]
      },

      cta: { title: "现在就来一发", desc: "把提示词粘给 AI，先出一个干净的 favicon.svg。", primary: "去 GitHub 看看", secondary: "复制安装提示词" },
      footer: { license: "MIT 许可", madeWith: "由 iskill-promo-page 生成" }
    },

    /* ── English ────────────────────────────────────────────────────── */
    en: {
      meta: {
        title: "ISKILL-APP-ICON · One glyph + one color → a full icon set",
        description: "Zero-dependency Python emits a squircle base + hand-drawn vector SVG, then headless Chromium renders the favicon / apple-touch-icon / PWA PNG set and manifest."
      },
      a11y: { skip: "Skip to content" },
      ui: { copy: "Copy", copied: "Copied", failed: "Copy failed" },
      nav: { features: "Features", shots: "Screens", how: "Get started", faq: "FAQ" },

      hero: {
        badge: "AI skill",
        titlePre: "One glyph, one color — ",
        titleAccent: "a whole icon set",
        titlePost: "",
        sub: "Zero-dependency Python draws a squircle base plus a hand-drawn vector SVG, then local headless Chromium renders the favicon, apple-touch-icon and PWA PNG set with a manifest, and prints the head snippet to paste.",
        ctaPrimary: "Copy install prompt",
        ctaSecondary: "View source",
        meta1: "Zero third-party deps",
        meta2: "6 built-in glyphs",
        meta3: "SVG-only needs no browser"
      },
      terminal: {
        title: "zsh — iskill-app-icon",
        lines: [
          [{ t: "$ ", c: "p" }, { t: "python3 scripts/make_icon.py --glyph leaf --color '#10C8A1' --out favicon.svg", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "wrote favicon.svg (hand-drawn vector, ~3–4 KB)", c: "s" }],
          [{ t: "$ ", c: "p" }, { t: "bash scripts/make-all.sh --glyph orbit --color '#3B82F6' --outdir public --name \"Gateway\" --sheet", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "favicon.svg · favicon-16/32/48.png · apple-touch-icon.png · icon-192/512.png · maskable-512.png · site.webmanifest", c: "s" }],
          [{ t: "→ ", c: "p" }, { t: "printed the <head> snippet to paste", c: "" }]
        ]
      },

      stats: [
        { value: "6", label: "built-in hand-drawn glyphs", note: "whale / cat / leaf / bolt / orbit / hex, plus a letter S" },
        { value: "9", label: "artifacts from one command", note: "favicon.svg + 3 PNG sizes + apple-touch-icon + 192/512 + maskable + manifest" },
        { value: "29 → 3.9 KB", label: "per-icon size (trace → hand-draw)", note: "5~10 béziers instead of tracing a bitmap" },
        { value: "0", label: "third-party dependencies", note: "stdlib only, no Pillow / cairosvg" }
      ],

      compare: {
        eyebrow: "Comparison",
        title: "Before vs after",
        sub: "",
        before: { title: "Without it", items: ["Trial and error over sizes and background colors for favicon / apple-touch-icon / maskable", "Tracing a bitmap gives tens of KB of vector with notched edges", "Shrinking the rounded icon for maskable leaves a visible seam"] },
        after: { title: "With it", items: ["One command emits all 9 artifacts", "5~10 béziers, a clean 3~4 KB vector", "A separate maskable source (full-bleed rect + content at 0.76)"] }
      },

      features: {
        eyebrow: "Features",
        title: "What it does",
        sub: "",
        items: [
          { icon: "bolt", title: "Full set in one line", desc: "<code>make-all.sh</code> chains SVG → PNG → manifest and prints the snippet." },
          { icon: "grid", title: "6 glyphs × 4 tiles", desc: "Combine <code>--glyph</code> and <code>--tile</code> freely, compare variants side by side." },
          { icon: "layers", title: "Derived palette", desc: "Give one main color; light / mid / dark and the cutout color are computed for you." },
          { icon: "shield", title: "Maskable done right", desc: "Full-bleed tile with content at 0.76, no seam around the corners." },
          { icon: "gauge", title: "Reviewed at 32px", desc: "<code>--sheet</code> renders a multi-size preview to check it still reads at 16/32px." },
          { icon: "monitor", title: "Headless render", desc: "Renders PNG with local Chromium — no Pillow / cairosvg / librsvg." }
        ]
      },

      showcase: {
        eyebrow: "Screens",
        title: "See the real thing",
        sub: "These images were generated by the skill itself; sources live in assets/samples/.",
        items: [
          { src: "assets/shots/sample-glyphs.png", alt: "Six built-in glyphs", caption: "Six built-in glyphs — the bottom-right of each is the real 32px / 16px result" },
          { src: "assets/shots/sample-tiles.png", alt: "Tiles and colors", caption: "Same glyph with a different --tile, or just a different main color" }
        ]
      },

      steps: {
        eyebrow: "Get started",
        title: "Up and running in three steps",
        sub: "The agent runs the commands. You say what you want and check the result.",
        items: [
          { title: "Let your agent install it", desc: "Paste the line into the chat — it clones the repo, reads the docs, and tells you how to use it.", codeKey: "install" },
          { title: "Say what icon you need", desc: "Glyph, brand color, full set or not — one sentence is enough. The agent picks the commands.", codeName: "prompt", code: "Make an icon set for this project, brand color #10C8A1. Show me one SVG first, then the full PNG set and manifest." },
          { title: "Check the preview sheet", desc: "It renders a multi-size sheet; just confirm 16 px is still readable. Don't like it? Pick another glyph — same params, same result." }
        ]
      },


      faq: {
        eyebrow: "FAQ",
        title: "Frequently asked",
        items: [
          { q: "Does it work on Windows / Linux?", a: "Two steps matter: generating the SVG is pure stdlib Python and runs anywhere; rendering the PNG needs local Chromium, and render_png.py's candidates are all macOS /Applications/*.app paths, so Windows reports “no Chromium browser found”. Workaround: set CHROME=/path/to/chrome.exe to your Windows Chrome, or generate SVG only (SVG-only needs no browser)." },
          { q: "Do I need Pillow / cairosvg?", a: "No. PNG export goes through a headless browser; the scripts use only the standard library: math / argparse / json / subprocess." },
          { q: "How do I change the main color?", a: "Change --color; the gradient and cutout color follow. For full control, pass --theme with {color, light, mid, dark, glyph_color}." },
          { q: "Can I add my own glyph?", a: "Yes. Add a 512×512 SVG block to the GLYPHS dict in scripts/make_icon.py; --glyph with the name works immediately." },
          { q: "How do I check small sizes?", a: "Add --sheet for a multi-size preview and confirm it still reads at 16px / 32px — the rule is to design at 512 but review at 32." }
        ]
      },

      cta: { title: "Give it a spin", desc: "Paste the prompt into your agent and get a clean favicon.svg first.", primary: "Open on GitHub", secondary: "Copy install prompt" },
      footer: { license: "MIT licensed", madeWith: "Built with iskill-promo-page" }
    }
  }
};
