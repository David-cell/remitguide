# -*- coding: utf-8 -*-
"""
RemitGuide — 汇率警报引擎（可本地运行，也可作为 Serverless 后端核心）
=================================================================
功能：
  - 订阅：保存 (email, pair, cond, target) 到存储（Upstash Redis REST 或本地 JSON）。
  - 检查：拉取实时汇率（frankfurter.app，免费无需 key），与每个订阅者的目标比较。
  - 提醒：达到目标时通过 Resend 发送邮件（无 key 时 dry-run 打印，不真正发送）。

存储（按环境变量自动选择）：
  - 设了 UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN → 用 Upstash（生产，Serverless 友好）。
  - 否则 → 本地 data/subscribers.json（开发/测试）。

邮件：
  - 设了 RESEND_API_KEY → 真实发送（需 FROM_EMAIL 为 Resend 已验证域名）。
  - 否则 → dry-run：打印将要发送的邮件，不联网。

实时汇率：
  - 默认 https://api.frankfurter.app/latest?from=X&to=CNY（ECB 参考价，每日更新，免费）。
  - --offline 时使用本地 data/platforms.json 的 fx 值（不联网，便于本地验证）。

CLI 示例：
  python scripts/rate_alert.py subscribe --email a@b.com --pair USDCNY --target 7.20
  python scripts/rate_alert.py check                 # dry-run（不发送）
  python scripts/rate_alert.py check --send          # 真正发送（需 RESEND_API_KEY）
  python scripts/rate_alert.py --offline selftest    # 离线自检（不联网、不发送）
  python scripts/rate_alert.py list
  python scripts/rate_alert.py reset                 # 清除已通知标记
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBS_FILE = os.path.join(REPO_ROOT, "data", "subscribers.json")
PLATFORMS_FILE = os.path.join(REPO_ROOT, "data", "platforms.json")

PAIRS = ["USDCNY", "AUDCNY", "GBPCNY", "CADCNY", "JPYCNY", "KRWCNY", "SGDCNY", "EURCNY", "HKDCNY"]
# 部分货币按"每 100 单位"展示（与目标值口径一致）
UNIT = {"JPY": 100, "KRW": 100}

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "alerts@remit.david-cells.com")
RATE_API = os.environ.get("RATE_API", "https://api.frankfurter.app/latest")
SUBS_KEY = "remitguide:subscribers"


# ---------------------------------------------------------------------------
# 存储层
# ---------------------------------------------------------------------------
def _upstash(method, path, body=None):
    url = "%s/%s" % (UPSTASH_URL.rstrip("/"), path)
    data = None
    headers = {"Authorization": "Bearer %s" % UPSTASH_TOKEN}
    if body is not None:
        data = body.encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _use_upstash():
    return bool(UPSTASH_URL and UPSTASH_TOKEN)


def load_subs():
    if _use_upstash():
        try:
            res = _upstash("GET", "get/%s" % SUBS_KEY)
            raw = res.get("result")
            return json.loads(raw) if raw else []
        except Exception as e:  # noqa: BLE001
            print("[WARN] Upstash 读取失败，回退空列表：%s" % e)
            return []
    # 本地文件
    if not os.path.exists(SUBS_FILE):
        return []
    try:
        with open(SUBS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_subs(subs):
    if _use_upstash():
        _upstash("POST", "set/%s" % SUBS_KEY, body=json.dumps(subs))
        return
    os.makedirs(os.path.dirname(SUBS_FILE), exist_ok=True)
    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 订阅
# ---------------------------------------------------------------------------
def add_subscriber(email, pair, cond, target):
    email = (email or "").strip().lower()
    pair = (pair or "").strip().upper()
    cond = (cond or "ge").strip().lower()
    if not email or "@" not in email:
        raise ValueError("邮箱无效")
    if pair not in PAIRS:
        raise ValueError("不支持的货币对：%s（可选：%s）" % (pair, ", ".join(PAIRS)))
    if cond not in ("ge", "le"):
        raise ValueError("cond 必须为 ge 或 le")
    target = float(target)
    if not (target > 0):
        raise ValueError("目标汇率必须大于 0")

    subs = load_subs()
    for s in subs:
        if s["email"] == email and s["pair"] == pair:
            s["cond"] = cond
            s["target"] = target
            s["notified"] = False
            s["updated"] = _now()
            save_subs(subs)
            return s, "updated"
    rec = {
        "email": email,
        "pair": pair,
        "cond": cond,
        "target": target,
        "notified": False,
        "created": _now(),
        "updated": _now(),
    }
    subs.append(rec)
    save_subs(subs)
    return rec, "added"


# ---------------------------------------------------------------------------
# 汇率
# ---------------------------------------------------------------------------
def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_rate_per_unit(pair, offline=False):
    """返回 1 单位 base 兑换的 CNY（与 data/platforms.json 口径一致）。"""
    base = pair[:3]
    quote = pair[3:]
    if offline:
        with open(PLATFORMS_FILE, encoding="utf-8") as f:
            fx = json.load(f)["_meta"]["fx"]
        if pair not in fx:
            raise ValueError("离线 fx 无 %s" % pair)
        return float(fx[pair])
    url = "%s?from=%s&to=%s" % (RATE_API, base, quote)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if quote not in data.get("rates", {}):
        raise ValueError("汇率源未返回 %s" % quote)
    return float(data["rates"][quote])


def value_for_target(pair, offline=False):
    """按订阅口径（JPY/KRW 用每 100）返回用于比较的数值。"""
    base = pair[:3]
    return get_rate_per_unit(pair, offline=offline) * UNIT.get(base, 1)


def threshold_met(value, cond, target):
    return (value >= target) if cond == "ge" else (value <= target)


# ---------------------------------------------------------------------------
# 邮件（Resend）
# ---------------------------------------------------------------------------
def send_email(to, subject, html):
    if not RESEND_API_KEY:
        print("[DRY-RUN] 将发送邮件 → %s | 主题：%s" % (to, subject))
        return True
    payload = {"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html}
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer %s" % RESEND_API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("[OK] 已发送邮件 → %s（HTTP %s）" % (to, resp.status))
        return True
    except urllib.error.HTTPError as e:
        print("[ERR] 发送失败 %s：%s" % (to, e.read().decode("utf-8", "ignore")[:300]))
        return False
    except Exception as e:  # noqa: BLE001
        print("[ERR] 发送失败 %s：%s" % (to, e))
        return False


def _alert_html(sub, value):
    cond_txt = "达到或超过" if sub["cond"] == "ge" else "跌破"
    return (
        "<div style='font-family:Inter,Arial,sans-serif;max-width:480px;margin:0 auto;"
        "border:3px solid #100e05;padding:20px;color:#100e05;'>"
        "<h2 style='margin:0 0 12px;font-family:Fraunces,serif;'>RemitGuide 汇率警报</h2>"
        "<p>你订阅的 <b>%s</b> 已%s目标 <b>%.4f</b>。</p>"
        "<p style='font-size:22px;font-weight:700;margin:14px 0;'>当前：<b>%.4f</b></p>"
        "<p style='font-size:13px;color:#6b6256;'>仅作信息提醒，不构成投资建议。可登录取消订阅（即将上线）。</p>"
        "</div>" % (sub["pair"], cond_txt, sub["target"], value)
    )


# ---------------------------------------------------------------------------
# 检查 + 提醒
# ---------------------------------------------------------------------------
def check_and_notify(send=False, offline=False):
    subs = load_subs()
    pending = [s for s in subs if not s.get("notified")]
    print("=== 汇率警报检查 %s（%s）===" % (_now(), "离线" if offline else "实时"))
    print("订阅总数 %d，待检查 %d" % (len(subs), len(pending)))
    sent = 0
    for s in pending:
        try:
            value = value_for_target(s["pair"], offline=offline)
        except Exception as e:  # noqa: BLE001
            print("  [SKIP] %s 取汇率失败：%s" % (s["pair"], e))
            continue
        met = threshold_met(value, s["cond"], s["target"])
        mark = "✓ 触发" if met else "— 未触发"
        print("  %s %s 当前 %.4f / 目标 %.4f %s" % (s["email"], s["pair"], value, s["target"], mark))
        if met:
            if send:
                if send_email(s["email"], "RemitGuide 汇率警报：%s 已触发" % s["pair"], _alert_html(s, value)):
                    s["notified"] = True
                    sent += 1
            else:
                print("    [DRY-RUN] 将提醒 %s（加 --send 真正发送）" % s["email"])
    if send:
        save_subs(subs)
    print("DONE：本次发送 %d 封" % sent)
    return sent


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="RemitGuide 汇率警报引擎")
    ap.add_argument("--offline", action="store_true", help="使用本地 fx 值，不联网")
    sub = ap.add_subparsers(dest="cmd")

    p_sub = sub.add_parser("subscribe", help="新增/更新订阅")
    p_sub.add_argument("--email", required=True)
    p_sub.add_argument("--pair", required=True, help="如 USDCNY")
    p_sub.add_argument("--target", required=True, type=float)
    p_sub.add_argument("--cond", default="ge", choices=["ge", "le"])
    p_sub.add_argument("--confirm", action="store_true", help="发送订阅确认邮件")

    sub.add_parser("check", help="检查并提醒（默认 dry-run）").add_argument("--send", action="store_true")
    sub.add_parser("list", help="列出订阅")
    sub.add_parser("reset", help="清除所有已通知标记")
    p_wipe = sub.add_parser("wipe", help="删除全部订阅（危险）")
    p_wipe.add_argument("--yes", action="store_true")

    p_st = sub.add_parser("selftest", help="离线自检")
    p_st.add_argument("--send", action="store_true", help="自检时也尝试真实发送")

    args = ap.parse_args()

    if args.cmd == "subscribe":
        rec, action = add_subscriber(args.email, args.pair, args.cond, args.target)
        print("[OK] 订阅%s：%s %s %s %.4f" % (action, rec["email"], rec["pair"], rec["cond"], rec["target"]))
        if args.confirm:
            send_email(rec["email"], "RemitGuide 汇率警报已订阅",
                       "<div style='font-family:Inter,Arial,sans-serif;border:3px solid #100e05;padding:20px;'>"
                       "<h2>已订阅汇率警报</h2><p>%s %s 目标 %.4f。达到时会邮件提醒你。</p></div>"
                       % (rec["pair"], rec["cond"], rec["target"]))
    elif args.cmd == "check":
        check_and_notify(send=args.send, offline=args.offline)
    elif args.cmd == "list":
        subs = load_subs()
        for s in subs:
            print("%s | %s | %s %.4f | notified=%s" % (s["email"], s["pair"], s["cond"], s["target"], s.get("notified")))
        print("共 %d 条" % len(subs))
    elif args.cmd == "reset":
        subs = load_subs()
        for s in subs:
            s["notified"] = False
        save_subs(subs)
        print("[OK] 已清除 %d 条订阅的已通知标记" % len(subs))
    elif args.cmd == "wipe":
        if not args.yes:
            print("[ABORT] 需加 --yes 确认删除全部订阅")
            return
        save_subs([])
        print("[OK] 已删除全部订阅")
    elif args.cmd == "selftest":
        test_email = "selftest@remitguide.local"
        # 用一个必定触发的目标（实时 USD/CNY ≈ 6~7，目标设 0.01 ≥ 即触发）
        add_subscriber(test_email, "USDCNY", "ge", 0.01)
        print("[SELFTEST] 已写入测试订阅，开始离线检查…")
        check_and_notify(send=args.send, offline=True)
        # 清理
        subs = [s for s in load_subs() if s["email"] != test_email]
        save_subs(subs)
        print("[SELFTEST] 已清理测试订阅。引擎逻辑正常。")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
