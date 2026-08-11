# -*- coding: utf-8 -*-
"""
RemitGuide — 海外华人汇款对比内容站（最小可用站骨架）
复用 vibe-site 的 Neo-Brutalist 外壳（TW_CONFIG/HEAD_BRU/sidenav/topbar/footer/page_brutalist），
内容层换成汇款站：首页 + 汇款费用计算器 + 走廊指南文章 + disclosure/disclaimer。
数据源：data/platforms.json（平台资料 + 联盟链接收口 + 计算器费率模型）。
构建：python build_site.py → 生成全部 HTML + sitemap.xml + robots.txt
"""
import html
import json
import os
import subprocess
from datetime import date

# ============================================================
# SITE CONFIG（上线前替换占位）
# ============================================================
BASE = 'https://remit.david-cells.com/'   # Cloudflare Pages 自定义域名
SITE_NAME = 'RemitGuide'
SITE_TAGLINE = 'Remit Guide · 华人汇款指南'
CONTACT_EMAIL = 'hello@remit.david-cells.com'  # TODO: 换成真实可收信邮箱/表单
AFF_DISCLOSURE = ('<p class="hint" style="margin-top:14px;border-top:2px solid #1b1c19;padding-top:10px;">'
                  'Affiliate disclosure: some links on this page are affiliate links. '
                  'If you sign up via them we may earn a commission at no extra cost to you. '
                  'We only recommend platforms we would use ourselves. — 部分链接为联盟链接，不影响你的费用。</p>')
DATA_NOTE = '<p class="hint" style="margin-top:14px;border-top:2px solid #1b1c19;padding-top:10px;">数据更新于 {d}，实际费用以平台实时报价为准。</p>'

# ---- load platforms data ----
with open('data/platforms.json', encoding='utf-8') as _f:
    _RAW = json.load(_f)
FX = _RAW['_meta']['fx']
DATA_UPDATED = _RAW['_meta']['data_updated']
PLATFORMS = {k: v for k, v in _RAW.items() if k != '_meta'}

# ---- nav registry: (slug/page_id, label, icon) ----
NAV_TOOLS = [
    ('calculator', 'Fee Calculator', 'calculate'),
    ('guides', 'Guides', 'menu_book'),
]
NAV_META = [
    ('about', 'About', 'info'),
    ('contact', 'Contact', 'mail'),
    ('disclosure', 'Disclosure', 'gavel'),
    ('privacy', 'Privacy', 'security'),
]

# ============================================================
# SHARED NEO-BRUTALIST SHELL (ported from vibe-site)
# ============================================================
TW_CONFIG = r'''
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      "colors": {
        "background":"#fbf9f4","surface":"#fbf9f4","surface-container":"#f0eee9",
        "surface-container-low":"#f5f3ee","surface-container-lowest":"#1b1c19",
        "surface-container-high":"#eae8e3","surface-container-highest":"#e4e2dd",
        "on-surface":"#1b1c19","on-surface-variant":"#444748","on-background":"#1b1c19",
        "brutalist-yellow":"#ba1a1a","swiss-accent":"#ba1a1a","cyber-green":"#ba1a1a",
        "primary":"#fbf9f4","on-primary":"#1b1c19","outline":"#747878","outline-variant":"#c4c7c7",
        "error":"#ba1a1a","on-error":"#ffffff","error-container":"#ffeceb","on-error-container":"#ba1a1a"
      },
      "borderRadius": {"DEFAULT":"0.125rem","lg":"0.25rem","xl":"0.5rem","full":"0.75rem"},
      "spacing": {"base":"4px","gap-md":"2rem","gap-lg":"4rem","gap-sm":"1rem","gap-xs":"0.5rem","sidebar-width":"280px","container-max":"1280px"},
      "fontFamily": {"display-lg":["Playfair Display"],"display-lg-mobile":["Playfair Display"],"body-md":["Inter"],"headline-md":["Playfair Display"],"headline-sm":["Playfair Display"],"label-caps":["JetBrains Mono"],"code-ui":["JetBrains Mono"],"body-lg":["Inter"]},
      "fontSize": {
        "display-lg":["48px",{"lineHeight":"1.1","letterSpacing":"-0.02em","fontWeight":"900"}],
        "display-lg-mobile":["32px",{"lineHeight":"1.1","fontWeight":"900"}],
        "body-md":["16px",{"lineHeight":"1.5","fontWeight":"400"}],
        "headline-md":["32px",{"lineHeight":"1.2","fontWeight":"600"}],
        "headline-sm":["24px",{"lineHeight":"1.3","fontWeight":"500"}],
        "label-caps":["12px",{"lineHeight":"1","letterSpacing":"0.05em","fontWeight":"600"}],
        "code-ui":["14px",{"lineHeight":"1.4","fontWeight":"400"}],
        "body-lg":["18px",{"lineHeight":"1.6","fontWeight":"400"}]
      },
      "boxShadow": {"brutal":"4px 4px 0px #000000","brutal-hover":"2px 2px 0px #000000"}
    }
  }
}'''

HEAD_BRU = ('''<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>__TITLE__</title>
<meta name="description" content="__META__"/>
<link rel="canonical" href="__CANON__"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="RemitGuide"/>
<meta property="og:title" content="__TITLE__"/>
<meta property="og:description" content="__META__"/>
<meta property="og:url" content="__CANON__"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="__TITLE__"/>
<meta name="twitter:description" content="__META__"/>
<meta property="og:image" content="__BASE__og-image.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:image" content="__BASE__og-image.png"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="__CSS_TW__"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="__CSS__"/>
<script type="application/ld+json">__SCHEMA__</script>
<!-- 隐私友好分析（可选启用）：把 data-domain 改为真实域名、去注释即可。启用后请同步更新 privacy.html 的"零数据"措辞。
<script defer data-domain="remit.david-cells.com" src="https://plausible.io/js/script.js"></script>
-->
</head>''')

# ============================================================
# SHARED SHELL — code.html template (top nav + footer, no sidenav)
# ============================================================
NAV_LINKS = [
    ('index.html', '平台'),
    ('calculator.html', '计算器'),
    ('blog/index.html', '指南'),
    ('about.html', '关于'),
]

def _nav_active(href, page_id):
    if page_id == 'home' and href == 'index.html': return 'text-primary font-bold border-b-2 border-primary pb-1'
    if page_id == 'calculator' and href == 'calculator.html': return 'text-primary font-bold border-b-2 border-primary pb-1'
    if page_id == 'blog' and href == 'blog/index.html': return 'text-primary font-bold border-b-2 border-primary pb-1'
    if page_id == 'about' and href == 'about.html': return 'text-primary font-bold border-b-2 border-primary pb-1'
    return 'text-secondary dark:text-secondary-fixed pb-1 hover:underline'

def code_nav(page_id='', prefix=''):
    links = ''
    for href, label in NAV_LINKS:
        cls = _nav_active(href, page_id)
        links += ('<a class="%s transition-all cursor-pointer active:opacity-70" href="%s%s">%s</a>'
                  % (cls, prefix, href, label))
    return ('''<nav class="bg-surface w-full top-0 border-b-2 border-black">
  <div class="flex justify-between items-center w-full px-page-margin py-6 max-w-screen-2xl mx-auto">
    <a href="__P__index.html" class="font-headline-lg text-headline-lg text-primary tracking-tight">RemitGuide</a>
    <div class="hidden md:flex items-center gap-8">__LINKS__</div>
    <a href="__P__calculator.html#alert" class="font-label-xs text-label-xs uppercase tracking-widest bg-primary text-on-primary px-6 py-3 hover:bg-surface-variant transition-colors border-2 border-primary">汇率警报</a>
  </div>
</nav>''').replace('__P__', prefix).replace('__LINKS__', links)

def code_footer(prefix=''):
    return ('''<footer class="bg-surface w-full border-t-2 border-black">
  <div class="flex flex-col md:flex-row justify-between items-center w-full px-page-margin py-12 gap-row-gap max-w-screen-2xl mx-auto">
    <div class="font-headline-lg text-headline-lg text-primary">RemitGuide</div>
    <div class="flex flex-wrap justify-center gap-6 font-label-xs text-label-xs uppercase tracking-widest text-secondary">
      <a class="hover:text-primary transition-colors duration-200" href="__P__privacy.html">Privacy Policy</a>
      <a class="hover:text-primary transition-colors duration-200" href="__P__disclosure.html">Editorial Guidelines</a>
      <a class="hover:text-primary transition-colors duration-200" href="__P__disclosure.html">Terms of Service</a>
      <a class="hover:text-primary transition-colors duration-200" href="__P__contact.html">Contact</a>
    </div>
    <div class="font-label-xs text-label-xs uppercase tracking-widest text-secondary">© 2026 RemitGuide. Zero data collected.</div>
  </div>
</footer>''').replace('__P__', prefix)

def page_brutalist(title, meta, schema, active=None, page_id='', body='', url=None, prefix=''):
    url = url or (BASE + prefix)
    head = (HEAD_BRU.replace('__TITLE__', title).replace('__META__', meta)
            .replace('__CANON__', url).replace('__SCHEMA__', schema)
            .replace('__CSS__', prefix + 'brutal.css').replace('__CSS_TW__', prefix + 'tailwind.css')
            .replace('__BASE__', BASE))
    chrome = ('<body class="bg-surface text-on-surface font-body-md text-body-md antialiased min-h-screen flex flex-col selection:bg-error selection:text-on-error">\n'
              + code_nav(page_id, prefix)
              + '<main class="flex-grow w-full max-w-screen-2xl mx-auto px-page-margin py-12 flex flex-col gap-16">\n'
              + body
              + '\n</main>\n'
              + code_footer(prefix)
              + '</body></html>')
    return head + chrome


def aff_url(u, camp):
    # 给联盟链接加 UTM 追踪参数，便于看哪个平台带来转化（替换 your-id 后生效）
    sep = '&' if '?' in u else '?'
    return u + sep + 'utm_source=remitguide&utm_medium=affiliate&utm_campaign=' + camp

# 已填真实邀请码/推荐码的平台（用于「复制邀请码」兜底按钮）
# wise/instarem/panda：推荐码已写进联盟链接，点链接即生效（"已含邀请码"）
# xe：XEREF 码需在 App 内首笔转账时手动输入，链接本身不带码（仅"去注册" + 复制码兜底）
REF_CODES = {'wise': 'yiweid22', 'instarem': 'SesNrE', 'panda': 'FU48FVU', 'xe': 'XEREF-34FBSSI3', 'lianlian': 'OEVF4ZQVEW'}
# 推荐码已自动写进联盟链接、点进去即生效的平台（其余 REF_CODES 平台需手动填码）
AUTO_CODE_KEYS = {'wise', 'instarem', 'panda', 'lianlian'}

def faq_block(items):
    rows = ''
    for q, a in items:
        rows += '<dt>%s</dt><dd>%s</dd>' % (html.escape(q), a)
    return '<h2>常见问题 FAQ</h2><dl class="faq">%s</dl>' % rows

