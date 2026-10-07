#!/usr/bin/env node
// svg-symbol-extract.mjs — 把一组 SVG 源文件提取为内联 <symbol> 精灵表（零依赖，纯 Node 标准库）
//
// 背景：整套 SVG 资产（avatar / 徽章 / 收集品 / 图标族）通常每枚一个源文件便于复用与覆盖，
// 但网页里内嵌使用时需要合成 <symbol id> 精灵表 + <use href="#id"> 引用，
// 保证「源文件 ↔ 页面内嵌」零偏差。本脚本即这条提取线的固化。
//
// 用法：
//   node svg-symbol-extract.mjs <dir>                          # 校验 + sprite 片段输出到 stdout
//   node svg-symbol-extract.mjs <dir> --out sprite.html        # 写入文件（而非 stdout）
//   node svg-symbol-extract.mjs <dir> --manifest manifest.json # 同时产出 JSON 资产清单
//   node svg-symbol-extract.mjs <dir> --check                  # 只校验不输出 sprite
//   node svg-symbol-extract.mjs <dir> --prefix av-             # symbol id 统一前缀
//
// 校验项（失败即 exit 1）：
//   1. 根元素 <svg> 且带 viewBox
//   2. 容器标签配平（svg/g/symbol/defs/clipPath）
//   3. 无外部引用（http(s) 资源、<script>、外链 <image href>）—— sprite 必须零外部依赖
//   4. id 无重复（以文件名 slug 为准）
//
// 实战出处：AI-Matrix 成长计划数字资产套件（WO-20261007-11，16 枚 avatar/徽章），
// 生成规范与工作流见 reference/svg-asset-sets.md。

import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { join, basename, extname } from "node:path";

const args = process.argv.slice(2);
const dir = args.find((a) => !a.startsWith("--"));
const flag = (name) => args.includes(name);
const val = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : undefined;
};

if (!dir) {
  console.error("用法: node svg-symbol-extract.mjs <svg目录> [--out file] [--manifest file] [--check] [--prefix p]");
  process.exit(2);
}
if (!statSync(dir).isDirectory()) {
  console.error(`不是目录: ${dir}`);
  process.exit(2);
}

const OUT = val("--out");
const MANIFEST = val("--manifest");
const CHECK_ONLY = flag("--check");
const PREFIX = val("--prefix") ?? "";
const CONTAINERS = ["svg", "g", "symbol", "defs", "clipPath", "mask", "pattern", "marker"];

const files = readdirSync(dir)
  .filter((f) => extname(f).toLowerCase() === ".svg")
  .sort();
if (files.length === 0) {
  console.error(`目录里没有 .svg 文件: ${dir}`);
  process.exit(2);
}

const slugify = (s) =>
  s.replace(extname(s), "").toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "");

const symbols = [];
const manifest = [];
const errors = [];
const seenIds = new Set();

for (const f of files) {
  const p = join(dir, f);
  const src = readFileSync(p, "utf8").trim();
  const label = `✗ ${f}`;

  if (!/<svg[\s>]/.test(src)) { errors.push(`${label}: 找不到根元素 <svg>`); continue; }
  const vb = src.match(/viewBox\s*=\s*"([^"]+)"/);
  if (!vb) { errors.push(`${label}: 缺 viewBox（sprite 缩放必需）`); continue; }

  // 外部引用：sprite 必须自包含
  if (/https?:\/\//.test(src.replace(/xmlns[^ >"]*=("[^"]*"|'[^']*')/g, ""))) {
    errors.push(`${label}: 含 http(s) 外部引用（xmlns 命名空间除外）`); continue;
  }
  if (/<script[\s>]/i.test(src)) { errors.push(`${label}: 含 <script>`); continue; }
  const imgHref = src.match(/<image[^>]+href\s*=\s*"(?!#)([^"]+)"/);
  if (imgHref) { errors.push(`${label}: <image href> 非锚点引用（${imgHref[1]}）`); continue; }

  // 容器配平
  let balanced = true;
  for (const t of CONTAINERS) {
    const open = (src.match(new RegExp(`<${t}[\\s>]`, "g")) ?? []).length;
    const close = (src.match(new RegExp(`</${t}>`, "g")) ?? []).length;
    const selfClose = (src.match(new RegExp(`<${t}[^>]*/>`, "g")) ?? []).length;
    if (open - selfClose !== close) { errors.push(`${label}: <${t}> 配平失败 (open=${open - selfClose} close=${close})`); balanced = false; break; }
  }
  if (!balanced) continue;

  const id = PREFIX + slugify(basename(f, ".svg"));
  if (seenIds.has(id)) { errors.push(`${label}: id 重复 ${id}`); continue; }
  seenIds.add(id);

  // 剥掉 xml 声明 / 注释 / <svg> 外壳，保留内部图形
  const inner = src
    .replace(/<\?xml[\s\S]*?\?>\s*/g, "")
    .replace(/<!DOCTYPE[\s\S]*?>/g, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/^[\s\S]*?<svg[^>]*>/, "")
    .replace(/<\/svg>\s*[\s\S]*$/, "")
    .trim();

  symbols.push(`<symbol id="${id}" viewBox="${vb[1]}">\n${inner}\n</symbol>`);
  manifest.push({ id, file: p, viewBox: vb[1] });
}

const summary = `共 ${files.length} 个源文件，通过 ${symbols.length}，失败 ${errors.length}`;
console.error(summary);

if (errors.length) {
  for (const e of errors) console.error("  " + e);
  process.exit(1);
}

if (MANIFEST) {
  writeFileSync(MANIFEST, JSON.stringify({ dir, count: manifest.length, assets: manifest }, null, 2) + "\n");
  console.error(`清单已写入 ${MANIFEST}`);
}
if (!CHECK_ONLY) {
  const sprite = symbols.join("\n");
  if (OUT) {
    writeFileSync(OUT, sprite + "\n");
    console.error(`sprite 已写入 ${OUT}（${symbols.length} 个 symbol）`);
  } else {
    console.log(sprite);
  }
}
