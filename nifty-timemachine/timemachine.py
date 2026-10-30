#!/usr/bin/env python3
"""Nifty Time Machine: replay an intraday NSE trade 10,000 times before you take it.

Built for the Indian market (NSE, 9:15 to 3:30 IST, 75 five-minute bars).
Method inspired by the MIT-licensed day-trader-skill by Jake Schincariol,
rewritten from scratch for NSE tickers (RELIANCE.NS, ^NSEI) and IST sessions.

Usage:
  python3 timemachine.py orb ^NSEI                      # latest full session, 15-min opening range breakout
  python3 timemachine.py orb RELIANCE.NS --date 2026-10-29
  python3 timemachine.py run ^NSEI --date 2026-10-29 --entry 25810 --stop 25760 \
      --target 25860 --entry-time 10:05
  add --json for machine-readable output, --replays N, --seed N (default 19)

Education only. A simulation from the last 60 days, not a prediction, not advice.
"""
import argparse, json, random, sys, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
SESSION_START = (9, 15)
SESSION_BARS = 75          # 9:15 to 15:30 in 5-minute bars
OR_BARS = 3                # 15-minute opening range: 9:15, 9:20, 9:25

class TMError(Exception):
    pass

def slot(dt):
    """Bar index within the NSE session, or None if outside it."""
    m = (dt.hour * 60 + dt.minute) - (SESSION_START[0] * 60 + SESSION_START[1])
    if m < 0 or m % 5:
        return None
    i = m // 5
    return i if i < SESSION_BARS else None

def fetch(sym):
    url = "https://query2.finance.yahoo.com/v8/finance/chart/%s?range=60d&interval=5m" % urllib.parse.quote(sym.upper())
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise TMError("Yahoo has no 5-minute chart for %s (HTTP %d). NSE stocks end in .NS, BSE in .BO, the Nifty 50 is ^NSEI. Renamed companies get new tickers." % (sym, e.code))
    except urllib.error.URLError as e:
        raise TMError("could not reach Yahoo (%s). On a Mac with Homebrew Python, set SSL_CERT_FILE to a certificate bundle." % e.reason)
    res = (data.get("chart") or {}).get("result")
    if not res:
        raise TMError("Yahoo returned no data for %s" % sym)
    return res[0]

def sessions(res):
    """{date: [75 bars of (o,h,l,c)]} for FULL sessions only."""
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    days = {}
    for k, t in enumerate(ts):
        o, h, l, c = q["open"][k], q["high"][k], q["low"][k], q["close"][k]
        if None in (o, h, l, c):
            continue
        dt = datetime.fromtimestamp(t, IST)
        i = slot(dt)
        if i is None:
            continue
        days.setdefault(dt.date().isoformat(), {})[i] = (o, h, l, c)
    # Yahoo leaves a few empty bars on quiet stocks; up to 3 are filled flat at the last close.
    full = {}
    for d, b in days.items():
        if 0 not in b or len(b) < SESSION_BARS - 3:
            continue
        bars, pc = [], b[0][0]
        for i in range(SESSION_BARS):
            bars.append(b.get(i, (pc, pc, pc, pc)))
            pc = bars[-1][3]
        full[d] = bars
    return dict(sorted(full.items()))

def ratios(day, prev_close):
    out, pc = [], prev_close
    for o, h, l, c in day:
        out.append((o / pc, h / pc, l / pc, c / pc))
        pc = c
    return out

def orb_plan(day, target_r=1.0):
    """15-minute opening range breakout, long only: entry at the close of the first bar
    that closes above the range high; stop at the range midpoint; target at target_r x risk."""
    hi = max(b[1] for b in day[:OR_BARS]); lo = min(b[2] for b in day[:OR_BARS])
    for i in range(OR_BARS, SESSION_BARS - 1):
        if day[i][3] > hi:
            entry = day[i][3]; stop = (hi + lo) / 2
            risk = entry - stop
            if risk <= 0:
                return None
            return {"entry": entry, "stop": stop, "target": entry + target_r * risk,
                    "entry_bar": i + 1, "range": (lo, hi), "target_r": target_r}
    return None

def walk(price, bars, stop, target):
    """bars: list of (o,h,l,c) ratios applied from price. Stop is checked first.
    Returns (outcome, exit price, price at 3:30 PM)."""
    p, res, px = price, None, None
    for ro, rh, rl, rc in bars:
        if res is None and p * rl <= stop:
            res, px = "stop", stop
        elif res is None and p * rh >= target:
            res, px = "target", target
        p = p * rc
    return (res, px, p) if res else ("neither", p, p)

def simulate(pool, plan, n, seed, window=2):
    rng = random.Random(seed)
    risk = plan["entry"] - plan["stop"]
    out = {"target": 0, "stop": 0, "neither": 0, "green": 0}
    closes, rs = [], []
    for _ in range(n):
        bars = []
        for i in range(plan["entry_bar"], SESSION_BARS):
            day = rng.choice(pool)
            j = min(SESSION_BARS - 1, max(0, i + rng.randint(-window, window)))
            bars.append(day[j])
        res, px, close = walk(plan["entry"], bars, plan["stop"], plan["target"])
        out[res] += 1
        if res == "target":
            r = plan["target_r"]; out["green"] += 1
        elif res == "stop":
            r = -1.0
        else:
            r = (px - plan["entry"]) / risk
            if px > plan["entry"]:
                out["green"] += 1
        closes.append(close); rs.append(r)
    closes.sort()
    pct = lambda q: closes[int(q * (len(closes) - 1))]
    return {k: 100.0 * v / n for k, v in out.items()} | {
        "median_close": pct(0.5), "p5": pct(0.05), "p95": pct(0.95), "avg_r": sum(rs) / n}