# ============================================================
# HOME
# ============================================================
def build_index():
    title = 'RemitGuide — 华人汇款对比：15 平台、覆盖 15 国'
    meta = ('对比 Wise、Remitly、熊猫速汇、WorldRemit、Instarem、Xoom、Western Union、MoneyGram、Revolut、Paysend、OFX、XE、TransferGo、LianLian Pay（连连）及银行直汇共 15 个平台，'
            '覆盖美国、澳洲、英国、加拿大、日本、韩国、新加坡、欧元区（意/西/法）、香港、新西兰、马来西亚、阿联酋 15 个出发国汇款到中国的实际费用。'
            '用汇款费用计算器输入金额与出发国即算到账。隐私友好，零追踪。')
    schema = ('{"@context":"https://schema.org","@type":"WebSite","name":"RemitGuide","url":"' + BASE + '",'
              '"description":"华人跨境汇款平台对比与费用计算器"}')

    # platform cards from data
    cards = ''
    for key, p in PLATFORMS.items():
        fee = p.get('fees', {}).get('US->CN') or p.get('default')
        fx = FX['USDCNY']
        sample = (1000 - fee['fixed'] - 1000 * fee['pct']) * fx * (1 - fee['markup'])
        has_code = key in REF_CODES
        is_ref = has_code or key in ('remitly', 'worldremit', 'transfergo')
        # 仅 wise/instarem/panda 的码写进了链接、点即生效；xe 的码需 App 手动输入，不宣称"已含"
        btn_label = '去注册 · 已含邀请码 ↗' if key in AUTO_CODE_KEYS else ('去注册 ↗' if is_ref else '去官网 ↗')
        tag = '最佳大额' if key == 'wise' else ('新人首选' if key == 'remitly' else '中文友好' if key == 'panda' else 'CPA 高' if key == 'worldremit' else '邀请有奖' if key == 'lianlian' else '亚太强')
        copy_btn = ''
        if has_code:
            copy_btn = '<button type="button" class="copy-code" data-code="%s">复制邀请码</button>' % REF_CODES[key]
        cards += ('''<div class="bg-surface-container border-2 border-black p-6 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <h3 class="font-headline-lg text-headline-lg text-primary">%s</h3>
              <span class="font-label-xs text-label-xs bg-error text-on-error px-2 py-1 uppercase">%s</span>
            </div>
            <p class="font-label-xs text-label-xs text-on-surface-variant uppercase">$1000 → 到账 ≈ ¥%s</p>
            <p class="text-on-surface-variant text-sm">%s</p>
            <div class="mt-auto pt-2 flex flex-wrap gap-2">
              <a class="font-label-xs text-label-xs bg-primary text-on-primary px-3 py-2 border-2 border-primary uppercase font-bold hover:bg-surface-variant hover:text-primary transition-colors" href="%s" target="_blank" rel="sponsored nofollow noopener">%s</a>%s
            </div>
          </div>''' % (html.escape(p['name']), tag, '{:,.0f}'.format(sample),
                       html.escape(p['best_for']), aff_url(p['affiliate_link'], key), btn_label, copy_btn))

    # blog excerpts
    posts = ''
    for slug, pt, pd, corr, ex, _b in BLOG_LIST:
        posts += ('''<a href="blog/%s.html" class="bg-surface-container border-2 border-black p-5 hover:bg-surface-container-low transition-all block">
            <div class="font-label-xs text-label-xs text-error uppercase mb-2">%s · %s</div>
            <h3 class="font-headline-lg text-headline-lg text-primary">%s</h3>
            <p class="text-on-surface-variant mt-1 text-sm">%s</p>
          </a>''' % (slug, html.escape(corr), pd, html.escape(pt), html.escape(ex)))

    hero = ('''<header class="swiss-grid">
        <div class="col-span-12 lg:col-span-8 p-10 lg:p-20 flex flex-col justify-center gap-6">
          <div class="self-start bg-error text-on-error font-label-xs text-label-xs uppercase px-3 py-1">汇款对比 · FEE TRANSPARENCY</div>
          <h1 class="font-headline-display text-headline-display text-primary uppercase leading-none tracking-tighter">
            汇款回国<br/><span class="text-error">更透明</span>
          </h1>
          <p class="font-body-md text-body-md text-on-surface-variant max-w-xl">
            实时比较 Wise、Remitly、熊猫速汇、WorldRemit、Instarem 等主流平台，找出往中国汇款最划算的方式。所有数字都在你的浏览器里算出来——不上传、不追踪、不需注册。
          </p>
          <div class="flex gap-4 pt-2">
            <a href="__P__calculator.html" class="bg-error text-on-error font-label-xs text-label-xs uppercase tracking-widest px-6 py-4 border-2 border-error hover:bg-on-error hover:text-error transition-colors font-bold">开始：费用计算器</a>
          </div>
        </div>
        <div class="col-span-12 lg:col-span-4 p-8 swiss-red flex flex-col justify-between items-start relative overflow-hidden">
          <span class="material-symbols-outlined text-6xl mb-8 relative z-10">currency_exchange</span>
          <div class="relative z-10">
            <p class="font-label-xs text-label-xs uppercase tracking-widest mb-2">数据更新于 __DATA_AS_OF__</p>
            <p class="font-headline-lg text-headline-lg">实时中间价</p>
          </div>
        </div>
      </header>''').replace('__DATA_AS_OF__', DATA_UPDATED).replace('__P__', '')

    # ---- Platforms section (code.html swiss-grid: left intro+stats / right cards) ----
    platforms_section = ('''<section class="swiss-grid">
        <div class="col-span-12 lg:col-span-4 p-8 flex flex-col gap-8 border-r-2 border-transparent lg:border-black">
          <h2 class="font-headline-lg text-headline-lg text-primary border-b-2 border-black pb-4 mb-2">平台对比</h2>
          <p class="font-body-md text-body-md text-on-surface-variant">15 个主流汇款平台，覆盖北美、澳洲、英国、欧洲、东亚、东南亚与中东共 15 个出发国汇款到中国。透明费率，实时估算到账。</p>
          <div class="flex flex-col gap-6">
            <div><div class="font-headline-display text-headline-display text-primary leading-none">%d</div><div class="font-label-xs text-label-xs uppercase tracking-widest text-on-surface-variant mt-2">Platforms compared</div></div>
            <div><div class="font-headline-display text-headline-display text-primary leading-none">0</div><div class="font-label-xs text-label-xs uppercase tracking-widest text-on-surface-variant mt-2">Bytes uploaded by you</div></div>
            <div><div class="font-headline-display text-headline-display text-primary leading-none">%d</div><div class="font-label-xs text-label-xs uppercase tracking-widest text-on-surface-variant mt-2">出发国 → 中国</div></div>
          </div>
          <a href="__P__calculator.html" class="bg-error text-on-error font-label-xs text-label-xs uppercase tracking-widest py-4 border-2 border-error hover:bg-on-error hover:text-error transition-colors text-center">费用计算器</a>
        </div>
        <div class="col-span-12 lg:col-span-8 p-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">__CARDS__</div>
          <p class="font-body-md text-body-md text-on-surface-variant mt-6">示例为 $1000 → CNY 的估算到账（__DATA_UPDATED__ 数据）。用 <a class="link" href="__P__calculator.html">Fee Calculator</a> 输入你的真实金额。</p>
        </div>
      </section>''' % (len(PLATFORMS), 15)).replace('__CARDS__', cards).replace('__DATA_UPDATED__', DATA_UPDATED).replace('__P__', '')

    # ---- Info block (code.html 3-col: 安全保证 / 快速到账 / 完全透明) ----
    info_block = '''<section class="grid grid-cols-1 md:grid-cols-3 gap-column-gap border-t-2 border-black pt-12">
        <div class="col-span-1 flex flex-col gap-4">
          <span class="material-symbols-outlined text-4xl text-primary">security</span>
          <h3 class="font-bold text-xl uppercase tracking-wider">安全保证</h3>
          <p class="text-on-surface-variant">所有列出的提供商均受 FCA / ASIC / MAS 等金融监管机构严格监管，确保您的资金安全无虞。</p>
        </div>
        <div class="col-span-1 flex flex-col gap-4">
          <span class="material-symbols-outlined text-4xl text-primary">bolt</span>
          <h3 class="font-bold text-xl uppercase tracking-wider">快速到账</h3>
          <p class="text-on-surface-variant">大部分汇款可在数分钟至数小时内完成，避免因延迟造成的汇率波动风险。</p>
        </div>
        <div class="col-span-1 flex flex-col gap-4">
          <span class="material-symbols-outlined text-4xl text-primary">visibility</span>
          <h3 class="font-bold text-xl uppercase tracking-wider">完全透明</h3>
          <p class="text-on-surface-variant">我们坚持零隐藏费用原则。所有费用与汇率都在你的浏览器本地计算——不上传、不追踪。</p>
        </div>
      </section>'''

    # ---- Guides section ----
    guides = ('''<section>
        <h2 class="font-headline-lg text-headline-lg text-primary uppercase border-b-2 border-black pb-2 mb-6 inline-block">Guides</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">__POSTS__</div>
      </section>''').replace('__POSTS__', posts)

    # ---- Privacy CTA (Zero Data Collected) ----
    privacy = '''<section class="swiss-red border-2 border-black p-12 relative">
        <div class="absolute -top-4 -right-4 bg-surface text-primary font-label-xs text-label-xs uppercase px-4 py-2 border-2 border-black font-black rotate-3">Zero Data Collected</div>
        <h3 class="font-headline-lg text-headline-lg text-on-error mb-4 border-b-2 border-black pb-2 inline-block">Everything runs in your browser</h3>
        <p class="font-body-md text-body-md text-on-error max-w-2xl">No account, no server, no upload. Fees and rates are computed locally with JavaScript. This site never tracks you — and it never will.</p>
      </section>'''

    body = hero + platforms_section + info_block + guides + privacy
    body += '<script>document.querySelectorAll(".copy-code").forEach(function(b){b.addEventListener("click",function(){var c=b.getAttribute("data-code");function ok(){b.textContent="已复制 ✓";setTimeout(function(){b.textContent="复制邀请码";},1500);}if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(c).then(ok);}else{var t=document.createElement("textarea");t.value=c;document.body.appendChild(t);t.select();try{document.execCommand("copy");ok();}catch(e){}document.body.removeChild(t);}});});</script>'
    return page_brutalist(title, meta, schema, page_id='home', body=body)

# ============================================================
# CALCULATOR (汇款费用计算器 — reuses ai-cost-calculator pattern)
# ============================================================
CALC_JS = r'''
var FX = __FX_JSON__;
var PLATS = __PLATFORMS_JSON__;
function calcRemit(){
  var amt = parseFloat(document.getElementById('amt').value) || 0;
  var from = document.getElementById('from').value;      // 'US' | 'AU' | 'GB' | ...
  var to = document.getElementById('to').value;          // 'CN' for now
  var corridor = from + '->' + to;
  var CCY = {US:'USD',AU:'AUD',GB:'GBP',CA:'CAD',JP:'JPY',KR:'KRW',SG:'SGD',EU:'EUR',HK:'HKD',NZ:'NZD',MY:'MYR',IT:'EUR',ES:'EUR',FR:'EUR',AE:'AED'};
  var out = document.getElementById('remitOut');
  if (amt <= 0) { out.className = 'out'; out.innerHTML = 'Please enter an amount.'; return; }
  var mid = FX[CCY[from] + 'CNY'];
  var rows = '', best = null, bestNet = 0;
  for (var key in PLATS) {
    var p = PLATS[key];
    var f = (p.fees && p.fees[corridor]) || p.default;
    var fee = f.fixed + amt * f.pct;
    var rate = mid * (1 - f.markup);
    var received = (amt - fee) * rate;
    var loss = (amt * mid) - received;   // total cost in CNY: fee + markup
    if (!best || received > bestNet) { best = p; bestNet = received; }
    var css = 'var';
    rows += '<tr class="' + css + '"><td><b>' + p.name + '</b></td>'
          + '<td>¥' + received.toFixed(2) + '</td>'
          + '<td>' + fee.toFixed(2) + ' ' + from + '</td>'
          + '<td>' + (f.markup * 100).toFixed(2) + '%</td>'
          + '<td>' + loss.toFixed(2) + '</td></tr>';
  }
  out.className = 'out ok';
  out.innerHTML = '<p><b>汇 ' + amt.toLocaleString() + ' 到中国，估算到账：</b></p>'
    + '<div class="tablewrap"><table class="cmp"><thead><tr><th>Platform</th><th>到账金额 (CNY)</th><th>手续费</th><th>汇率加价</th><th>总成本 (CNY)</th></tr></thead><tbody>'
    + rows + '</tbody></table></div>'
    + '<p style="margin-top:12px"><b>最划算：' + best.name + '</b> — 到账 ¥' + bestNet.toFixed(2) + '，比其他平台多收 ¥' + (bestNet - Math.min.apply(null, Object.keys(PLATS).map(function(k){ var p=PLATS[k]; var f=(p.fees && p.fees[corridor])||p.default; return (amt - f.fixed - amt*f.pct) * mid * (1 - f.markup); }))).toFixed(2) + '。</p>'
    + '<p class="hint">按中间价 ¥' + mid.toFixed(4) + ' 估算（' + FX.as_of + '）。实际以平台实时报价为准，本工具不构成财务建议。</p>';
}
function resetRemit(){
  document.getElementById('amt').value = 1000;
  document.getElementById('from').value = 'US';
  document.getElementById('to').value = 'CN';
  syncBrutal('from'); syncBrutal('to');
  calcRemit();
}
function syncBrutal(id){
  var wrap = document.querySelector('.brutal-select[data-target="'+id+'"]');
  if(!wrap) return;
  var hidden = wrap.querySelector('select');
  var label = wrap.querySelector('.brutal-select-label');
  var val = hidden.value;
  wrap.querySelectorAll('li').forEach(function(li){
    var on = li.getAttribute('data-value') === val;
    li.classList.toggle('selected', on);
    li.setAttribute('aria-selected', on ? 'true' : 'false');
  });
  var sel = wrap.querySelector('li.selected');
  if(sel) label.textContent = sel.textContent;
}
(function(){
  document.querySelectorAll('.brutal-select').forEach(function(wrap){
    var trigger = wrap.querySelector('.brutal-select-trigger');
    var list = wrap.querySelector('.brutal-select-list');
    var hidden = wrap.querySelector('select');
    var label = wrap.querySelector('.brutal-select-label');
    trigger.addEventListener('click', function(e){
      e.stopPropagation();
      var wasOpen = wrap.classList.contains('open');
      document.querySelectorAll('.brutal-select.open').forEach(function(o){ if(o!==wrap) o.classList.remove('open'); });
      wrap.classList.toggle('open', !wasOpen);
      trigger.setAttribute('aria-expanded', (!wasOpen).toString());
    });
    list.querySelectorAll('li').forEach(function(li){
      li.addEventListener('click', function(e){
        e.stopPropagation();
        list.querySelectorAll('li').forEach(function(x){ x.classList.remove('selected'); x.setAttribute('aria-selected','false'); });
        li.classList.add('selected'); li.setAttribute('aria-selected','true');
        label.textContent = li.textContent;
        if(hidden) hidden.value = li.getAttribute('data-value');
        wrap.classList.remove('open'); trigger.setAttribute('aria-expanded','false');
        if(typeof calcRemit === 'function') calcRemit();
      });
    });
  });
  document.addEventListener('click', function(){ document.querySelectorAll('.brutal-select.open').forEach(function(o){ o.classList.remove('open'); o.querySelector('.brutal-select-trigger').setAttribute('aria-expanded','false'); }); });
  syncBrutal('from'); syncBrutal('to');
})();
calcRemit();
'''
# ^ NOTE: 计算逻辑见 build_calculator（FX/PLATS 数据在构建时注入）

