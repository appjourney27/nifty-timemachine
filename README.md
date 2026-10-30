# Nifty Time Machine

A free Claude skill that replays an Indian intraday trade 10,000 times before you take it. Built for the Indian market on the 9:15 to 3:30 IST session:

- NSE stocks: `HDFCBANK`, `INFY`, `IRFC` (any stock Yahoo Finance lists on NSE)
- BSE stocks: `RELIANCE.BO`
- Indices: `NIFTY`, `BANKNIFTY`, `SENSEX`
- ETFs: `NIFTYBEES`

It tests long (buy) trades only. It works on stocks and indices, not on option or futures contracts.

The idea comes from the MIT-licensed [day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill), which only works on US stocks. This version is written from scratch for India.

## Setup guide

**What you need:**

- **Claude Code:** Claude's coding app (desktop app or terminal). Skills run here, and it needs a Claude plan.
- **Python 3.8 or newer:** Macs often have it already. To check, ask Claude: "check if Python is installed". If it's missing, install it from python.org.

No API key, no signup, and nothing to pay for the data.

**Step 1: Install.** Open Claude Code, paste this link and say `install skill`:

```
https://github.com/appjourney27/nifty-timemachine
```

**Step 2: Run it.** Ask Claude, or type this directly:

```
/nifty-timemachine NIFTY
/nifty-timemachine RELIANCE
```

You can also ask in plain words: "Run the time machine on Nifty". If the skill doesn't show up, close Claude Code and open it again.

**Step 3: Read the result.**

- **target first:** how many replays hit the target first
- **stop first:** how many replays hit the stop loss first
- **neither:** how many hit neither by 3:30 PM
- **History:** how the same rule did on past real days
- **Verdict:** the plain answer, such as "close to a coin flip"

**Manual install (optional):** download the repo and copy the `nifty-timemachine` folder into `~/.claude/skills/`.

## Example (Nifty 50, 29 Oct 2026, seed 19)

```
^NSEI, 2026-10-29. Entry 22758.40 at 9:40 IST, stop 22701.27, target 22815.53 (1.0R).
10000 replays of the rest of the session to 3:30 PM, from 58 full sessions, seed 19.
  target first   46.6 %
  stop first     52.0 %
  neither         1.5 %   still open at 3:30 PM
History: the same rule on 58 real sessions fired 31 times: 12 target, 14 stop, 5 neither.
Close to a coin flip.
```

## Please read

If a ticker gives "no 5-minute chart", the company may have been renamed or the ticker changed; check it on Yahoo Finance. "No opening range breakout" means the rule did not fire that day: try another `--date`, or give your own plan with `run`.

Education only. Not financial advice, and not from a SEBI-registered adviser. It never places a trade. It is a simulation from the last 60 days of free Yahoo data, which can lag, not a prediction. Most people who trade F&O in India lose money.

MIT licence.
