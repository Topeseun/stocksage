# StockSage — Demo Video Script

**Project:** StockSage — autonomous AI agent for tokenized stocks on Base
**Track:** Base Stocks Maxxing hackathon, Agentic Stock Finance track
**Length:** ~2 minutes (120 seconds)
**Format:** Screen-recorded dashboard walkthrough + voiceover. No face-to-camera.
**Pace:** ~150 words per minute — slow enough for a busy judge to follow.
**Language rule:** Plain English throughout. No jargon without an immediate plain explanation. No hype, no unverifiable claims.

## Status note (read before recording)

- The research report (`~/workspace/stocksage/research/research-report.md`) does **not exist yet** at time of writing.
- Token identities used below (symbols + contract addresses) are **verified real** — taken from `~/workspace/stocksage/research/minted.csv` (72 Coinbase tokenized stocks on Base, pulled 2026-11-12). They may be named on screen.
- Every **score, portfolio value, holding weight, rebalance amount and decision reason** is a `[PLACEHOLDER]` — no scores or portfolio data exist yet. Replace each one from the verified dashboard immediately before recording. **Never read a placeholder number aloud and never show a made-up number on screen.**
- Paper trading only. No real funds, no token launched. The script says this once, plainly.

---

## Full narration (120 seconds)

### Segment 1 — The problem (0:00–0:08, 8 sec)

**Narration:**
> "Tokenized stocks are real stocks, turned into tokens you can hold on Base. Dozens of them launched at once — and they move fast. No human can research all of them by hand, every day."

**Caption/subtitle:**
> Tokenized stocks are real stocks, turned into tokens you can hold on Base. Dozens launched at once — and they move fast. No human can research all of them by hand, every day.

**On screen:** Title card: "StockSage" + one line: "An autonomous AI agent for tokenized stocks on Base." Background: slow pan of the token list (symbols only, no numbers yet).

---

### Segment 2 — What StockSage is (0:08–0:18, 10 sec)

**Narration:**
> "StockSage is an autonomous AI agent that does that research for you. It reads live activity on Base and market data, scores every stock, and manages a portfolio — rebalancing it as the signals change."

**Caption/subtitle:**
> StockSage is an autonomous AI agent that does that research for you. It reads live activity on Base and market data, scores every stock, and manages a portfolio — rebalancing it as the signals change.

**On screen:** Title card fades to the dashboard home view. The three-step loop appears as on-screen text: "RESEARCH → SCORE → REBALANCE".

---

### Segment 3 — How it works, and why it's novel (0:18–0:30, 12 sec)

**Narration:**
> "It works in a simple loop. First, research: the agent reads on-chain activity and price action for each stock. Then, score: it gives every stock one clear, explainable score. Then, rebalance: it shifts the portfolio toward the strongest scores — and writes down why. The new part isn't the scores. It's that the whole loop runs by itself, in the open, on live Base data."

**Caption/subtitle:**
> It works in a simple loop. First, research: the agent reads on-chain activity and price action for each stock. Then, score: it gives every stock one clear, explainable score. Then, rebalance: it shifts the portfolio toward the strongest scores — and writes down why. The new part isn't the scores. It's that the whole loop runs by itself, in the open, on live Base data.

**On screen:** The three steps highlight one at a time (RESEARCH, then SCORE, then REBALANCE) as each is named. End on the full loop diagram.

> **30-SECOND CHECK:** By 0:30 a judge who knows nothing about the project can say: *tokenized stocks are hard to research by hand; StockSage is an agent that researches them, scores them, and rebalances a portfolio on its own; the novelty is the autonomous, transparent loop running on live Base data.* If any of that is unclear, re-record the opening before touching the rest.

---

### Segment 4 — The research scores (0:30–0:48, 18 sec)

**Narration:**
> "Here's the dashboard. This is the research view. Every tokenized stock gets a score — [TOP STOCK FROM LIVE DATA] is highest right now, at [TOP SCORE]. The score isn't a black box: click any stock and you see what drove it — on-chain activity, price movement, and market signals, each shown separately."

**Caption/subtitle:**
> Here's the dashboard. This is the research view. Every tokenized stock gets a score — [TOP STOCK FROM LIVE DATA] is highest right now, at [TOP SCORE]. The score isn't a black box: click any stock and you see what drove it — on-chain activity, price movement, and market signals, each shown separately.

**On screen:** Dashboard research/scores view. Cursor hovers the top-ranked row, then clicks into one stock's score breakdown (on-chain activity / price action / market signals as separate components).

---

### Segment 5 — The portfolio (0:48–1:05, 17 sec)

**Narration:**
> "Those scores feed straight into the portfolio. This is a paper-trading portfolio — practice money, no real funds. The agent holds more of the highest-scored stocks and less of the weakest. Right now it holds [NUMBER OF HOLDINGS] stocks, and [TOP HOLDING] is the largest position, at [TOP HOLDING WEIGHT] of the portfolio."

**Caption/subtitle:**
> Those scores feed straight into the portfolio. This is a paper-trading portfolio — practice money, no real funds. The agent holds more of the highest-scored stocks and less of the weakest. Right now it holds [NUMBER OF HOLDINGS] stocks, and [TOP HOLDING] is the largest position, at [TOP HOLDING WEIGHT] of the portfolio.

**On screen:** Dashboard portfolio view. Cursor moves across the holdings list, pausing on the largest holding. Portfolio value shown only if it is the live dashboard figure — otherwise keep the value off screen.

---