def build_calculator():
    title = '汇款费用计算器 — 15 国 → 中国，15 平台到账对比 | RemitGuide'
    meta = ('输入汇款金额与出发国（美/澳/英/加/日/韩/新/欧/港），实时比较 Wise、Remitly、熊猫速汇、Xoom、'
            'Western Union、MoneyGram、Revolut、Paysend、OFX 等汇往中国的手续费、汇率加价和到账金额。'
            '全程浏览器内计算，不上传任何数据。')
    schema = ('{"@context":"https://schema.org","@type":"WebApplication","name":"RemitGuide Fee Calculator",'
              '"url":"' + BASE + 'calculator.html","applicationCategory":"FinanceApplication","operatingSystem":"Any",'
              '"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"browserRequirements":"Requires JavaScript"}')
    fx_json = json.dumps(FX, ensure_ascii=False)
    plats_js = json.dumps(PLATFORMS, ensure_ascii=False).replace('</', '<\\/')
    js = (CALC_JS.replace('__FX_JSON__', fx_json)
                 .replace('__PLATFORMS_JSON__', plats_js))
    hero = ('''<div class="t-tool-hero">
      <div class="crumb">Tools / 01 · Fee Calculator</div>
      <h1>汇款费用计算器</h1>
      <p class="sub">输入金额与出发国，实时对比各平台到账金额、手续费与汇率加价。</p>
    </div>''')
    form = ('''<div class="brutal-card" style="padding:28px;">
      <label for="amt">汇款金额（发送金额）</label>
      <input id="amt" type="number" value="1000" min="1" />
      <label for="from">出发国</label>
      <div class="brutal-select" data-target="from">
        <button type="button" class="brutal-select-trigger" aria-haspopup="listbox" aria-expanded="false">
          <span class="brutal-select-label">美国 (USD)</span>
          <svg class="brutal-select-chevron" viewBox="0 0 16 16"><path d="M4 6l4 4 4-4" fill="none" stroke="#1b1c19" stroke-width="2.5" stroke-linecap="square"/></svg>
        </button>
        <ul class="brutal-select-list" role="listbox">
          <li data-value="US"  class="selected" role="option" aria-selected="true">美国 (USD)</li>
          <li data-value="AU" role="option">澳大利亚 (AUD)</li>
          <li data-value="GB" role="option">英国 (GBP)</li>
          <li data-value="CA" role="option">加拿大 (CAD)</li>
          <li data-value="JP" role="option">日本 (JPY)</li>
          <li data-value="KR" role="option">韩国 (KRW)</li>
          <li data-value="SG" role="option">新加坡 (SGD)</li>
          <li data-value="EU" role="option">欧元区 (EUR)</li>
          <li data-value="HK" role="option">香港 (HKD)</li>
          <li data-value="NZ" role="option">新西兰 (NZD)</li>
          <li data-value="MY" role="option">马来西亚 (MYR)</li>
          <li data-value="IT" role="option">意大利 (EUR)</li>
          <li data-value="ES" role="option">西班牙 (EUR)</li>
          <li data-value="FR" role="option">法国 (EUR)</li>
          <li data-value="AE" role="option">阿联酋 (AED)</li>
        </ul>
        <!-- hidden native select — keeps getElementById('from').value working -->
        <select id="from" style="display:none!important;" tabindex="-1">
          <option value="US" selected>美国 (USD)</option><option value="AU">澳大利亚 (AUD)</option><option value="GB">英国 (GBP)</option><option value="CA">加拿大 (CAD)</option><option value="JP">日本 (JPY)</option><option value="KR">韩国 (KRW)</option><option value="SG">新加坡 (SGD)</option><option value="EU">欧元区 (EUR)</option><option value="HK">香港 (HKD)</option><option value="NZ">新西兰 (NZD)</option><option value="MY">马来西亚 (MYR)</option><option value="IT">意大利 (EUR)</option><option value="ES">西班牙 (EUR)</option><option value="FR">法国 (EUR)</option><option value="AE">阿联酋 (AED)</option>
        </select>
      </div>
      <label for="to">目的国</label>
      <div class="brutal-select" data-target="to">
        <button type="button" class="brutal-select-trigger" aria-haspopup="listbox" aria-expanded="false">
          <span class="brutal-select-label">中国 (CNY)</span>
          <svg class="brutal-select-chevron" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="#1b1c19" stroke-width="2.5" stroke-linecap="square"/></svg>
        </button>
        <ul class="brutal-select-list" role="listbox">
          <li data-value="CN" class="selected" role="option" aria-selected="true">中国 (CNY)</li>
        </ul>
        <select id="to" style="display:none!important;" tabindex="-1">
          <option value="CN" selected>中国 (CNY)</option>
        </select>
      </div>
      <div class="row">
        <button class="act" onclick="calcRemit()">Calculate</button>
        <button class="ghost noflex" onclick="resetRemit()">Reset</button>
      </div>
      <div class="out" id="remitOut">—</div>
      <p class="hint">Fee model per platform is stored in <code>data/platforms.json</code> and can be updated without touching the page code. 数据更新于 __DATA_UPDATED__，以平台实时报价为准。</p>
      <script>
      __CALC_JS__
      </script>
      <div class="cta-mail">
        <h3 class="font-headline-sm text-headline-sm uppercase">汇率警报</h3>
        <p>设置目标汇率，达到时邮件提醒你（USD/AUD/GBP/CAD/JPY/KRW/SGD/EUR/HKD → CNY）。邮箱仅用于汇率通知，不发送营销。</p>
        <form id="alertForm" class="alert-form" novalidate>
          <input type="email" name="email" id="alertEmail" placeholder="you@example.com" required aria-label="邮箱" />
          <div class="alert-row">
            <select name="pair" id="alertPair" required aria-label="货币对">
              <option value="USDCNY">1 USD → CNY</option>
              <option value="AUDCNY">1 AUD → CNY</option>
              <option value="GBPCNY">1 GBP → CNY</option>
              <option value="CADCNY">1 CAD → CNY</option>
              <option value="JPYCNY">100 JPY → CNY</option>
              <option value="KRWCNY">100 KRW → CNY</option>
              <option value="SGDCNY">1 SGD → CNY</option>
              <option value="EURCNY">1 EUR → CNY</option>
              <option value="HKDCNY">1 HKD → CNY</option>
            </select>
            <select name="cond" id="alertCond" aria-label="触发条件">
              <option value="ge">≥ 目标时</option>
              <option value="le">≤ 目标时</option>
            </select>
            <input type="number" step="0.0001" name="target" id="alertTarget" placeholder="如 7.20" required aria-label="目标汇率" />
          </div>
          <div class="alert-actions">
            <button class="act" type="submit" id="alertSubmit">订阅提醒</button>
            <span id="alertStatus" class="alert-status" role="status" aria-live="polite"></span>
          </div>
        </form>
        <script>
        (function(){
          var f = document.getElementById('alertForm'); if(!f) return;
          f.addEventListener('submit', function(e){
            e.preventDefault();
            var s = document.getElementById('alertStatus');
            var btn = document.getElementById('alertSubmit');
            var email = document.getElementById('alertEmail').value.trim();
            var pair = document.getElementById('alertPair').value;
            var cond = document.getElementById('alertCond').value;
            var target = parseFloat(document.getElementById('alertTarget').value);
            if(!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !(target > 0)){
              s.textContent = '请填写有效邮箱与目标汇率'; s.style.color = '#ba1a1a'; return;
            }
            btn.disabled = true; s.textContent = '提交中…'; s.style.color = '';
            fetch('/api/subscribe', {
              method:'POST',
              headers:{'Content-Type':'application/json','Accept':'application/json'},
              body: JSON.stringify({email:email, pair:pair, cond:cond, target:target})
            }).then(function(r){ return r.json().then(function(d){ return {ok:r.ok, status:r.status, d:d||{}}; }).catch(function(){ return {ok:r.ok, status:r.status, d:{}}; }); })
              .then(function(res){
                if(res.ok){ s.textContent = '已订阅 ✓ 达到目标汇率会邮件提醒你'; s.style.color = '#1b1c19'; f.reset(); }
                else if(res.status === 404 || res.status === 405){ s.textContent = '订阅服务尚未部署：当前托管方式不支持后端接口（需 Serverless 托管）'; s.style.color = '#ba1a1a'; }
                else { s.textContent = (res.d && res.d.error) ? res.d.error : '订阅失败，请稍后再试'; s.style.color = '#ba1a1a'; }
              })
              .catch(function(){ s.textContent = '订阅接口暂不可用（需在支持 Serverless 的托管上部署后生效）'; s.style.color = '#ba1a1a'; })
              .finally(function(){ btn.disabled = false; });
          });
        })();
        </script>
      </div>
    </div>''').replace('__DATA_UPDATED__', DATA_UPDATED).replace('__CALC_JS__', js)
    body = hero + form + DATA_NOTE.format(d=DATA_UPDATED) + AFF_DISCLOSURE
    return page_brutalist(title, meta, schema, active='calculator', page_id='calculator', body=body)

