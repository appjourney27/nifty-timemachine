---
name: nifty-timemachine
description: >-
  Nifty Time Machine for Indian stocks. Replays the rest of an NSE trading day
  10,000 times from the stock's own 5-minute bars over the last 60 days, and
  re-runs the same opening-range-breakout rule on every past session, before
  you risk a rupee. Works on NSE stocks (HDFCBANK.NS), BSE stocks
  (RELIANCE.BO), indices (^NSEI Nifty 50, ^NSEBANK Bank Nifty, ^BSESN Sensex)
  and ETFs (NIFTYBEES.NS), on the 9:15 to 3:30 IST session. Use when the user says "run the
  time machine", "replay this trade", "what are the odds", "simulate this
  trade", "backtest this setup on Nifty", or "is this a coin flip".
argument-hint: "[TICKER, e.g. ^NSEI or RELIANCE.NS]"
---

# nifty-timemachine

Before money goes in, this skill asks one question: if today plays out like
this stock's last 60 days, how often does the plan hit the target first, the
stop first, or neither by 3:30 PM? It answers with 10,000 replays and with the
real record of the same rule on every past session. It is a simulation, not a
prediction. Most F&O traders in India lose money (SEBI's own study), and a
good-looking replay does not change that.

`${CLAUDE_SKILL_DIR}` is this skill's folder.

```bash
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" orb NIFTY                        # latest session with a breakout, 15-min opening range
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" orb RELIANCE --date 2026-10-29   # plain names mean NSE; add .BO for BSE
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" run NIFTY --date 2026-10-29 \
    --entry 22758.40 --stop 22701.27 --target 22815.53 --entry-time 9:40
```

Flags: `--target-r` (default 1), `--replays` (default 10000), `--seed`
(default 19), `--json`. Names: NIFTY, BANKNIFTY, SENSEX, or any stock such as
RELIANCE (NSE) or RELIANCE.BO (BSE). On Windows use `python` if `python3` is
missing. Python 3.8+, nothing to install. Data: Yahoo
Finance's free 5-minute chart (60 days), unofficial, can lag.

## How it works

1. **Sessions.** Keeps full NSE days only: 75 five-minute bars, 9:15 to
   3:30 IST. Up to 3 empty bars (Yahoo leaves the last minutes blank on some
   stocks) are filled flat at the last close. Today, if still open, is left out.
2. **The plan.** `orb` mode: the 15-minute opening range (9:15 to 9:30); entry
   at the close of the first bar that closes above it; stop at the range
   midpoint; target at 1R. `run` mode takes your own entry, stop, target, time.
3. **One replay.** From the entry, each remaining bar is drawn at random from
   a past session at the same time of day (plus or minus 2 bars) and scaled to
   the current price. The stop is checked before the target in every bar.
4. **10,000 replays** give the odds: target first, stop first, neither, and
   green (target first or above the entry at 3:30 PM), the price range at the
   close and the average R.
5. **History.** The same rule on every past session: how often it fired and
   what really happened.
6. **Verdict.** At 1R the target must come first in half the replays that hit
   a side to break even (1 in 1 + R in general). Within 5 points: "close to a
   coin flip"; 5 to 15: "leans"; 15 or more: "strongly".

## Steps

1. Ask which stock or index, and whether to use the opening range breakout or
   their own plan. Long trades only.
2. Run the tool. Report, in this order: the odds, the 3:30 PM price range,
   the average R, the history line, then the verdict exactly as printed. Say
   the seed.
3. If it is a coin flip, say so plainly. Never dress it up.
4. Say once that this is built from the last 60 days and is not a prediction
   or advice. Results, news and RBI days can do what those 60 days never did.

## Never

Never place an order, size a position, name a stock to buy, promise a profit,
or call a result a sure thing. Long only. Education, not financial advice.