### Segment 6 — A rebalance decision, with its reason (1:05–1:22, 17 sec)

**Narration:**
> "When scores change, the portfolio changes. Here's the most recent rebalance, from [REBALANCE DATE AND TIME]. The agent [REBALANCE ACTION — e.g. increased its holding in X and trimmed Y]. And here is the reason, in plain words, logged next to the decision: [LOGGED REASON, VERBATIM FROM THE DASHBOARD]. Every decision the agent makes leaves a record like this."

**Caption/subtitle:**
> When scores change, the portfolio changes. Here's the most recent rebalance, from [REBALANCE DATE AND TIME]. The agent [REBALANCE ACTION]. And here is the reason, in plain words, logged next to the decision: [LOGGED REASON, VERBATIM FROM THE DASHBOARD]. Every decision the agent makes leaves a record like this.

**On screen:** Dashboard rebalance-history / decision-log view. Cursor highlights the most recent entry, then the reason text attached to it. Zoom or highlight the reason field so it is readable.

---

### Segment 7 — The loop runs on its own (1:22–1:38, 16 sec)

**Narration:**
> "Nobody clicked a button to make that happen. The agent re-runs the loop on its own — fresh research, fresh scores, and a rebalance whenever the scores move enough. The same view is available from the command line, for anyone who wants to check the agent's work without opening the dashboard."

**Caption/subtitle:**
> Nobody clicked a button to make that happen. The agent re-runs the loop on its own — fresh research, fresh scores, and a rebalance whenever the scores move enough. The same view is available from the command line, for anyone who wants to check the agent's work without opening the dashboard.

**On screen:** Brief CLI shot (one command, e.g. showing scores or latest rebalance — exact command TBD from the real CLI), then back to the dashboard loop diagram. Keep the CLI shot short: 4–5 seconds, large font, no scrolling walls of text.

---

### Segment 8 — What it runs on (1:38–1:52, 14 sec)

**Narration:**
> "Everything you just saw runs on live Base data — real tokenized stocks, real on-chain activity, real prices. The universe covers [NUMBER OF STOCKS TRACKED] tokenized stocks, from [EXAMPLE STOCK A] to [EXAMPLE STOCK B]. And because it's paper trading, you can watch the agent's judgement without risking a cent."

**Caption/subtitle:**
> Everything you just saw runs on live Base data — real tokenized stocks, real on-chain activity, real prices. The universe covers [NUMBER OF STOCKS TRACKED] tokenized stocks, from [EXAMPLE STOCK A] to [EXAMPLE STOCK B]. And because it's paper trading, you can watch the agent's judgement without risking a cent.

**On screen:** Dashboard token-universe / coverage view (or the scores list scrolled to show breadth). Verified example names may be used here, e.g. AAPLc, NVDAc, TSLAc — see live-data slots.

---

### Segment 9 — Close (1:52–2:00, 8 sec)

**Narration:**
> "StockSage: an autonomous AI agent that researches tokenized stocks on Base, scores them, and manages a portfolio — Agentic Stock Finance, running on live Base data."

**Caption/subtitle:**
> StockSage: an autonomous AI agent that researches tokenized stocks on Base, scores them, and manages a portfolio — Agentic Stock Finance, running on live Base data.

**On screen:** Closing title card: "StockSage" + "Agentic Stock Finance — Base Stocks Maxxing" + repo/demo link (URL placeholder: [REPO OR DEMO LINK]).

---

## Word count / pacing check

| Segment | Time | Words (approx.) | Pace |
|---|---|---|---|
| 1 Problem | 0:00–0:08 | 33 | ~4.1 w/s — brisk hook, deliberate |
| 2 What it is | 0:08–0:18 | 34 | ~3.4 w/s |
| 3 How it works | 0:18–0:30 | 68 | ~5.7 w/s — fastest stretch; slow down on "in the open, on live Base data" |
| 4 Scores | 0:30–0:48 | 52 | ~2.9 w/s |
| 5 Portfolio | 0:48–1:05 | 54 | ~3.2 w/s |
| 6 Rebalance | 1:05–1:22 | 52 | ~3.1 w/s |
| 7 Autonomy + CLI | 1:22–1:38 | 49 | ~3.1 w/s |
| 8 Live data | 1:38–1:52 | 50 | ~3.6 w/s |
| 9 Close | 1:52–2:00 | 26 | ~3.3 w/s |
| **Total** | **0:00–2:00** | **~418** | **~3.5 w/s average** |

Note: Segment 3 is the densest. If the read runs over 12 seconds, cut "First," / "Then," openers are load-bearing — instead trim "it gives every stock one clear, explainable score" to "it scores every stock, and shows its working." Do not speed up the delivery to fit; cut words instead.

## Recording notes

- **Voice:** One calm, steady voiceover. No background music under narration, or music at −20 dB maximum and only under the title cards.
- **Captions:** Burn in the caption text above (or upload as an .srt with identical wording). Captions must match the spoken words exactly, including placeholder values once filled.
- **No fake numbers:** If a dashboard panel shows a number the narrator does not mention, it must still be a real dashboard number. If the dashboard isn't ready for a shot, cut the shot — do not mock it up with invented figures.
- **X post requirement:** The finished video goes in a public X post tagging @buildonbase. Keep the video under X's limits (≤ 2 min 20 sec; this 2:00 cut fits). Include the repo/demo link in the post text, not only in the video.
- **Retakes:** If any placeholder is still unfilled at record time, record the opening (Segments 1–3) first — they contain no live numbers and never go stale.