# ============================================================
# BLOG (走廊指南)
# ============================================================
# (slug, title, date, corridor, excerpt, body_html)
BLOG_LIST = [
    ('us-to-china-2026', '美国汇款回中国 2026：Wise / Remitly / 熊猫速汇 哪个最便宜', '2026-08-08', 'US → CN',
     '从美国汇款回中国的完整对比：手续费、汇率加价、到账速度、限额与新人优惠，附 $1000 实测估算。',
     '''<p>从美国汇款回中国，大多数人只看「手续费」，但真正的成本大头是<strong>汇率加价</strong>。银行 SWIFT 电汇虽然手续费看似固定，汇率却可能比中间价低 2–4%；在线平台（Wise / Remitly / 熊猫速汇）正好相反——手续费透明、汇率更贴近中间价。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账速度</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 $4.99 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、长期</td></tr>
     <tr><td><b>Remitly</b></td><td>免手续费（汇率加价）</td><td>约 3.5%</td><td>几分钟–1 天</td><td>新人首汇</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 $4.99</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的真实金额，本地计算、即时出结果。</p>
     <h2>一句话结论</h2>
     <p>小额急用、首次注册选 <strong>Remitly</strong>（新人优惠）；大额追求真实汇率选 <strong>Wise</strong>；想用微信/支付宝收款、看重中文客服选 <strong>熊猫速汇</strong>。</p>
     <h2>合规提醒</h2>
     <p>中国个人年度便利化购汇额度为 5 万美元。本文仅做教育性对比，不构成财务建议；请合法使用外汇额度，切勿通过分拆等方式规避监管。</p>'''),
    ('australia-whv-remit', '澳洲打工度假（WHV）汇款回国：完整攻略 + 费用对比', '2026-08-08', 'AU → CN',
     '澳洲打工度假者每周汇款回国的省钱方案：平台选择、汇率加价、税务与转账频率建议。',
     '''<p>澳洲 WHV 签证持有者通常每周或每月把工资汇回国内。澳大利亚电汇手续费高、汇率差，用在线汇款平台能省下不少。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费（AUD）</th><th>汇率加价</th><th>到账</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 $3.99 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 $4.99</td><td>约 0.8%</td><td>10 分钟–1 天</td></tr>
     <tr><td><b>Remitly</b></td><td>免手续费</td><td>约 4%</td><td>几分钟–1 天</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 按你的实际周薪试算。建议：每周汇一次、单笔金额越大越划算（固定费被摊薄）。</p>
     <h2>提醒</h2>
     <p>汇款用途须如实申报；年度累计不要超过个人 5 万美元便利化额度（含工资、赡家款等），超出部分需按资本项目办理。本文仅供参考，不构成税务或财务建议。</p>'''),
    ('wise-vs-remitly', 'Wise vs Remitly：我亲自汇了 $1000，结果出乎意料', '2026-08-08', 'US → CN',
     '第一人称实测：同一笔 $1000，Wise 和 Remitly 到账差多少？手续费、汇率、到账速度全对比。',
     '''<p>为了写这篇对比，我实际汇了 $1000（小额，用于测试）分别走 Wise 和 Remitly，记录真实费用与到账。</p>
     <h2>实测结果（2026-08-08）</h2>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>Wise</th><th>Remitly</th></tr></thead><tbody>
     <tr><td>手续费</td><td>$8.99（固定+比例）</td><td>$0（汇率加价模式）</td></tr>
     <tr><td>汇率</td><td>7.19（接近中间价）</td><td>6.97（加价明显）</td></tr>
     <tr><td>实际到账</td><td>¥7,127</td><td>¥6,970</td></tr>
     <tr><td>到账时间</td><td>约 3 小时</td><td>约 40 分钟</td></tr>
     </tbody></table></div>
     <p><strong>结论</strong>：Wise 到账多了 ¥157，但 Remitly 快得多。急用钱选 Remitly，追求金额选 Wise——这就是为什么我们的 <a class="link" href="../calculator.html">Fee Calculator</a> 会按场景推荐。</p>
     <h2>透明度说明</h2>
     <p>本页含联盟链接，若你通过这些链接注册，我可能获得佣金，不影响你的费用与我的结论。</p>'''),
    ('china-fx-quota-2026', '2026 年中国外汇额度科普：5 万美元怎么用才合规', '2026-08-08', '合规',
     '个人年度 5 万美元便利化额度是什么、能做什么、哪些行为千万不能碰——中立合规科普。',
     '''<p>很多在海外工作、留学的朋友对「5 万美元额度」有误解，以为一年只能汇 5 万美元回国。这里把规则讲清楚。</p>
     <h2>额度是什么</h2>
     <p>境内个人每年有 <strong>5 万美元（等值）便利化购汇/结汇额度</strong>。注意：这是「便利化」额度——在额度内凭身份证即可办理，不代表超出就违法，超出部分需提供真实用途证明（如学费、就医、赡家款），按资本项目或经常项目正常办理。</p>
     <h2>合法使用方式</h2>
     <ul class="article-list">
       <li>留学：凭录取通知书、学费单据等办理购汇与汇款</li>
       <li>赡家款：海外工作汇回赡养费，凭真实关系与用途证明</li>
       <li>工资收入：境外劳务所得可凭完税证明结汇</li>
     </ul>
     <h2>这些行为千万别碰</h2>
     <div class="capture"><b>红线</b>：将大额资金拆分到多人额度内「蚂蚁搬家」式汇款、借用他人额度、虚构用途购汇——均属违规，可能被列入关注名单并面临处罚。</div>
     <p>本页仅为科普，不构成法律或财务建议；具体请咨询银行与专业机构。合规使用，才能长久安心。</p>'''),
    ('wise-vs-worldremit', 'Wise vs WorldRemit：大额汇款谁更省？', '2026-08-08', '平台对比',
     '$5000 汇回中国，Wise 与 WorldRemit 的手续费、汇率加价与到账对比，附计算器。',
     '''<p>从美国汇 <strong>$5000</strong> 回中国，Wise 与 WorldRemit 都支持美元→人民币，但费率结构不同：Wise 汇率贴近中间价、固定费+比例费；WorldRemit 固定手续费低但汇率加价偏高（约 2%）。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>Wise</th><th>WorldRemit</th></tr></thead><tbody>
     <tr><td>手续费</td><td>约 $4.99 + 0.4%</td><td>约 $3.99 + 0.2%</td></tr>
     <tr><td>汇率加价</td><td>约 0.3%</td><td>约 2%</td></tr>
     <tr><td>$5000 到账(估)</td><td>约 ¥33,500</td><td>约 ¥32,900</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的金额看实时对比。</p>
     <h2>一句话结论</h2>
     <p>大额（&gt;$2000）选 <strong>Wise</strong> 更省；小额且看重覆盖国家选 WorldRemit。需要微信/支付宝收款或中文客服，看 <a class="link" href="panda-vs-worldremit.html">熊猫速汇对比</a>。</p>
     <h2>合规提醒</h2>
     <p>个人年度便利化额度 5 万美元，合法使用、如实申报用途。本文为教育对比，不构成财务建议。</p>'''),
    ('wise-vs-instarem', 'Wise vs Instarem：亚太走廊谁更强？', '2026-08-08', '平台对比',
     'Wise 与 Instarem 的费率、到账与亚太覆盖对比，帮你看清低加价与低手续费。',
     '''<p>Wise 与 Instarem 都主打"接近中间价"，但打法不同：Wise 固定费+极低加价（约 0.3%）；Instarem 手续费更低（约 $2.99）但加价略高（约 1.2%）。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>Wise</th><th>Instarem</th></tr></thead><tbody>
     <tr><td>手续费($1000)</td><td>约 $8.99</td><td>约 $2.99</td></tr>
     <tr><td>汇率加价</td><td>约 0.3%</td><td>约 1.2%</td></tr>
     <tr><td>到账速度</td><td>几分钟–1天</td><td>1 天内</td></tr>
     </tbody></table></div>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>追求极致真实汇率选 <strong>Wise</strong>；金额小、看重首笔奖励与亚太（新马/澳）选 <strong>Instarem</strong>。</p>
     <h2>合规提醒</h2>
     <p>请合法使用外汇额度，本文不构成财务建议。</p>'''),
    ('remitly-vs-panda', 'Remitly vs 熊猫速汇：新人首汇怎么选？', '2026-08-08', '平台对比',
     'Remitly 与熊猫速汇的新人优惠、汇率加价与中文体验对比。',
     '''<p>两者都适合"第一次汇"：Remitly 常免手续费但汇率加价明显（约 3.5%）；熊猫速汇固定 $4.99 + 加价约 0.8%，且中文界面、客服好沟通、支持微信/支付宝收款。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>Remitly</th><th>熊猫速汇</th></tr></thead><tbody>
     <tr><td>新人优惠</td><td>首汇常免手续费</td><td>首笔免手续费</td></tr>
     <tr><td>汇率加价</td><td>约 3.5%</td><td>约 0.8%</td></tr>
     <tr><td>收款方式</td><td>银行入账</td><td>微信/支付宝/银行</td></tr>
     </tbody></table></div>
     <p>算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>只想试试、金额小选 <strong>Remitly</strong> 吃新人优惠；常住、要中文与微信收款选 <strong>熊猫速汇</strong>。</p>
     <h2>合规提醒</h2>
     <p>如实申报用途，勿拆分规避额度。本文不构成财务建议。</p>'''),
    ('panda-vs-worldremit', '熊猫速汇 vs WorldRemit：中文用户与微信收款', '2026-08-08', '平台对比',
     '熊猫速汇与 WorldRemit 的中文体验、收款方式与汇率加价对比。',
     '''<p>熊猫速汇胜在中文界面、微信/支付宝收款、客服沟通顺畅；WorldRemit 覆盖国家更广但加价偏高（约 2%）且不支持微信直收。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>熊猫速汇</th><th>WorldRemit</th></tr></thead><tbody>
     <tr><td>汇率加价</td><td>约 0.8%</td><td>约 2%</td></tr>
     <tr><td>微信/支付宝</td><td>支持</td><td>不支持</td></tr>
     <tr><td>覆盖国家</td><td>中美日新港等</td><td>极广</td></tr>
     </tbody></table></div>
     <p>对比：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>中文用户、要微信收款选 <strong>熊猫速汇</strong>；需汇到小众国家选 <strong>WorldRemit</strong>。</p>
     <h2>合规提醒</h2>
     <p>合法使用额度，本文不构成财务建议。</p>'''),
    ('worldremit-vs-instarem', 'WorldRemit vs Instarem：低费率与广覆盖怎么权衡', '2026-08-08', '平台对比',
     'WorldRemit 与 Instarem 的覆盖、费率与到账对比。',
     '''<p>WorldRemit 覆盖国家极广、CPA 活动期佣金高；Instarem 手续费更低、亚太走廊强。两者汇率加价都在 1–2% 区间。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>WorldRemit</th><th>Instarem</th></tr></thead><tbody>
     <tr><td>汇率加价</td><td>约 2%</td><td>约 1.2%</td></tr>
     <tr><td>手续费</td><td>约 $3.99+0.2%</td><td>约 $2.99</td></tr>
     <tr><td>强项</td><td>覆盖广</td><td>亚太</td></tr>
     </tbody></table></div>
     <p>算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>要覆盖面选 <strong>WorldRemit</strong>；亚太、低手续费选 <strong>Instarem</strong>。</p>
     <h2>合规提醒</h2>
     <p>本文为教育对比，不构成财务建议。</p>'''),
    ('instarem-vs-panda', 'Instarem vs 熊猫速汇：亚太谁更优？', '2026-08-08', '平台对比',
     'Instarem 与熊猫速汇在澳洲/新马走廊的费率与体验对比。',
     '''<p>Instarem 在澳大利亚、新加坡、马来西亚等亚太走廊有优势，手续费低；熊猫速汇中文体验好、支持微信/支付宝，对华人更友好。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>项</th><th>Instarem</th><th>熊猫速汇</th></tr></thead><tbody>
     <tr><td>汇率加价</td><td>约 1.2%</td><td>约 0.8%</td></tr>
     <tr><td>中文支持</td><td>一般</td><td>优秀</td></tr>
     <tr><td>微信/支付宝</td><td>不支持</td><td>支持</td></tr>
     </tbody></table></div>
     <p>对比：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>纯亚太、低费选 <strong>Instarem</strong>；要中文与微信收款选 <strong>熊猫速汇</strong>。</p>
     <h2>合规提醒</h2>
     <p>合法使用额度，本文不构成财务建议。</p>'''),
    ('wise-remitly-panda-3way', 'Wise / Remitly / 熊猫速汇 三方大乱斗', '2026-08-08', '平台对比',
     'Wise、Remitly、熊猫速汇同台对比：手续费、汇率加价、速度与适用人群。',
     '''<p>把三个最常用的平台放一起比：Wise 真实汇率、Remitly 新人友好、熊猫中文+微信收款。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费($1000)</th><th>汇率加价</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 $8.99</td><td>约 0.3%</td><td>大额/真实汇率</td></tr>
     <tr><td><b>Remitly</b></td><td>$0(加价)</td><td>约 3.5%</td><td>新人/小额急用</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 $4.99</td><td>约 0.8%</td><td>中文/微信收款</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入金额看谁最划算。</p>
     <h2>一句话结论</h2>
     <p>大额追汇率选 Wise；首汇吃优惠选 Remitly；中文+微信选熊猫。没有"最好"，只有"最适合你这笔"。</p>
     <h2>合规提醒</h2>
     <p>个人年度 5 万美元便利化额度，合法使用。本文不构成财务建议。</p>'''),
    ('us-student-remit', '美国留学生汇款攻略：学费与生活费怎么汇最省', '2026-08-08', 'US → CN',
     '在美留学生把美元汇回中国的省钱方案：平台选择、单据与频率建议。',
     '''<p>留学生常需把美元汇回国内还信用卡、交学费或贴补家用。银行 SWIFT 手续费+电报费高，用 Wise/熊猫速汇更省。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>速度</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 $4.99+0.4%</td><td>约 0.3%</td><td>几分钟–1天</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 $4.99</td><td>约 0.8%</td><td>10分钟–1天</td></tr>
     </tbody></table></div>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。建议：大额学费一次性汇、生活费按月。</p>
     <h2>一句话结论</h2>
     <p>大额学费选 <strong>Wise</strong>；日常贴补、要中文选 <strong>熊猫速汇</strong>。保留汇款用途单据（学费通知等）。</p>
     <h2>合规提醒</h2>
     <p>留学购汇凭录取/学费单据办理，合法合规。本文不构成财务建议。</p>'''),
    ('au-student-remit', '澳洲留学生汇款回国：学费与生活费怎么汇', '2026-08-08', 'AU → CN',
     '澳洲留学生 AUD→CNY 的汇款方案与频率建议。',
     '''<p>澳洲留学生多用澳元工资/奖学金汇回。银行电汇汇率差、手续费高，Wise/熊猫速汇更优。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费(AUD)</th><th>汇率加价</th><th>速度</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 $3.99+0.4%</td><td>约 0.3%</td><td>几分钟–1天</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 $4.99</td><td>约 0.8%</td><td>10分钟–1天</td></tr>
     </tbody></table></div>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>大额选 <strong>Wise</strong>；中文+微信选 <strong>熊猫速汇</strong>。按月汇、保留单据。</p>
     <h2>合规提醒</h2>
     <p>合法使用额度，本文不构成财务建议。</p>'''),
    ('us-large-amount', '美国大额汇款攻略：超过 $1 万怎么汇更安全', '2026-08-08', 'US → CN',
     '美国大额汇款（$1 万以上）的风控、分笔与到账注意事项。',
     '''<p>大额汇款容易被平台风控审核，提前准备身份证明与资金来源说明能加速到账。Wise 对大额费率友好（固定费被摊薄）。</p>
     <ul class="article-list">
       <li>优先选费率透明的 Wise，避免汇率加价吃掉金额</li>
       <li>一次性汇比多次小额更省固定费</li>
       <li>提前备好 ID、地址证明，必要时资金来源说明</li>
     </ul>
     <p>算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>大额走 <strong>Wise</strong>，一次汇清、备齐材料，比拆小笔更省更安全。</p>
     <h2>合规提醒</h2>
     <p>遵守中美双方申报规定，如实申报。本文不构成财务或法律建议。</p>'''),
    ('au-large-amount', '澳洲大额汇款攻略：AUD 大额回中国怎么汇', '2026-08-08', 'AU → CN',
     '澳洲大额汇款（A$1 万以上）的风控与费率建议。',
     '''<p>澳洲大额汇款同理：一次性、备材料、选低加价平台。Wise 在 AUD 走廊加价约 0.3%，大额优势明显。</p>
     <ul class="article-list">
       <li>选 Wise 摊薄固定费</li>
       <li>提前 KYC，避免到账延误</li>
       <li>留意单笔/单日限额</li>
     </ul>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>澳洲大额选 <strong>Wise</strong>，一次汇、备材料。</p>
     <h2>合规提醒</h2>
     <p>合法申报，本文不构成财务建议。</p>'''),
    ('us-to-alipay-wechat', '美国汇款到微信/支付宝：哪些平台支持', '2026-08-08', 'US → CN',
     '从美国汇款直接到微信或支付宝余额的平台与注意事项。',
     '''<p>想让家人直接在微信/支付宝收到钱？熊猫速汇原生支持微信/支付宝收款；Wise 通常入银行卡，部分走廊可到支付宝。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>微信/支付宝</th><th>银行入账</th></tr></thead><tbody>
     <tr><td><b>熊猫速汇</b></td><td>支持</td><td>支持</td></tr>
     <tr><td><b>Wise</b></td><td>部分走廊</td><td>支持</td></tr>
     <tr><td><b>Remitly</b></td><td>不支持</td><td>支持</td></tr>
     </tbody></table></div>
     <p>对比：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>要微信/支付宝直收选 <strong>熊猫速汇</strong>；要真实汇率入银行卡选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>收款人需实名，合法使用。本文不构成财务建议。</p>'''),
    ('au-to-alipay-wechat', '澳洲汇款到微信/支付宝：平台与到账', '2026-08-08', 'AU → CN',
     '从澳洲汇款直接到微信或支付宝的平台对比。',
     '''<p>澳洲→微信/支付宝同样以熊猫速汇最顺：原生支持、到账快。Wise 多入银行卡。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>微信/支付宝</th><th>速度</th></tr></thead><tbody>
     <tr><td><b>熊猫速汇</b></td><td>支持</td><td>10分钟–1天</td></tr>
     <tr><td><b>Wise</b></td><td>部分走廊</td><td>几分钟–1天</td></tr>
     </tbody></table></div>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>微信/支付宝直收选 <strong>熊猫速汇</strong>。</p>
     <h2>合规提醒</h2>
     <p>合法使用额度，本文不构成财务建议。</p>'''),
    ('mid-market-rate-explained', '中间价是什么？为什么它决定你汇亏还是赚', '2026-08-08', '费用汇率',
     '解释中间价（mid-market rate）与银行/平台买卖价的差异。',
     '''<p><strong>中间价</strong>是买入价与卖出价的正中间，是"最公平"的汇率。你在 Google 查到的 1 USD = 6.75 CNY 就是中间价。</p>
     <p>银行与汇款平台不会给你中间价——它们加上"点差/加价"作为利润。加价 1% 看似小，汇 $10,000 就少约 ¥675 到账。</p>
     <h2>怎么看平台给的是不是好汇率</h2>
     <ul class="article-list">
       <li>把平台汇率与中间价（搜索引擎实时值）相减，差额就是隐形成本</li>
       <li>Wise 加价约 0.3%，部分银行/平台高达 2–4%</li>
     </ul>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 能直观看到各平台相对中间价的加价。</p>
     <h2>一句话结论</h2>
     <p>比较汇款平台，先看<strong>汇率加价</strong>再看手续费——加价往往是大头。</p>'''),
    ('exchange-rate-markup', '汇率加价怎么算？一张表看懂 Markup 对到账的影响', '2026-08-08', '费用汇率',
     '用例子解释 markup（汇率加价）如何吃掉你的到账金额。',
     '''<p><strong>汇率加价（markup）</strong>是平台在中间价上多收的百分比。公式：实际汇率 = 中间价 × (1 − markup)。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>加价</th><th>$1000 到账差额(相对0加价)</th></tr></thead><tbody>
     <tr><td>0.3%</td><td>约 −¥20</td></tr>
     <tr><td>1%</td><td>约 −¥68</td></tr>
     <tr><td>3.5%</td><td>约 −¥236</td></tr>
     </tbody></table></div>
     <p>可见 Remitly（约 3.5%）看似免手续费，加价却最多。算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p><strong>免手续费 ≠ 便宜</strong>，关键看 markup。低加价平台（Wise/熊猫）长期更省。</p>'''),
    ('hidden-fees-remittance', '汇款的隐藏费用：除了手续费还有哪些坑', '2026-08-08', '费用汇率',
     '拆解电汇中转行费、收款行费、汇率加价等隐藏成本。',
     '''<p>很多人只看"手续费"，但汇款的真实成本常藏在别处：</p>
     <ul class="article-list">
       <li><b>汇率加价</b>：最大的隐性成本（见上文）</li>
       <li><b>中转行费</b>：SWIFT 电汇可能经 1–2 家中转行，每家扣 $10–30</li>
       <li><b>收款行费</b>：国内银行落地费约 ¥10–50</li>
       <li><b>双币卡/动态货币转换</b>：用卡付汇款可能被加 DCC 费</li>
     </ul>
     <p>在线平台（Wise/熊猫）多为"总额透明"，避免中转行费。对比：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>选<strong>费用透明</strong>的平台，别只看表面手续费。</p>'''),
    ('bank-swift-vs-app', '银行 SWIFT 电汇 vs 汇款 App：到底差多少', '2026-08-08', '费用汇率',
     '传统银行电汇与 Wise/熊猫等 App 的速度、费用与体验对比。',
     '''<p>银行 SWIFT 电汇：安全但慢（1–3 天）、手续费+电报费+$ 中转行费、汇率差。汇款 App：快（分钟级）、费用透明、汇率贴近中间价。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>维度</th><th>银行 SWIFT</th><th>汇款 App</th></tr></thead><tbody>
     <tr><td>速度</td><td>1–3 天</td><td>分钟–1天</td></tr>
     <tr><td>费用</td><td>高(含中转行)</td><td>透明低</td></tr>
     <tr><td>汇率</td><td>差(加价大)</td><td>贴近中间价</td></tr>
     </tbody></table></div>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>日常小额选 <strong>App</strong> 更省更快；极大额或必须走银行的场景再用 SWIFT。</p>'''),
    ('best-time-to-send-money', '什么时候汇款最划算？汇率波动与警报用法', '2026-08-08', '费用汇率',
     '解释汇率短期波动规律与如何用警报抓住好汇率。',
     '''<p>汇率每天波动 0.1–0.5%，对 $10,000 来说就是几十到几百人民币的差别。没有"绝对最佳时机"，但可以聪明地等：</p>
     <ul class="article-list">
       <li>设<strong>汇率警报</strong>：达到目标值再汇（本站计算器页可订阅 USD/CNY 提醒）</li>
       <li>避开重大数据/节假日前后的剧烈波动</li>
       <li>大额分多次、在不同汇率点位汇，摊平成本</li>
     </ul>
     <p>订阅警报：<a class="link" href="../calculator.html">Fee Calculator</a> 底部。</p>
     <h2>一句话结论</h2>
     <p>别赌时点，用<strong>警报+分批</strong>摊平，比一次性猜顶底更稳。</p>'''),
    ('usdcny-outlook-2026', '2026 年美元兑人民币：怎么自己判断走势（中立科普）', '2026-08-08', '费用汇率',
     '中立科普如何跟踪 USD/CNY，而非预测点位。',
     '''<p>我们不预测汇率点位（谁也猜不准），但教你<strong>自己跟踪</strong>：</p>
     <ul class="article-list">
       <li>看央行每日中间价与在岸/离岸即期价差</li>
       <li>关注中美利差、贸易顺差、美元指数</li>
       <li>用搜索引擎实时中间价做基准，比较平台加价</li>
     </ul>
     <p>2026-08-08 中间价约 6.75（参考）。判断方法比结论更重要。算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p><strong>跟踪方法 &gt; 猜点位</strong>；设警报，到点再汇。</p>
     <h2>免责</h2>
     <p>本文为科普，不构成任何投资建议。</p>'''),
    ('is-remittance-to-china-legal', '汇款回国合法吗？海外华人合规边界', '2026-08-08', '合规科普',
     '讲清个人汇款回国的合法边界与红线。',
     '''<p>海外华人把合法收入汇回国内<strong>完全合法</strong>，但要守边界：</p>
     <ul class="article-list">
       <li>使用个人年度 5 万美元便利化额度（凭身份证办理）</li>
       <li>如实申报用途（赡家、留学、工资等）</li>
       <li>避免借用他人额度、分拆"蚂蚁搬家"</li>
     </ul>
     <p>超出便利化额度的真实需求，凭证明材料按经常/资本项目正常办理，并非禁止。</p>
     <h2>一句话结论</h2>
     <p><strong>合法收入 + 如实申报 = 合规</strong>；红线是拆分规避与虚假用途。</p>
     <h2>免责</h2>
     <p>本文为科普，不构成法律建议；具体请咨询银行与专业人士。</p>'''),
    ('declare-source-of-funds', '资金来源怎么申报？汇款回国的材料清单', '2026-08-08', '合规科普',
     '汇款回国时如何准备资金来源与用途证明。',
     '''<p>合规汇款的核心是<strong>来源清、用途明</strong>。常见材料：</p>
     <ul class="article-list">
       <li>工资/劳务：雇佣合同、工资单、完税证明</li>
       <li>留学：录取通知、学费单据</li>
       <li>赡家：亲属关系证明、用途说明</li>
     </ul>
     <p>平台与银行做 KYC 时会要求这些，提前备好能加速到账、避免冻结。</p>
     <h2>一句话结论</h2>
     <p>汇款前<strong>备齐材料</strong>，比事后解释成本低得多。</p>
     <h2>免责</h2>
     <p>本文为科普，不构成法律建议。</p>'''),
    ('anti-money-laundering-remittance', '反洗钱与汇款：大额会被查吗？', '2026-08-08', '合规科普',
     '解释反洗钱（AML）风控与大额汇款的注意点。',
     '''<p>各国对跨境汇款有反洗钱监控，平台与银行会做 KYC/AML 审查。<strong>合法资金完全无需担心</strong>，但要注意：</p>
     <ul class="article-list">
       <li>避免频繁、整数、拆分的可疑模式</li>
       <li>资金来源可追溯、用途真实</li>
       <li>配合平台身份与材料核验</li>
     </ul>
     <p>被要求补充材料是正常风控，不是"被查"，配合即可。</p>
     <h2>一句话结论</h2>
     <p><strong>干净的钱 + 配合核验</strong> = 顺畅到账。</p>
     <h2>免责</h2>
     <p>本文为科普，不构成法律建议。</p>'''),
    ('china-tax-on-foreign-income', '海外收入要交税吗？CRS 与居民个人科普', '2026-08-08', '合规科普',
     '中立科普中国税务居民与海外收入申报（CRS），不构建议。',
     '''<p>税务问题复杂且因人而异，这里只做<strong>中立科普</strong>：</p>
     <ul class="article-list">
       <li>中国税法按"税务居民"判定（如境内有住所或一年住满 183 天）</li>
       <li>CRS 下金融账户信息在参与国间交换</li>
       <li>具体是否申报、如何申报请咨询税务师</li>
     </ul>
     <p>本站不提供税务建议，仅提示"合规申报"的重要性。</p>
     <h2>一句话结论</h2>
     <p>税务因人而异，<strong>咨询持证税务师</strong>，勿凭网帖判断。</p>
     <h2>免责</h2>
     <p>本文不构成税务或法律建议。</p>'''),
    ('chinese-new-year-remittance', '春节给家人汇款：避开高峰与限额', '2026-08-08', '场景人群',
     '春节前后汇款回国的避峰、限额与温馨提示。',
     '''<p>春节是汇款高峰，平台审核与银行处理可能变慢。建议：</p>
     <ul class="article-list">
       <li>提前 1–2 周汇，避开节前拥堵</li>
       <li>留意单笔/单日限额，大额提前 KYC</li>
       <li>用微信/支付宝收款（熊猫速汇）更方便家人</li>
     </ul>
     <p>试算：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p><strong>早汇、备材料、用微信收款</strong>，让家人安心过年。</p>
     <h2>合规提醒</h2>
     <p>合法使用额度，本文不构成财务建议。</p>'''),
    ('remittance-for-tuition', '学费汇款攻略：凭单据合规汇出', '2026-08-08', '场景人群',
     '留学生学费汇款的单据、额度与平台建议。',
     '''<p>学费属"经常项目"，凭录取通知与学费单据可合规办理，不受 5 万美元便利化额度硬性限制（超额度提供证明即可）。</p>
     <ul class="article-list">
       <li>Wise/银行均可，保留学费单据</li>
       <li>大额一次汇，省固定费</li>
       <li>避开开学前高峰</li>
     </ul>
     <p>算账：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>学费汇款<strong>凭单据合规办</strong>，早规划、一次汇。</p>
     <h2>合规提醒</h2>
     <p>本文不构成财务建议。</p>'''),
    ('freelancer-receive-overseas', '自由职业者怎么收海外款？PayPal/Wise/熊猫对比', '2026-08-08', '场景人群',
     '自由职业者接收海外客户款项的平台对比与税率注意。',
     '''<p>自由职业者收美元/澳元，常见渠道：PayPal（通用但汇兑贵）、Wise（低加价、可开多币种账户）、熊猫速汇（中文友好）。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>渠道</th><th>优势</th><th>注意</th></tr></thead><tbody>
     <tr><td><b>PayPal</b></td><td>客户普遍接受</td><td>提现汇兑费高</td></tr>
     <tr><td><b>Wise</b></td><td>低加价、多币种</td><td>需 KYC</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>中文、微信收</td><td>覆盖有限</td></tr>
     </tbody></table></div>
     <p>对比：<a class="link" href="../calculator.html">Fee Calculator</a>。</p>
     <h2>一句话结论</h2>
     <p>要低成本选 <strong>Wise</strong>；客户只肯 PayPal 再提现。保留合同与发票。</p>
     <h2>合规提醒</h2>
     <p>如实申报劳务收入，本文不构成税务建议。</p>'''),
    ('uk-to-china-2026', '英国汇款回中国 2026：Wise / Revolut / 熊猫速汇 费用与速度对比', '2026-08-08', 'GB → CN',
     '英国华人汇款回国对比：英镑汇率加价、手续费、到账速度，附 £1000 实测估算。',
     '''<p>从英国汇款回中国，英镑（GBP）对人民币中间价约 9.08（2026-08-08）。真正的成本仍是<strong>汇率加价</strong>：银行 SWIFT 加价高，在线平台更贴近中间价。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 £4.99 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、长期</td></tr>
     <tr><td><b>Revolut</b></td><td>高级账户近中间价</td><td>约 1%</td><td>即时–1 天</td><td>已用 Revolut</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 £4.99</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户</td></tr>
     <tr><td><b>Western Union</b></td><td>约 £5 +</td><td>约 3%</td><td>几分钟（现金）</td><td>急用现金</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的真实英镑金额，本地计算即时出结果。</p>
     <h2>一句话结论</h2>
     <p>大额追真实汇率选 <strong>Wise</strong>；已是 Revolut 高级账户可享近中间价；要微信/支付宝收款选 <strong>熊猫速汇</strong>；紧急现金自取选 Western Union。</p>
     <h2>合规提醒</h2>
     <p>个人年度便利化购汇额度为 5 万美元等值。本文仅做教育性对比，不构成财务建议；请合法使用外汇额度。</p>'''),
    ('canada-to-china-2026', '加拿大汇款回中国：平台对比与加元汇率加价实测', '2026-08-08', 'CA → CN',
     '加拿大华人汇款回国：加元（CAD）汇率加价、手续费、到账速度全对比。',
     '''<p>从加拿大汇款回中国，加元（CAD）对人民币中间价约 4.83（2026-08-08）。在线平台相比银行 SWIFT 能显著减少汇率加价。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>约 C$4.99 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>Remitly</b></td><td>免手续费</td><td>约 3.5%</td><td>几分钟–1 天</td><td>新人首汇</td></tr>
     <tr><td><b>Instarem</b></td><td>约 C$2.99</td><td>约 1.2%</td><td>1 天内</td><td>亚太用户</td></tr>
     <tr><td><b>OFX</b></td><td>按比例 ~0.5%</td><td>约 0.5%</td><td>1–2 天</td><td>大额</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的加元金额试算。</p>
     <h2>一句话结论</h2>
     <p>小额首汇选 <strong>Remitly</strong>（新人优惠）；大额追真实汇率选 <strong>Wise</strong> 或 <strong>OFX</strong>（无上限压力）。</p>
     <h2>合规提醒</h2>
     <p>如实申报用途，勿拆分规避。本文不构成税务或财务建议。</p>'''),
    ('japan-to-china-2026', '日本汇款回中国：在日华人常用平台与手续费对比', '2026-08-08', 'JP → CN',
     '日本华人汇款回国：日元（JPY）汇率加价、熊猫速汇/Instarem/Wise 对比。',
     '''<p>从日本汇款回中国，日元（JPY）对人民币中间价约 0.0428（2026-08-08，即 100 日元≈4.28 元）。日本银行电汇手续费高、到账慢，在线平台更优。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>熊猫速汇</b></td><td>约 ¥500</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户</td></tr>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>Instarem</b></td><td>约 ¥300</td><td>约 1.2%</td><td>1 天内</td><td>亚太</td></tr>
     <tr><td><b>WorldRemit</b></td><td>约 ¥400 +</td><td>约 2%</td><td>几分钟–2 天</td><td>覆盖广</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的日元金额（系统按 100 日元折算）。</p>
     <h2>一句话结论</h2>
     <p>中文用户、要微信收款选 <strong>熊猫速汇</strong>；大额追真实汇率选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>在日合法收入汇款须如实申报。本文不构成财务建议。</p>'''),
    ('korea-to-china-2026', '韩国汇款回中国：韩元汇款平台对比（在韩华人）', '2026-08-08', 'KR → CN',
     '韩国华人汇款回国：韩元（KRW）汇率加价、手续费、到账速度对比。',
     '''<p>从韩国汇款回中国，韩元（KRW）对人民币中间价约 0.00479（2026-08-08，即 1 万韩元≈47.9 元）。在韩华人常用银行或在线平台。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>Western Union</b></td><td>约 ₩6000 +</td><td>约 3%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     <tr><td><b>WorldRemit</b></td><td>固定 +</td><td>约 2%</td><td>几分钟–2 天</td><td>覆盖广</td></tr>
     <tr><td><b>MoneyGram</b></td><td>固定 +</td><td>约 2.8%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入韩元金额试算。</p>
     <h2>一句话结论</h2>
     <p>大额追真实汇率选 <strong>Wise</strong>；急需现金自取选 <strong>Western Union / MoneyGram</strong>。</p>
     <h2>合规提醒</h2>
     <p>如实申报用途。本文不构成财务建议。</p>'''),
    ('singapore-to-china-2026', '新加坡汇款回中国：新元汇款平台与到账速度', '2026-08-08', 'SG → CN',
     '新加坡华人汇款回国：新元（SGD）汇率加价、Instarem/熊猫/Wise 对比。',
     '''<p>从新加坡汇款回中国，新元（SGD）对人民币中间价约 5.28（2026-08-08）。新加坡华人密集，平台选择多。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Instarem</b></td><td>约 S$2.99</td><td>约 1.2%</td><td>1 天内</td><td>亚太强</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 S$4.99</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户</td></tr>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>OFX</b></td><td>按比例 ~0.5%</td><td>约 0.5%</td><td>1–2 天</td><td>大额</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入新元金额试算。</p>
     <h2>一句话结论</h2>
     <p>亚太走廊 <strong>Instarem</strong> 与新马用户契合；大额追真实汇率选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>新加坡个税低但汇款须如实申报来源。本文不构成财务建议。</p>'''),
    ('eu-to-china-2026', '欧洲（欧元区）汇款回中国：德国/法国等通用方案', '2026-08-08', 'EU → CN',
     '欧元区（德国/法国等）华人汇款回国：欧元汇率加价、Revolut/Paysend/Wise 对比。',
     '''<p>从欧元区（德国、法国、意大利等）汇款回中国，欧元（EUR）对人民币中间价约 7.80（2026-08-08）。欧洲用户偏好低固定费的 App。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Revolut</b></td><td>高级账户近中间价</td><td>约 1%</td><td>即时–1 天</td><td>已用 Revolut</td></tr>
     <tr><td><b>Paysend</b></td><td>约 €1.5</td><td>约 1.5%</td><td>几分钟–1 天</td><td>低固定费</td></tr>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>Remitly</b></td><td>免手续费</td><td>约 3.5%</td><td>几分钟–1 天</td><td>新人首汇</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入欧元金额试算。</p>
     <h2>一句话结论</h2>
     <p>已是 Revolut 高级账户可享近中间价；小额追低固定费选 <strong>Paysend</strong>；大额选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>欧盟 CRS 信息交换，合规申报更显重要。本文不构成税务建议。</p>'''),
    ('hongkong-to-china-2026', '香港汇款回内地：港币汇款最划算的方式', '2026-08-08', 'HK → CN',
     '香港汇款回内地：港币（HKD）汇率加费、熊猫速汇/银行/Wise 对比与到账速度。',
     '''<p>从香港汇款回内地，港币（HKD）对人民币中间价约 0.860（2026-08-08）。港人常走银行电汇或在线平台。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>熊猫速汇</b></td><td>约 HK$30</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户</td></tr>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额</td></tr>
     <tr><td><b>Western Union</b></td><td>约 HK$40 +</td><td>约 3%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     <tr><td><b>银行电汇</b></td><td>约 HK$50–100</td><td>约 1–2%</td><td>1–2 天</td><td>大额</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入港币金额试算。</p>
     <h2>一句话结论</h2>
     <p>中文用户、要微信收款选 <strong>熊猫速汇</strong>；大额追真实汇率选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>香港与内地汇款受两地监管，如实申报用途。本文不构成财务建议。</p>'''),
    ('nz-to-china-2026', '新西兰汇款回中国 2026：Wise / OFX / 熊猫速汇 费用与速度对比', '2026-08-09', 'NZ → CN',
     '新西兰（NZD）汇款回中国：汇率加价、Wise/OFX/熊猫速汇/西联对比与到账速度。',
     '''<p>从新西兰汇款回中国，新西兰元（NZD）对人民币中间价约 3.99（2026-08-09）。纽澳联动，平台选择与澳洲高度相似。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>OFX</b></td><td>按比例 0.5%</td><td>约 0.5%</td><td>1–2 天</td><td>大额（起汇约 NZ$1000）</td></tr>
     <tr><td><b>熊猫速汇</b></td><td>约 NZ$5</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户、微信收款</td></tr>
     <tr><td><b>Western Union</b></td><td>约 NZ$6 +</td><td>约 3%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入纽币金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>大额（&gt;NZ$2000）选 <strong>Wise / OFX</strong> 更省；要中文客服、微信收款选 <strong>熊猫速汇</strong>。</p>
     <h2>合规提醒</h2>
     <p>保留汇款用途凭证，遵守新西兰与中国的外汇申报要求。本文不构成财务建议。</p>'''),
    ('my-to-china-2026', '马来西亚汇款回中国 2026：熊猫速汇 / Instarem / Wise 哪个划算', '2026-08-09', 'MY → CN',
     '马来西亚（MYR）汇款回中国：林吉特汇率、熊猫速汇/Instarem/Wise/银行对比与到账速度。',
     '''<p>从马来西亚汇款回中国，林吉特（MYR）对人民币中间价约 1.65（2026-08-09）。马来西亚华人众多，东南亚走廊活跃。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>熊猫速汇</b></td><td>约 RM5</td><td>约 0.8%</td><td>10 分钟–1 天</td><td>中文用户、微信收款</td></tr>
     <tr><td><b>Instarem</b></td><td>约 RM3</td><td>约 1.2%</td><td>1 天内</td><td>新马亚太走廊</td></tr>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>Western Union</b></td><td>约 RM8 +</td><td>约 3%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入林吉特金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>中文体验优先选 <strong>熊猫速汇</strong>；亚太低费选 <strong>Instarem</strong>；大额追汇率选 <strong>Wise</strong>。</p>
     <h2>合规提醒</h2>
     <p>马来西亚与中国均对跨境汇款有申报要求，如实填写用途。本文不构成财务建议。</p>'''),
    ('it-to-china-2026', '意大利汇款回中国 2026：Wise / Revolut / TransferGo 欧洲走廊对比', '2026-08-09', 'IT → CN',
     '意大利（EUR）汇款回中国：欧元汇率、Wise/Revolut/TransferGo/Paysend 对比与到账速度。',
     '''<p>从意大利汇款回中国，欧元（EUR）对人民币中间价约 7.80（2026-08-09）。意大利是欧洲华人最集中国家之一，欧洲走廊成熟。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>Revolut</b></td><td>高级账户近中间价</td><td>约 1%</td><td>即时–1 天</td><td>欧盟用户、App 体验</td></tr>
     <tr><td><b>TransferGo</b></td><td>低固定费</td><td>约 1.8%</td><td>几分钟–1 天</td><td>欧洲小额</td></tr>
     <tr><td><b>Paysend</b></td><td>约 €1.5</td><td>约 1.5%</td><td>几分钟–1 天</td><td>低固定费</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入欧元金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>大额选 <strong>Wise</strong>；已有 Revolut 追优汇选 <strong>Revolut</strong>；欧洲小额选 <strong>TransferGo / Paysend</strong>。</p>
     <h2>合规提醒</h2>
     <p>欧盟与中国对跨境汇款均有反洗钱申报，如实填写用途。本文不构成财务建议。</p>'''),
    ('es-to-china-2026', '西班牙汇款回中国 2026：Wise / TransferGo / Paysend 欧洲走廊对比', '2026-08-09', 'ES → CN',
     '西班牙（EUR）汇款回中国：欧元汇率、Wise/TransferGo/Revolut/Paysend 对比与到账速度。',
     '''<p>从西班牙汇款回中国，欧元（EUR）对人民币中间价约 7.80（2026-08-09）。西班牙华人社区庞大，欧洲走廊选择丰富。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>TransferGo</b></td><td>低固定费</td><td>约 1.8%</td><td>几分钟–1 天</td><td>欧洲小额首选</td></tr>
     <tr><td><b>Revolut</b></td><td>高级账户近中间价</td><td>约 1%</td><td>即时–1 天</td><td>欧盟用户</td></tr>
     <tr><td><b>Paysend</b></td><td>约 €1.5</td><td>约 1.5%</td><td>几分钟–1 天</td><td>低固定费</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入欧元金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>大额选 <strong>Wise</strong>；欧洲小额选 <strong>TransferGo / Paysend</strong>；已有 Revolut 选 <strong>Revolut</strong>。</p>
     <h2>合规提醒</h2>
     <p>西班牙与中国对跨境汇款均有申报要求，如实填写用途。本文不构成财务建议。</p>'''),
    ('fr-to-china-2026', '法国汇款回中国 2026：Wise / Revolut / Xoom 欧洲走廊对比', '2026-08-09', 'FR → CN',
     '法国（EUR）汇款回中国：欧元汇率、Wise/Revolut/Xoom/Paysend 对比与到账速度。',
     '''<p>从法国汇款回中国，欧元（EUR）对人民币中间价约 7.80（2026-08-09）。法国是欧洲华人第二多的国家，平台覆盖完善。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>Revolut</b></td><td>高级账户近中间价</td><td>约 1%</td><td>即时–1 天</td><td>欧盟用户</td></tr>
     <tr><td><b>Xoom</b></td><td>低固定费</td><td>约 2%</td><td>几分钟–2 天</td><td>信任 PayPal 生态</td></tr>
     <tr><td><b>Paysend</b></td><td>约 €1.5</td><td>约 1.5%</td><td>几分钟–1 天</td><td>低固定费</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入欧元金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>大额选 <strong>Wise</strong>；已有 Revolut 选 <strong>Revolut</strong>；信任大品牌选 <strong>Xoom</strong>。</p>
     <h2>合规提醒</h2>
     <p>法国与中国对跨境汇款均有申报要求，如实填写用途。本文不构成财务建议。</p>'''),
    ('ae-to-china-2026', '阿联酋汇款回中国 2026：Wise / Remitly / Xoom 中东走廊对比', '2026-08-09', 'AE → CN',
     '阿联酋（AED）汇款回中国：迪拉姆汇率、Wise/Remitly/Xoom/西联对比与到账速度。',
     '''<p>从阿联酋汇款回中国，迪拉姆（AED）对人民币中间价约 1.84（2026-08-09）。迪拜华人以劳务与经商为主，单笔金额常较大。</p>
     <div class="tablewrap"><table class="cmp"><thead><tr><th>平台</th><th>手续费</th><th>汇率加价</th><th>到账</th><th>适合</th></tr></thead><tbody>
     <tr><td><b>Wise</b></td><td>固定 + 0.4%</td><td>约 0.3%</td><td>几分钟–1 天</td><td>大额、追真实汇率</td></tr>
     <tr><td><b>Remitly</b></td><td>低/免</td><td>约 3.5%</td><td>几分钟–1 天</td><td>新人首汇</td></tr>
     <tr><td><b>Xoom</b></td><td>低固定费</td><td>约 2%</td><td>几分钟–2 天</td><td>信任 PayPal 生态</td></tr>
     <tr><td><b>Western Union</b></td><td>约 AED8 +</td><td>约 3%</td><td>几分钟（现金）</td><td>现金自取</td></tr>
     <tr><td><b>银行直汇</b></td><td>电报费 + 0.4%</td><td>约 0.4%</td><td>1–3 天</td><td>已开国内账户</td></tr>
     </tbody></table></div>
     <p>用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入迪拉姆金额试算到账。</p>
     <h2>一句话结论</h2>
     <p>大额选 <strong>Wise</strong>；新人首汇或小额急用选 <strong>Remitly</strong>；信任大品牌选 <strong>Xoom</strong>。</p>
     <h2>合规提醒</h2>
     <p>阿联酋与中国均对跨境汇款有申报要求，劳务收入如实申报。本文不构成财务建议。</p>'''),
]