def history(days, target_r):
    h = {"sessions": len(days), "fired": 0, "target": 0, "stop": 0, "neither": 0, "r": 0.0}
    for day in days:
        plan = orb_plan(day, target_r)
        if not plan:
            continue
        h["fired"] += 1
        res, px = real_walk(day, plan)
        h[res] += 1
        h["r"] += plan["target_r"] if res == "target" else -1.0 if res == "stop" else (px - plan["entry"]) / (plan["entry"] - plan["stop"])
    if h["fired"]:
        h["avg_r"] = h["r"] / h["fired"]
    return h

def real_walk(day, plan):
    for o, hi, lo, c in day[plan["entry_bar"]:]:
        if lo <= plan["stop"]:
            return "stop", plan["stop"]
        if hi >= plan["target"]:
            return "target", plan["target"]
    return "neither", day[-1][3]

def verdict(mc, target_r):
    sided = mc["target"] + mc["stop"]
    if sided <= 0:
        return "No replay hit a side; the close decides everything."
    share = 100.0 * mc["target"] / sided
    need = 100.0 / (1 + target_r)
    gap = share - need
    if abs(gap) < 5:
        v = "Close to a coin flip" if target_r == 1 else "Close to break-even"
    elif abs(gap) < 15:
        v = "Leans toward the target" if gap > 0 else "Leans toward the stop"
    else:
        v = "Strongly toward the target" if gap > 0 else "Strongly toward the stop"
    return "%s: target first %.1f %% vs stop first %.1f %%." % (v, mc["target"], mc["stop"])

def hhmm(i):
    m = SESSION_START[0] * 60 + SESSION_START[1] + 5 * i
    return "%d:%02d" % (m // 60, m % 60)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["orb", "run"])
    ap.add_argument("symbol")
    ap.add_argument("--date")
    ap.add_argument("--entry", type=float); ap.add_argument("--stop", type=float); ap.add_argument("--target", type=float)
    ap.add_argument("--entry-time", help="IST bar start, e.g. 10:05")
    ap.add_argument("--target-r", type=float, default=1.0)
    ap.add_argument("--replays", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=19)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        days = sessions(fetch(a.symbol))
        dates = list(days)
        if not dates:
            raise TMError("no full NSE sessions in the data")
        d = a.date or dates[-1]
        if d not in days:
            raise TMError("%s is not a full session in the last 60 days (have %s to %s)" % (d, dates[0], dates[-1]))
        before = [x for x in dates if x < d]
        if len(before) < 20:
            raise TMError("only %d full sessions before %s; need 20" % (len(before), d))
        day = days[d]
        if a.mode == "orb":
            plan = orb_plan(day, a.target_r)
            if not plan:
                raise TMError("no opening range breakout on %s. Try another --date, or give your own plan with run" % d)
        else:
            if None in (a.entry, a.stop, a.target, a.entry_time):
                raise TMError("run needs --entry, --stop, --target and --entry-time")
            h, m = map(int, a.entry_time.split(":"))
            i = slot(datetime(2000, 1, 1, h, m))
            if i is None or a.stop >= a.entry or a.target <= a.entry:
                raise TMError("plan does not make sense (long only: stop < entry < target, time on the 5-minute grid)")
            plan = {"entry": a.entry, "stop": a.stop, "target": a.target, "entry_bar": i,
                    "target_r": (a.target - a.entry) / (a.entry - a.stop)}
        pool = []
        prev = None
        for x in dates:
            if x >= d:
                break
            pc = prev[-1][3] if prev else days[x][0][0]
            pool.append(ratios(days[x], pc)); prev = days[x]
        mc = simulate(pool, plan, a.replays, a.seed)
        hist = history([days[x] for x in before], plan["target_r"]) if a.mode == "orb" else None
        out = {"symbol": a.symbol.upper(), "date": d, "plan": plan, "entry_time": hhmm(plan["entry_bar"]),
               "replays": a.replays, "seed": a.seed, "pool_sessions": len(pool), "mc": mc,
               "history": hist, "verdict": verdict(mc, plan["target_r"])}
    except TMError as e:
        print("Nifty Time Machine: %s" % e, file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(out, indent=2, default=float)); return 0
    p = plan
    print("%s, %s. Entry %.2f at %s IST, stop %.2f, target %.2f (%.1fR)." % (out["symbol"], d, p["entry"], out["entry_time"], p["stop"], p["target"], p["target_r"]))
    print("%d replays of the rest of the session to 3:30 PM, from %d full sessions, seed %d." % (a.replays, len(pool), a.seed))
    print("  target first  %5.1f %%" % mc["target"])
    print("  stop first    %5.1f %%" % mc["stop"])
    print("  neither       %5.1f %%   still open at 3:30 PM" % mc["neither"])
    print("  green         %5.1f %%   target first, or above the entry at 3:30 PM" % mc["green"])
    print("  Price at 3:30 PM: median %.2f, 90 %% of replays between %.2f and %.2f." % (mc["median_close"], mc["p5"], mc["p95"]))
    print("  Average R: %+.3f" % mc["avg_r"])
    if hist:
        print("History: the same rule on %d real sessions fired %d times: %d target, %d stop, %d neither. Average R %+.3f." % (
            hist["sessions"], hist["fired"], hist["target"], hist["stop"], hist["neither"], hist.get("avg_r", 0)))
    print(out["verdict"])
    print("A simulation from the last 60 days, not a prediction. Not financial advice.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
