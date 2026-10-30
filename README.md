# Nifty Time Machine

A free Claude skill that replays an Indian intraday trade 10,000 times before you take it. Built for the Indian market on the 9:15 to 3:30 IST session:

- NSE stocks: `HDFCBANK`, `INFY`, `IRFC` (any stock Yahoo Finance lists on NSE)
- BSE stocks: `RELIANCE.BO`
- Indices: `NIFTY`, `BANKNIFTY`, `SENSEX`
- ETFs: `NIFTYBEES`

It tests long (buy) trades only. It works on stocks and indices, not on option or futures contracts.

The idea comes from the MIT-licensed [day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill), which only works on US stocks. This version is written from scratch for India.

## Setup guide

**Aapko chahiye:**

- **Claude Code:** Claude ka coding app (desktop app ya terminal). Skills isi mein chalti hain, aur iske liye Claude ka plan chahiye.
- **Python 3.8 ya naya:** Mac mein aksar pehle se hota hai. Check karne ke liye Claude se bolo: "check if Python is installed". Nahi hai toh python.org se install karo.

Koi API key nahi, koi signup nahi, kuch pay nahi karna data ke liye.

**Step 1: Install karo.** Claude Code kholo, ye link paste karo aur bolo `install skill`:

```
https://github.com/appjourney27/nifty-timemachine
```

**Step 2: Chalao.** Claude se bolo, ya seedha type karo:

```
/nifty-timemachine NIFTY
/nifty-timemachine RELIANCE
```

Aap normal bhasha mein bhi bol sakte ho: "Nifty pe time machine chalao". Skill turant nahi dikhe toh Claude Code band karke dobara kholo.

**Step 3: Result samjho.**

- **target first:** kitne replays mein target pehle laga
- **stop first:** kitne replays mein stop loss pehle laga
- **neither:** 3:30 PM tak dono nahi lage
- **History:** yahi rule pichhle asli dinon mein kaisa chala
- **Verdict:** seedha jawab, jaise "close to a coin flip"

**Haath se install (optional):** repo download karo aur `nifty-timemachine` folder ko `~/.claude/skills/` mein copy karo.

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