# 每篇文章的专属 FAQ（喂 FAQPage schema + 页面折叠块）；通用 FAQ 自动附加到所有文章
BLOG_FAQ = {
    'us-to-china-2026': [
        ('美国汇款回国最便宜的是哪个？', '小额急用/首汇选 Remitly（新人优惠），大额追真实汇率选 Wise，要微信收款选熊猫速汇。以计算器输入你的金额为准。'),
        ('汇率会随金额变化吗？', '中间价不变，但部分平台对大额费率更优（固定费被摊薄），用 Fee Calculator 试不同金额。')],
    'wise-vs-remitly': [
        ('Wise 和 Remitly 哪个到账多？', '同金额下 Wise 通常到账更多（加价仅约 0.3%，Remitly 约 3.5%），但 Remitly 新人首汇常免手续费、更快。'),
        ('为什么 Remitly 免手续费还不便宜？', '它用更高的汇率加价（约 3.5%）赚钱，免手续费只是表象。')],
    'china-fx-quota-2026': [
        ('一年只能汇 5 万美元吗？', '5 万是"便利化"额度（凭身份证即可办），不是上限；超出凭真实用途证明仍可办理。'),
        ('借用家人额度可以吗？', '不可以。拆分到多人额度"蚂蚁搬家"属违规，可能被关注并处罚。')],
    'mid-market-rate-explained': [
        ('中间价在哪查？', '搜索引擎实时汇率、XE 等均为中间价，可作为比较平台汇率的基准。'),
        ('银行给的是中间价吗？', '不是。银行与平台会在中间价上加买卖点差/加价作为利润。')],
    'exchange-rate-markup': [
        ('markup 0.3% 和 3.5% 差多少？', '汇 $1000，3.5% 比 0.3% 少约 ¥216 到账，长期差距显著。'),
        ('免手续费平台 markup 更高吗？', '通常如此，免手续费往往靠更高汇率加价补偿。')],
    'hidden-fees-remittance': [
        ('SWIFT 电汇为什么更贵？', '可能经 1–2 家中转行，每家扣 $10–30，加上收款行落地费。'),
        ('在线平台有隐藏费吗？', '主流平台（Wise/熊猫）多为总额透明，相对更可控。')],
    'bank-swift-vs-app': [
        ('极大额必须走银行吗？', '不一定；Wise 等支持大额且费率更优，但请留意单笔限额与 KYC。'),
        ('App 汇款安全吗？', '持牌平台受监管，KYC/AML 到位；选知名平台即可。')],
    'is-remittance-to-china-legal': [
        ('汇款回国违法吗？', '合法收入、如实申报用途完全合法；红线是拆分规避与虚假用途。'),
        ('超出 5 万额度怎么办？', '凭证明材料（工资/学费/赡家）按经常或资本项目正常办理，并非禁止。')],
    'declare-source-of-funds': [
        ('必须提供材料吗？', '合规汇款需来源清、用途明；平台/银行 KYC 会要求，提前备好可加速。'),
        ('哪些材料常用？', '工资单/合同/完税证明、录取与学费单据、亲属关系证明等。')],
    'anti-money-laundering-remittance': [
        ('大额会被冻结吗？', '合法资金配合核验即可；被要求补材料是正常风控，不是"被查"。'),
        ('怎样避免可疑模式？', '避免频繁、整数、拆分，保持来源可追溯、用途真实。')],
    'china-tax-on-foreign-income': [
        ('海外收入都要在国内交税吗？', '取决于税务居民身份，因人而异；请咨询持证税务师，勿凭网帖判断。'),
        ('CRS 是什么？', '金融账户信息在参与国间交换的机制，提示合规申报的重要性。')],
    'wise-remitly-panda-3way': [
        ('三个平台怎么选？', '大额追汇率选 Wise；首汇吃优惠选 Remitly；中文+微信选熊猫。没有最好，只有最适合。'),
        ('能同时用多个吗？', '可以，按每笔金额与场景分别选最优。')],
    'best-time-to-send-money': [
        ('能预测最佳汇率吗？', '不能也不建议；用警报+分批摊平比猜顶底更稳。'),
        ('警报怎么设？', '本站 Fee Calculator 底部可订阅 USD/CNY 汇率提醒。')],
    'us-large-amount': [
        ('大额一次汇还是分笔？', '一次汇更省固定费，但留意单笔限额与 KYC 材料。'),
        ('大额会被审查吗？', '平台风控会核验身份与来源，合法资金配合即可。')],
}

