// RemitGuide — 汇率警报定时检查 (Serverless Cron)
// 由平台定时任务触发（如 Vercel Cron 访问 /api/cron），遍历订阅、拉实时汇率、达标即发邮件。
// 自包含，无第三方依赖。与 subscribe.js 共享同一套环境变量与存储/邮件逻辑。
//
// 环境变量：
//   UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN  —— 存储（必填）
//   RESEND_API_KEY + FROM_EMAIL                        —— 发件（必填，否则只打印不发送）
//   RATE_API（可选，默认 https://api.frankfurter.app/latest）
//   ALERT_SECRET（可选）                               —— 设了则要求请求带 ?secret=xxx 才执行
//
// Vercel 触发：vercel.json { "crons": [{ "path": "/api/cron", "schedule": "0 1 * * *" }] }
//   （免费版最低每日一次；如需鉴权，把 path 写成 "/api/cron?secret=你的密钥"）

const PAIRS = ["USDCNY","AUDCNY","GBPCNY","CADCNY","JPYCNY","KRWCNY","SGDCNY","EURCNY","HKDCNY"];
const UNIT = { JPY: 100, KRW: 100 };
const SUBS_KEY = "remitguide:subscribers";
const RATE_API = process.env.RATE_API || "https://api.frankfurter.app/latest";

function useUpstash(){ return !!(process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN); }
async function upstash(method, path, body){
  const base = process.env.UPSTASH_REDIS_REST_URL.replace(/\/$/, "");
  const opts = { method, headers: { Authorization: `Bearer ${process.env.UPSTASH_REDIS_REST_TOKEN}` } };
  if (body !== undefined){ opts.body = JSON.stringify(body); opts.headers["Content-Type"] = "application/json"; }
  const r = await fetch(`${base}/${path}`, opts);
  return await r.json();
}
async function loadSubs(){
  if (useUpstash()){
    try { const res = await upstash("GET", `get/${SUBS_KEY}`); return res.result ? JSON.parse(res.result) : []; }
    catch(e){ console.error("upstash load fail", e); return []; }
  }
  try { return JSON.parse(require("fs").readFileSync("data/subscribers.json", "utf8")); } catch(e){ return []; }
}
async function saveSubs(subs){
  if (useUpstash()){ await upstash("POST", `set/${SUBS_KEY}`, subs); return; }
  require("fs").writeFileSync("data/subscribers.json", JSON.stringify(subs, null, 2));
}
async function sendEmail(to, subject, html){
  const key = process.env.RESEND_API_KEY;
  if (!key){ console.log("[DRY-RUN] would email", to, subject); return true; }
  const r = await fetch("https://api.resend.com/emails", {
    method:"POST",
    headers:{ Authorization:`Bearer ${key}`, "Content-Type":"application/json" },
    body: JSON.stringify({ from: process.env.FROM_EMAIL || "alerts@remitguide.xxx", to:[to], subject, html }),
  });
  if (!r.ok){ console.error("send fail", await r.text()); return false; }
  return true;
}
async function getRatePerUnit(pair){
  const base = pair.slice(0, 3), quote = pair.slice(3);
  const r = await fetch(`${RATE_API}?from=${base}&to=${quote}`, { headers:{ Accept:"application/json" } });
  const d = await r.json();
  if (!d.rates || d.rates[quote] == null) throw new Error("汇率源未返回 " + quote);
  return parseFloat(d.rates[quote]);
}

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  // 鉴权
  const secret = process.env.ALERT_SECRET;
  if (secret){
    const url = new URL(req.url, "http://localhost");
    if (url.searchParams.get("secret") !== secret){ res.statusCode = 401; res.end(JSON.stringify({ error: "unauthorized" })); return; }
  }
  const subs = await loadSubs();
  const pending = subs.filter(s => !s.notified);
  let sent = 0;
  for (const s of pending){
    try {
      const rate = await getRatePerUnit(s.pair);
      const value = rate * (UNIT[s.pair.slice(0, 3)] || 1);
      const met = s.cond === "ge" ? value >= s.target : value <= s.target;
      if (met){
        const condTxt = s.cond === "ge" ? "达到或超过" : "跌破";
        const html = `<div style="font-family:Inter,Arial;max-width:480px;margin:0 auto;border:3px solid #100e05;padding:20px;color:#100e05;">`
          + `<h2>RemitGuide 汇率警报</h2>`
          + `<p>你订阅的 <b>${s.pair}</b> 已${condTxt}目标 <b>${s.target}</b>。</p>`
          + `<p style="font-size:22px;font-weight:700;margin:14px 0;">当前：<b>${value.toFixed(4)}</b></p>`
          + `<p style="font-size:13px;color:#6b6256;">仅作信息提醒，不构成投资建议。</p></div>`;
        if (await sendEmail(s.email, `RemitGuide 汇率警报：${s.pair} 已触发`, html)){ s.notified = true; sent++; }
      }
    } catch(e){ console.error("check fail", s.pair, e); }
  }
  await saveSubs(subs);
  res.statusCode = 200;
  res.end(JSON.stringify({ checked: pending.length, sent }));
};

// Cloudflare Pages Functions 适配器（如用 CF Cron Triggers，取消注释）：
// export async function onRequestGet({ request, env }) {
//   for (const k in env) process.env[k] = env[k];
//   return module.exports(request, { setHeader(){}, set statusCode(v){}, get statusCode(){return 0}, end:(b)=>new Response(b,{headers:{'Content-Type':'application/json'}}) });
// }
