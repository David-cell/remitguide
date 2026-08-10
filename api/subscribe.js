// RemitGuide — 汇率警报订阅接口 (Serverless: Vercel / Cloudflare Pages Functions)
// 前端 POST /api/subscribe 即触发。自包含，无第三方依赖（仅用 Node 内置 fetch / fs）。
//
// 环境变量：
//   UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN  —— 生产存储（必填；否则回退本地 data/subscribers.json，仅开发可用）
//   RESEND_API_KEY + FROM_EMAIL                        —— 发送确认/提醒邮件（可选，缺则跳过发送，仅记录）
//
// 部署差异：
//   Vercel / Cloudflare Pages Functions：本文件放 api/subscribe.js，路径即 /api/subscribe。
//   Netlify：放 netlify/functions/subscribe.js，并在 public/_redirects 加  /api/subscribe  /.netlify/functions/subscribe  200
//   Cloudflare 需把 process.env 改为从 context.env 读取（见文件末注释）。

const PAIRS = ["USDCNY","AUDCNY","GBPCNY","CADCNY","JPYCNY","KRWCNY","SGDCNY","EURCNY","HKDCNY"];
const SUBS_KEY = "remitguide:subscribers";

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

function validate(b){
  if (!b || !b.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email)) return "邮箱无效";
  if (!PAIRS.includes(b.pair)) return "不支持的货币对";
  if (!["ge","le"].includes(b.cond)) return "cond 必须为 ge/le";
  if (!(parseFloat(b.target) > 0)) return "目标汇率必须大于 0";
  return null;
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

function readBody(req){
  return new Promise((resolve, reject)=>{
    let data=""; req.on("data", c=> data+=c); req.on("end", ()=>{ try{ resolve(data?JSON.parse(data):{}); }catch(e){ reject(e); } });
  });
}

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  if (req.method !== "POST"){ res.statusCode = 405; res.end(JSON.stringify({ error: "仅支持 POST" })); return; }
  let body;
  try { body = await readBody(req); } catch(e){ res.statusCode = 400; res.end(JSON.stringify({ error: "请求体解析失败" })); return; }
  const err = validate(body);
  if (err){ res.statusCode = 400; res.end(JSON.stringify({ error: err })); return; }

  const subs = await loadSubs();
  const email = String(body.email).trim().toLowerCase();
  const pair = String(body.pair).toUpperCase();
  const cond = body.cond || "ge";
  const target = parseFloat(body.target);
  let found = false;
  for (const s of subs){
    if (s.email === email && s.pair === pair){ s.cond = cond; s.target = target; s.notified = false; s.updated = new Date().toISOString(); found = true; break; }
  }
  if (!found){ subs.push({ email, pair, cond, target, notified:false, created:new Date().toISOString(), updated:new Date().toISOString() }); }
  await saveSubs(subs);

  if (process.env.RESEND_API_KEY){
    await sendEmail(email, "RemitGuide 汇率警报已订阅",
      `<div style="font-family:Inter,Arial;border:3px solid #100e05;padding:20px;color:#100e05;"><h2>已订阅汇率警报</h2><p>${pair} ${cond} ${target}。达到目标时会邮件提醒你。</p></div>`);
  }
  res.statusCode = 200;
  res.end(JSON.stringify({ ok:true, pair, cond, target }));
};

// Cloudflare Pages Functions 适配器（如用 CF，取消注释并替换上面的 module.exports）：
// export function onRequestPost({ request, env }) {
//   // 把 env 注入 process.env
//   for (const k in env) process.env[k] = env[k];
//   return module.exports(request, { setHeader(){}, get statusCode(){return 0}, set statusCode(v){}, end:(b)=>new Response(b,{headers:{'Content-Type':'application/json'}}) });
// }
