# 接入代码片段

把图标接进项目。复制粘贴即可。

---

## 一、最简（只要 favicon）

把 `favicon.svg` 和 `favicon.ico` 放到站点根目录，`<head>` 里加：

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" href="/favicon.ico" sizes="48x48" />
```

现代浏览器选 SVG，**缩放不糊**，体积只有 PNG 的几分之一；
不支持 SVG favicon 的老浏览器退到 `favicon.ico`（内嵌 16/32/48 三档）。
就算什么都不写，老浏览器也会按约定路径自动请求 `/favicon.ico` —— 所以这个文件必须在根目录。

---

## 二、推荐（全套）

```html
<link rel="icon" href="/favicon.ico" sizes="48x48" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="theme-color" content="#10C8A1" />
<meta name="apple-mobile-web-app-title" content="我的应用" />
```

要点：

- `favicon.ico` 是给**不支持 SVG favicon 的浏览器**的兜底，内嵌 16/32/48 三档。
- `theme-color` 让移动端地址栏跟着变色 —— 用你图标的主色，整体感立刻上来。
- `apple-touch-icon` **必须是不透明 PNG**（iOS 会盖自己的圆角遮罩，透明区会被填黑）。

---

## 三、PWA

`site.webmanifest`（`make-all.sh --name "…" --short "…"` 会自动生成）：

```json
{
  "name": "我的应用",
  "short_name": "我的",
  "start_url": "./",
  "display": "standalone",
  "background_color": "#10C8A1",
  "theme_color": "#10C8A1",
  "icons": [
    { "src": "./icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "./icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "./maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

**maskable 一定要给。** 安卓装了 PWA 之后，桌面图标会按厂商形状裁切（圆、方、水滴…）。
只给 `any` 的图标，系统会在图标外面垫一圈白边（"洗脸"效果）；
给了 `maskable` 才是满幅铺开、按系统形状裁切。

生成 maskable 源件的正确姿势（`make-all.sh` 已内置）：

```bash
python3 scripts/make_icon.py --glyph whale --color '#10C8A1' \
        --tile rect --inset 0 --scale 0.76 --out .maskable.svg
```

- `--tile rect --inset 0`：底板铺满整个方形（不要圆角，否则和底色之间露接缝）
- `--scale 0.76`：内容缩到 76%，落进安全区（Android 保证裁切的圆是画布的 80%）

安全区速查：内容外接半径 ≤ 画布的 **40%**（即直径 80%）。

---

## 四、Vite

`public/` 目录下的文件会**原样拷到构建产物根目录**，路径写 `/xxx` 即可：

```
public/
├── favicon.ico
├── favicon.svg
├── favicon-32.png
├── apple-touch-icon.png
├── icon-192.png
├── icon-512.png
├── maskable-512.png
└── site.webmanifest
```

`index.html` 里写：

```html
<link rel="icon" href="/favicon.ico" sizes="48x48" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

Vite 会按 `base` 重写 `/` 开头的 URL。若 `base: "./"`（相对路径部署），
构建产物里会变成 `./favicon.svg`，同样是正确的。

> ⚠️ **`dist/` 要不要提交**：如果应用是"纯静态 + 本地服务托管"（比如由某个 Python 脚本
> 单端口托管），把构建产物一起提交更省事 —— 使用者不必装 Node。
> 常规前端项目还是应该把 `dist/` 放进 `.gitignore`。

---

## 五、Next.js

- `app/` 路由：把 `favicon.ico` / `icon.png` / `apple-icon.png` 直接放进 `app/`，Next 自动接管。
- 想用 SVG：`app/icon.svg` 即可，Next 会生成对应的 `<link>`。
- 更细粒度控制用 `metadata`：

```ts
// app/layout.tsx
export const metadata = {
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }, { url: "/favicon-32.png", sizes: "32x32" }],
    apple: "/apple-touch-icon.png",
  },
};
export const viewport = { themeColor: "#10C8A1" };
```

- 放在 `public/` 下的文件用 `/xxx` 访问。

---

## 六、微信小程序

小程序没有 favicon，用的是**项目根目录的 `logo.png`**（后台配置）与代码里的
`navigationBarBackgroundColor`。

建议：

- 导出 `icon-512.png` 作为小程序 Logo（透明底、方图）。
- 页面背景色 / 导航栏色用图标主色，保持一致：

```json
{ "navigationBarBackgroundColor": "#10C8A1", "navigationBarTextStyle": "white" }
```

---

## 七、缓存坑

换图标后浏览器**很可能还显示旧的**，因为 favicon 缓存极其顽固。

- 开发时：硬刷新（Chrome：`Cmd/Ctrl + Shift + R`），或直接开无痕窗口看。
- 用 SVG 主件时，可以在 URL 上挂版本：`/favicon.svg?v=2`。
- **PWA / Service Worker 是更隐蔽的一层**：SW 会连 favicon 一起缓存。
  换图标后要让 SW 版本号（或内容指纹）变化，否则装过 PWA 的用户可能几周都刷不过来。
  SW 的更新策略见 `iskill-pwa-guideline`。
- 线上部署：给图标文件配置较长缓存没问题，但**换图时务必改文件名或加版本参数**。

---

## 八、校验清单

- [ ] 浏览器标签页显示新图标（无痕窗口确认，排除缓存干扰）
- [ ] 手机"添加到主屏"后图标正常（安卓要确认 maskable 生效，没有白边）
- [ ] `theme-color` 与图标主色一致
- [ ] `site.webmanifest` 里的路径能访问到（打开 DevTools → Application → Manifest 看有没有报错）
- [ ] `apple-touch-icon.png` 是不透明的（透明区在 iOS 上会变黑）
