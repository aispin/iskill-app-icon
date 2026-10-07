# 整套 SVG 资产生成规范（avatar / 徽章 / 收集品 / 图标族）

> 适用场景：一次产出一**套**风格统一的 SVG 资产——产品收集品（avatar）、成就徽章、
> 积分商城道具、插画图标族等。单枚 app icon 的生成见 SKILL.md 主流程；
> 本文解决的是「套」的问题：视觉同族、命名可寻址、页面零偏差内嵌。
>
> 方法论出处：AI-Matrix 成长计划数字资产套件实战（2026-10-07，16 枚 avatar/徽章，
> 一名 LLM 设计师 + 提取脚本，全程可复现）。

## 一、动工前先定四件事（缺一会返工）

1. **尺寸档**：每套只选一档主力画布——
   - `24×24`：工具栏图标、状态图标（stroke 风格，坐标走偶数网格）
   - `96×96`：avatar / 徽章 / 收集品（填充为主，可带 1~2 处镂空细节）
   - 混档可以，但**每枚源文件只一个 viewBox**，套内同类资产必须同档。
2. **色板**：品牌主色 + 派生色（亮部/暗部）+ 中性灰阶，全集合计 ≤ 8 色。
   主体尽量走 `currentColor`（代码里跟随文字色，天然双主题）；
   品牌色块允许硬编码，但**每个主题下都要肉眼复核一遍对比度**。
3. **命名规范**：`<类型>-<两位编号>-<slug>.svg`，如 `avatar-01-stardust-rover.svg`、
   `badge-07-legend.svg`。编号即资产 ID，供配置表/数据库引用，**定稿后不可复用给新资产**。
4. **一句话人设**：avatar/收集品类每枚配一句「它是什么 + 它的怪癖」。
   这不是文案装饰——LLM 生成时靠它保持形象差异，产品侧靠它写图鉴和覆盖名。

## 二、LLM 批量生成工作流（实测可靠的路子）

```
定色板/画布/命名 → 逐枚提示（人设+风格锚点）→ 分批落盘（每 3~4 枚回读）
→ xmllint / 提取脚本校验 → 变体比选 → 定稿 → 提取 symbol 内嵌页面
```

要点：
- **风格锚点前置**：第一批 2~3 枚定调（造型语言、圆角程度、细节密度、描边粗细），
  后续每枚的提示里都带上「与 avatar-01 同族视觉语言」。先多生成几个候选比选再定调，比事后统一快得多。
- **分批落盘**：批量生成最容易死在「一口气写完全部 → 中断 → 全部丢失」。
  每 3~4 枚写盘一次并回读校验，中断也保住已产出的。
- **每枚独立文件**，不要一张 SVG 画全套——独立文件才能被覆盖机制、配置表、
  symbol 提取分别引用。
- **原创红线**：参考竞品的「格式」可以（几何语言、配色思路），临摹「形象」不行
  （具体角色轮廓、标志性五官组合）。提示里写明「禁止临摹 XX 的形象」。

## 三、双主题与状态变体

| 变体 | 做法 | 备注 |
|---|---|---|
| 浅色/深色主题 | 主体 `currentColor`；独立文件里给 `:root` 与 `@media (prefers-color-scheme)` 两个 fill 值 | 页面内嵌版靠外层 CSS color 控制 |
| 未获得/剪影态 | CSS `filter: grayscale(1) + opacity`，或单独出一枚 `*-silhouette.svg` | 优先 CSS，能不出第二份文件就不出 |
| 稀有度分型 | 同一造型换背板/光环/配色映射，**不改主体** | 稀有度档位先在配置层定，再决定要不要出视觉变体 |

## 四、质量验收清单（逐枚过）

- [ ] viewBox 存在且套内同类资产一致
- [ ] 容器标签配平（`g`/`symbol`/`defs` 开合数一致）
- [ ] 零外部引用（无 `http(s)` 资源、`<script>`、外链 `<image href>`）
- [ ] `currentColor` 或双主题 fill 已验证（浅深两色背景下截图对比）
- [ ] 缩到 32px（icon 档）/ 48px（avatar 档）仍认得出主体——「缩图验收」沿用 app icon 的铁律
- [ ] id 无重复、命名符合 `<类型>-<编号>-<slug>` 规范

## 五、提取内嵌：`svg-symbol-extract.mjs`

源文件是复用与覆盖的真相源，页面内嵌用 symbol 精灵表保证零偏差：

```bash
S=~/.workbuddy/skills/iskill-app-icon

# 只校验（CI / 交付前自检）
node $S/scripts/svg-symbol-extract.mjs docs/assets/avatars --check

# 校验 + 产出 sprite 片段（stdout，粘进 <body> 开头即可 <use href="#id"> 引用）
node $S/scripts/svg-symbol-extract.mjs docs/assets/avatars --prefix av-

# 校验 + 写 sprite 文件 + JSON 资产清单（喂给配置表/覆盖机制）
node $S/scripts/svg-symbol-extract.mjs docs/assets/avatars \
     --out sprite.html --manifest assets-manifest.json --prefix av-
```

页面用法（sprite 粘进 `<body>` 顶部后）：

```html
<svg class="asset" width="48" height="48"><use href="#av-avatar-01-stardust-rover"/></svg>
```

JSON 清单（`--manifest`）就是后续「App 覆盖默认资产」机制的输入：
编号 / 源文件 / viewBox 三元组直接映射成配置表。

## 六、踩过的坑

| 现象 | 对策 |
|---|---|
| 批量生成后半程风格漂移（后半批不像第一批） | 风格锚点写进每枚提示；每批生成完先并排比选再继续 |
| sprite 里图形不显示 | symbol 内部引用了外部资源被校验拦下；或 `<use>` 的 id 前缀对不上——清单 JSON 核对 |
| 双主题下深色主题「糊成一团」 | 主体别用纯黑硬编码；中性灰阶给足层次，细节色与背景色对比度 ≥ 3:1 |
| 源文件改了页面没变 | sprite 是生成物——重跑提取脚本同步，别手改 sprite |
| LLM 生成的 SVG 偶发标签不闭合 | 提取脚本容器配平校验会拦；重生成该枚而不是手补标签 |
