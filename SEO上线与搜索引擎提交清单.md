# RemitGuide — 上线前 & 搜索引擎提交清单

> 目标：让海外华人（美/澳→中国走廊）在 Google / Bing 搜"汇款/remit to China"时能找到你。
> 本清单假设你用 **GitHub Pages + 自定义域名**（vibe-site 已跑通的同款方案）。

---

## 0. 上线前必须先替换的占位（否则全站错链）

在 `build_site.py` 顶部改这三处，再 `python build_site.py` 重新生成：

| 占位 | 改成 | 说明 |
|---|---|---|
| `BASE = 'https://remitguide.xxx/'` | 你的真实域名，含结尾 `/` | 影响 canonical、og:url、sitemap、JSON-LD |
| `CONTACT_EMAIL = 'hello@remitguide.xxx'` | 真实邮箱 | 联系页 + 邮件抓取 |
| 汇率警报接口 `/api/subscribe` | 需部署 Serverless 函数（`api/subscribe.js` + `api/cron.js`，见脚本目录）并配置 Upstash + Resend 环境变量 | 纯静态托管（GitHub Pages）无法运行后端，订阅提交会 404；需 Vercel/Netlify/Cloudflare Pages 之一承载 `/api/*` 与定时任务 |

`data/platforms.json` 里每个平台的 `affiliate_link`（`your-id` 占位）也要换成真实联盟链接——不然点击"Official site"跳 404。

---

## 1. 域名 / HTTPS 配置（GitHub Pages）

1. 仓库根放 `CNAME` 文件，内容只有一行：`remitguide.xxx`（无 www、无协议）。
2. 域名 DNS：
   - 用 **A 记录** 指向 GitHub Pages IP：`185.199.108.153 / 185.199.109.153 / 185.199.110.153 / 185.199.111.153`（4 条都加，抗单点）。
   - 或 **CNAME 记录** 指向 `youruser.github.io`（仅当域名即根域时用 A 记录更稳）。
3. 仓库 Settings → Pages → Custom domain 填域名 → 勾 **Enforce HTTPS**。证书由 GitHub 自动签发（首次约几分钟~几小时）。
4. 仓库根保留 `.nojekyll`（已有），否则 `_` 开头目录被 Jekyll 忽略。
5. 验证：`curl -I https://remitguide.xxx/` 返回 `200` 且 `strict-transport-security` 头存在。

---

## 2. Google Search Console（核心，必做）

1. 打开 https://search.google.com/search-console/ → **添加属性** → 选 **"网址前缀"** 模式，填 `https://remitguide.xxx/`（与 BASE 一致）。
2. 验证方式（任选其一，推荐 DNS TXT，免改代码）：
   - **DNS 验证**：在域名后台加一条 TXT 记录，值用 GSC 给的 `google-site-verification=...`。
   - 或 **HTML 标记**：把 GSC 给的 `<meta name="google-site-verification" ...>` 加进 `HEAD_BRU`（在 `build_site.py` 第 ~88 行附近），重新生成。
3. 左侧 **站点地图** → 提交 `https://remitguide.xxx/sitemap.xml`。
4. 提交后等 1–3 天，看 **覆盖率** 报告是否全部"已编入索引"。
5. 建议开启 **网址检查工具** 手动测首页 / calculator.html 能否索引。

> 提示：Google 在美区搜索份额 ~85%（移动 93%），这是你 90% 的发现流量来源。

---

## 3. Bing Webmaster Tools（顺手做，零成本 + 喂 AI 搜索）

1. 打开 https://www.bing.com/webmasters/ → **添加站点** → 填 `https://remitguide.xxx/`。
2. 验证：Bing 支持 **"从 Google Search Console 导入"**（登录同一账号一键同步验证），最省事；否则同样用 DNS TXT 或 XML 文件。
3. **提交站点地图** → `https://remitguide.xxx/sitemap.xml`。
4. 为什么值得：Bing 美区份额 ~10%（桌面 16%），且 **ChatGPT 联网检索底层用 Bing 索引、Copilot 也基于 Bing**——优化 Bing ≈ 顺带进 AI 答案。对"Wise vs Remitly"这种事实型查询，AI 摘要会直接引用你。

---

## 4. 上线前技术自检（逐项打勾）

- [ ] `BASE` / 邮箱 / 汇率警报接口（Serverless 环境变量：Upstash + Resend）/ 联盟链接 全部替换，无 `xxx` / `your-id` 残留
- [ ] 每个页面 `<title>` 唯一且含目标关键词（Wise / Remitly / 汇款 / remit to China）
- [ ] `<meta name="description">` 各页不同、≤160 字、有召唤（"输入金额即算到账"）
- [ ] `rel="canonical"` 指向真实域名（已内置 `__CANON__`）
- [ ] Open Graph / Twitter 卡片完整（已内置，换图可换 `og-image.png`）
- [ ] JSON-LD 结构化数据有效（WebSite / WebApplication / Article / CollectionPage 已内置）——可用 https://search.google.com/test/rich-results 验
- [ ] `robots.txt` 指向真实 `Sitemap:`（已内置 `BASE`+sitemap.xml）
- [ ] 全站 **无 `noindex`**（默认无，别手滑加）
- [ ] 移动端友好：输入框 ≥16px（已修）、用 `100dvh` 防 footer 裁切（已修）、`viewport` 已设
- [ ] HTTPS 全程（Enforce HTTPS 已开）
- [ ] 页面速度：Tailwind / Google Fonts 走 CDN，已够快；若以后要极致可改自托管 CSS
- [ ] 404 页（GitHub Pages 默认有，可后续自定义）

---

## 5. 上线后监控

- **GSC**：每周看「效果」报告（展示量 / 点击 / 平均排名），盯 "remit to china"、"wise vs remitly"、"汇款回国" 等词。
- **Bing**：Webmaster 报告看索引量与点击。
- **索引时效**：汇率/费用类内容变化频繁，`build_site.py` 里 `DATA_UPDATED` 更新后重生成，sitemap `lastmod` 会自动变，Google 会更快重抓。
- 发现某页长期 0 展示：检查是否被 Google 判"内容单薄" → 补该走廊的实测长文（见《社区分发与内容矩阵》）。