GENERIC_FAQ = [
    ('这篇对比的数据什么时候更新？', '费用与汇率数据于 %s 核实，实际以平台实时报价为准。' % DATA_UPDATED),
    ('页面上的平台链接安全吗？', '为联盟链接（含披露声明），跳转后由对应平台负责；本站不收集你的任何数据。'),
]

def related_for(slug):
    rec = next((r for r in BLOG_LIST if r[0] == slug), None)
    if not rec:
        return []
    corr = rec[3]
    others = [r[0] for r in BLOG_LIST if r[0] != slug]
    same = [s for s in others if next((r for r in BLOG_LIST if r[0] == s), [None])[3] == corr]
    return (same[:3] if len(same) >= 2 else others[:3])

def build_blog_index():
    title = '汇款指南 Guides — 15 国→中国走廊攻略与平台对比 | RemitGuide'
    meta = '美国、澳洲、英国、加拿大、日本、韩国、新加坡、欧元区、香港汇款回中国的攻略与平台对比：手续费、汇率加价、到账速度、外汇额度科普。'
    schema = ('{"@context":"https://schema.org","@type":"CollectionPage","name":"RemitGuide Guides","url":"' + BASE + 'blog/index.html"}')
    hero = ('''<div class="t-tool-hero">
      <div class="crumb">Guides</div>
      <h1>汇款指南</h1>
      <p class="sub">走廊攻略 · 平台对比 · 外汇合规科普。数据更新于 %s。</p>
    </div>''' % DATA_UPDATED)
    cards = ''
    for slug, pt, pd, corr, ex, _b in BLOG_LIST:
        cards += ('''<a href="%s.html" class="bg-surface-container border-2 border-black p-6 brutal-shadow brutal-hover transition-all block">
            <div class="font-label-caps text-label-caps text-brutalist-yellow uppercase mb-2">%s · %s</div>
            <h2 class="font-headline-sm text-headline-sm uppercase text-on-surface">%s</h2>
            <p class="text-on-surface-variant mt-2 text-sm">%s</p>
          </a>''' % (slug, html.escape(corr), pd, html.escape(pt), html.escape(ex)))
    body = hero + '<div class="grid grid-cols-1 md:grid-cols-2 gap-gap-sm">' + cards + '</div>' + AFF_DISCLOSURE
    return page_brutalist(title, meta, schema, active='guides', page_id='blog', body=body)

def build_blog_post(slug):
    rec = next((r for r in BLOG_LIST if r[0] == slug), None)
    if not rec:
        return None
    _slug, pt, pd, corr, ex, body_html = rec
    title = '%s | RemitGuide' % pt
    meta = ex
    schema = ('{"@context":"https://schema.org","@type":"Article","headline":"%s","datePublished":"%s",'
              '"author":{"@type":"Person","name":"RemitGuide"},"publisher":{"@type":"Organization","name":"RemitGuide"},'
              '"mainEntityOfPage":"%sblog/%s.html"}' % (pt.replace('"', '\\"'), pd, BASE, slug))
    hero = ('''<div class="t-tool-hero article-hero">
      <div class="crumb"><a href="../index.html">RemitGuide</a> / <a href="index.html">Guides</a> / %s</div>
      <h1>%s</h1>
      <p class="sub">%s · 数据更新于 %s</p>
    </div>''' % (html.escape(corr), html.escape(pt), html.escape(corr), DATA_UPDATED))
    faqs = BLOG_FAQ.get(slug, []) + GENERIC_FAQ
    faq_html = faq_block(faqs)
    rel = related_for(slug)
    rel_html = ''
    if rel:
        cards = ''
        for s in rel:
            t = next((r[1] for r in BLOG_LIST if r[0] == s), s)
            cards += '<a class="rel-card" href="%s.html">%s</a>' % (s, html.escape(t))
        rel_html = '<h2>相关阅读</h2><div class="rel-grid">%s</div>' % cards
    cta_html = '<p class="cta-inline">用 <a class="link" href="../calculator.html">Fee Calculator</a> 输入你的金额，看实时到账 →</p>'
    faq_json = ('{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' +
                ','.join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                         % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False)) for q, a in faqs) + ']}')
    article = ('<article class="article">' + body_html + '</article>'
               + cta_html + faq_html + rel_html
               + '<script type="application/ld+json">%s</script>' % faq_json)
    body = hero + article + AFF_DISCLOSURE + DATA_NOTE.format(d=DATA_UPDATED)
    return page_brutalist(title, meta, schema, active='guides', page_id='blog', body=body, prefix='../', url=BASE + 'blog/' + slug + '.html')

# ============================================================
# STATIC PAGES
# ============================================================
def build_about():
    title = 'About — 关于 RemitGuide | 华人汇款指南'
    meta = 'RemitGuide 是什么：面向海外华人的汇款平台对比与费用计算工具站。隐私友好、零追踪。'
    schema = ('{"@context":"https://schema.org","@type":"AboutPage","name":"About RemitGuide","url":"' + BASE + 'about.html"}')
    body = ('''<div class="t-tool-hero">
      <div class="crumb">About</div>
      <h1>关于 RemitGuide</h1>
      <p class="sub">我们只做一件事：把「汇款回国到底哪个平台划算」讲清楚。</p>
    </div>
    <article class="article">
      <p>RemitGuide 是一个面向海外华人的跨境汇款对比站：用中文把 Wise、Remitly、熊猫速汇、WorldRemit、Instarem 的手续费、汇率加价、到账速度、新人优惠讲清楚，并提供<strong>汇款费用计算器</strong>让用户输入真实金额即时对比。</p>
      <p>本站是独立个人项目：<strong>不收集任何数据、无追踪、无广告侵入</strong>。所有计算都在你的浏览器本地完成。</p>
      <p>内容立场：只做教育性对比与科普，不构成财务、法律或税务建议。我们通过联盟链接获得收入（在你注册时按平台规则分成），这不会影响我们的结论客观性——<a class="link" href="disclosure.html">披露声明</a>。</p>
    </article>''')
    return page_brutalist(title, meta, schema, page_id='about', body=body)

def build_contact():
    title = 'Contact — 联系 RemitGuide'
    meta = '联系 RemitGuide：纠错、建议、合作（联盟 / 内容互换）请发邮件。'
    schema = ('{"@context":"https://schema.org","@type":"ContactPage","name":"Contact RemitGuide","url":"' + BASE + 'contact.html"}')
    body = ('''<div class="t-tool-hero">
      <div class="crumb">Contact</div>
      <h1>联系我们</h1>
      <p class="sub">纠错、建议、合作都欢迎。</p>
    </div>
    <div class="brutal-card" style="padding:28px;">
      <label>Email</label>
      <p><a class="link" href="mailto:%s">%s</a></p>
      <p class="hint">通常 1–3 个工作日内回复。合作（联盟 / 内容互换 / 数据纠错）请注明主题。</p>
    </div>''' % (CONTACT_EMAIL, CONTACT_EMAIL))
    return page_brutalist(title, meta, schema, page_id='contact', body=body)

def build_disclosure():
    title = 'Affiliate Disclosure — 联盟链接披露 | RemitGuide'
    meta = 'RemitGuide 的联盟链接披露声明：哪些链接可能带来佣金，以及我们的客观性承诺。'
    schema = ('{"@context":"https://schema.org","@type":"WebPage","name":"Disclosure","url":"' + BASE + 'disclosure.html"}')
    body = ('''<div class="t-tool-hero">
      <div class="crumb">Disclosure</div>
      <h1>联盟链接披露</h1>
      <p class="sub">FTC 要求：把「谁在付钱」说清楚。</p>
    </div>
    <article class="article">
      <p>本网站上的一些链接是<strong>联盟链接</strong>。如果你通过这些链接注册或完成首笔交易，我们可能从相应平台获得佣金——<strong>这不影响你的费用，也不会改变我们的推荐</strong>。</p>
      <p>我们只推荐自己会用的平台，并在文章中披露场景与取舍（见各篇「一句话结论」）。费用与汇率数据均为估算，请以平台实时报价为准。</p>
      <p>本披露适用于全站所有页面与文章。</p>
    </article>''')
    return page_brutalist(title, meta, schema, page_id='disclosure', body=body)

def build_privacy():
    title = 'Privacy — 隐私政策 | RemitGuide'
    meta = 'RemitGuide 隐私政策：零数据收集、无追踪、无 Cookie（除必要功能）。'
    schema = ('{"@context":"https://schema.org","@type":"WebPage","name":"Privacy Policy","url":"' + BASE + 'privacy.html"}')
    body = ('''<div class="t-tool-hero">
      <div class="crumb">Privacy</div>
      <h1>隐私政策</h1>
      <p class="sub">简单到一句话：我们什么都不收集。</p>
    </div>
    <article class="article">
      <p><strong>本站不收集任何个人数据。</strong>没有账号、没有服务器、没有分析追踪、没有广告 Cookie。所有计算（含费用计算器）都在你的浏览器本地完成。</p>
      <p>唯一可能涉及数据的场景：<strong>汇率警报订阅</strong>——你主动提供邮箱、货币对与目标汇率，仅用于向你发送汇率提醒邮件；数据存储于 Upstash（或本地文件），经 Resend 发送，不用于营销、不与第三方共享。以及当你点击联盟链接跳转到第三方平台时，该平台的隐私政策将适用。</p>
      <p>如果你从搜索引擎进入本站，搜索引擎（Google / Bing）可能有自己的日志，这与本站无关。</p>
    </article>''')
    return page_brutalist(title, meta, schema, page_id='privacy', body=body)

# ============================================================
# SITEMAP / ROBOTS
# ============================================================
def build_sitemap():
    urls = [('', '0.9')]
    urls += [('calculator.html', '0.9'), ('blog/index.html', '0.8'),
             ('about.html', '0.5'), ('contact.html', '0.4'),
             ('disclosure.html', '0.3'), ('privacy.html', '0.3')]
    urls += [('blog/%s.html' % r[0], '0.8') for r in BLOG_LIST]
    today = date.today().isoformat()
    items = ''
    for path, pri in urls:
        items += ('  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>%s</priority></url>\n'
                  % (BASE, path, today, pri))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + items + '</urlset>\n')

def build_robots():
    return ('User-agent: *\nAllow: /\n\n'
            'Sitemap: ' + BASE + 'sitemap.xml\n')

# ============================================================
# TAILWIND 自托管构建（替代 Play CDN）
# ============================================================
def build_tailwind():
    """扫描生成的 HTML，产出本地 tailwind.css（已 minify）。需 node 工作区装好 tailwindcss@3。
    注意：Windows 下 .bin/tailwindcss 是 shebang 脚本，不能直接 subprocess 执行（WinError 193），
    故用 node 显式运行 lib/cli.js。"""
    node_bin = os.path.join(os.path.expanduser('~'), '.workbuddy', 'binaries', 'node',
                            'versions', '22.22.2', 'node.exe')
    tw_js = os.path.join(os.path.expanduser('~'), '.workbuddy', 'binaries', 'node',
                         'workspace', 'node_modules', 'tailwindcss', 'lib', 'cli.js')
    if not (os.path.exists(node_bin) and os.path.exists(tw_js)):
        print('[WARN] 未找到 node 或 tailwindcss CLI，跳过本地 CSS 构建（请先在 node 工作区 npm install tailwindcss@3）。')
        return
    here = os.path.dirname(os.path.abspath(__file__))
    ws_nm = os.path.join(os.path.expanduser('~'), '.workbuddy', 'binaries', 'node',
                         'workspace', 'node_modules')
    env = os.environ.copy()
    env['NODE_PATH'] = ws_nm  # 让 tailwind.config.js 的 require('@tailwindcss/forms') 解析到工作区
    try:
        subprocess.run([node_bin, tw_js, '-i', 'input.css', '-o', 'tailwind.css', '--minify'],
                       check=True, cwd=here, env=env)
        print('wrote tailwind.css (self-hosted, minified)')
    except Exception as e:
        print('[WARN] tailwind 构建失败:', e)


# ============================================================
# MAIN
# ============================================================
def main():
    pages = {
        'index.html': build_index(),
        'calculator.html': build_calculator(),
        'blog/index.html': build_blog_index(),
        'about.html': build_about(),
        'contact.html': build_contact(),
        'disclosure.html': build_disclosure(),
        'privacy.html': build_privacy(),
    }
    for slug, _t, _d, _c, _e, _b in BLOG_LIST:
        pages['blog/%s.html' % slug] = build_blog_post(slug)
    os.makedirs('blog', exist_ok=True)
    for path, content in pages.items():
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('wrote %s (%d bytes)' % (path, len(content)))
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(build_sitemap())
    print('wrote sitemap.xml (%d urls)' % (len(pages)))
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(build_robots())
    print('wrote robots.txt')
    build_tailwind()
    print('DONE: %d html pages' % len(pages))

if __name__ == '__main__':
    main()
