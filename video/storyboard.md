# StockSage — Demo Video Storyboard

**Companion to:** `script.md` (exact narration + captions).
**Length:** 120 seconds, 9 segments. **Format:** Screen-recorded dashboard walkthrough + voiceover; title cards at start and end only.

## Segment-by-segment table

| # | Time | Narration line (condensed — full text in script.md) | On-screen visual | On-screen text / callout |
|---|---|---|---|---|
| 1 | 0:00–0:08 | "Tokenized stocks are real stocks, turned into tokens you can hold on Base…" | Title card over a slow pan of the token list (symbols only) | **StockSage** — "An autonomous AI agent for tokenized stocks on Base." |
| 2 | 0:08–0:18 | "StockSage is an autonomous AI agent that does that research for you…" | Title card fades to dashboard home view | Loop diagram appears: **RESEARCH → SCORE → REBALANCE** |
| 3 | 0:18–0:30 | "It works in a simple loop. First, research… Then, score… Then, rebalance…" | Same loop diagram; each step highlights as it is named | Each step highlights in turn: **RESEARCH**, then **SCORE**, then **REBALANCE**. Final frame: full loop + "runs by itself, in the open, on live Base data" |
| 4 | 0:30–0:48 | "Here's the dashboard. This is the research view…" | Dashboard research/scores view | Top-ranked row highlighted; then one stock's score-breakdown panel: **On-chain activity / Price action / Market signals** as separate components |
| 5 | 0:48–1:05 | "Those scores feed straight into the portfolio. This is a paper-trading portfolio…" | Dashboard portfolio view | Holdings list; largest holding highlighted. Callout: **"Paper trading — no real funds"** (persistent label on this view) |
| 6 | 1:05–1:22 | "When scores change, the portfolio changes. Here's the most recent rebalance…" | Dashboard rebalance-history / decision-log view | Most recent entry highlighted; its **reason field zoomed/highlighted** so the logged reason is readable on video |
| 7 | 1:22–1:38 | "Nobody clicked a button to make that happen…" | Brief CLI shot (one command, large font), then back to dashboard loop diagram | CLI: single command + its output only — no scrolling. Keep to 4–5 sec |
| 8 | 1:38–1:52 | "Everything you just saw runs on live Base data…" | Token-universe / coverage view, or scores list scrolled to show breadth | Callout: **"[N] tokenized stocks tracked — live Base data"** (N from dashboard) |
| 9 | 1:52–2:00 | "StockSage: an autonomous AI agent that researches tokenized stocks on Base…" | Closing title card | **StockSage** — "Agentic Stock Finance — Base Stocks Maxxing" + repo/demo link |

## Shot list (screen recording — capture in this order)

Record each shot as a separate clip so a bad take doesn't cost the whole video. Suggested order follows the script, but Segments 1–3 (no live numbers) can be recorded first, any time.

1. **Title card (static, 8 sec).** "StockSage" + tagline. Background: slow vertical pan of the token list, symbols only, no scores/numbers visible.
2. **Dashboard home + loop diagram (22 sec).** Home view; the RESEARCH → SCORE → REBALANCE diagram animates or highlights step-by-step. Cursor rests on each step as it is named (0:18 RESEARCH, ~0:23 SCORE, ~0:27 REBALANCE).
3. **Research / scores view (18 sec).** Full scores table visible. Cursor hovers the top-ranked row (~0:36), then clicks into that stock's detail/breakdown (~0:40). Hold on the breakdown panel (on-chain activity / price action / market signals) until the segment ends.
4. **Portfolio view (17 sec).** Holdings list + allocation. Cursor sweeps slowly down the holdings (~0:52), pauses on the largest holding (~0:58). The "Paper trading — no real funds" label must be visible in frame.
5. **Rebalance history / decision log (17 sec).** Most recent entry at top. Cursor highlights the entry (~1:08), then the reason text (~1:14). If the reason text is small, zoom the capture region to the reason field for the last 6 seconds.
6. **CLI (5 sec).** Terminal, large font (≥18 pt), one command showing scores or the latest rebalance. No scrolling, no extra output. Cut back to the dashboard loop diagram for the remaining ~11 sec of the segment.
7. **Token universe / coverage view (14 sec).** Scores list scrolled slowly, or a universe/coverage panel showing the count of tracked stocks. No single number on screen unless it is the live dashboard figure.
8. **Closing title card (static, 8 sec).** "StockSage" + "Agentic Stock Finance — Base Stocks Maxxing" + repo/demo link.

**Capture settings:** 1920×1080, 30 fps. Dashboard at 100% browser zoom unless text is unreadable at video scale — then 125% and re-check framing. Hide bookmarks bar, notifications, and any personal tabs before recording. Mouse movements slow and deliberate; never wiggle the cursor while waiting.

## Live-data slots — fill from the verified dashboard before recording

Every item below must be replaced with the real dashboard value. **Nothing on this list may be invented, estimated, or carried over from an earlier draft.** Check each box as it is filled and re-verify against the dashboard on record day (values move).

### Script placeholders

- [ ] **[TOP STOCK FROM LIVE DATA]** (Segment 4) — highest-scored stock at record time: symbol + full name.
- [ ] **[TOP SCORE]** (Segment 4) — that stock's score, exactly as the dashboard shows it (same scale/units).
- [ ] **[NUMBER OF HOLDINGS]** (Segment 5) — count of stocks currently held in the paper portfolio.
- [ ] **[TOP HOLDING]** (Segment 5) — largest holding by weight: symbol.
- [ ] **[TOP HOLDING WEIGHT]** (Segment 5) — its weight, exactly as shown (e.g. % of portfolio).
- [ ] **[REBALANCE DATE AND TIME]** (Segment 6) — timestamp of the most recent rebalance, as logged.
- [ ] **[REBALANCE ACTION]** (Segment 6) — what the agent did (e.g. "increased its holding in X and trimmed Y"), in the narrator's words but faithful to the log.
- [ ] **[LOGGED REASON, VERBATIM FROM THE DASHBOARD]** (Segment 6) — the decision's logged reason, quoted word-for-word. If the logged reason is jargon-heavy, the narrator may paraphrase it *after* quoting it — never instead of quoting it.
- [ ] **[NUMBER OF STOCKS TRACKED]** (Segment 8) — count of tokenized stocks in the tracked universe.
- [ ] **[EXAMPLE STOCK A] / [EXAMPLE STOCK B]** (Segment 8) — two well-known tracked stocks. Verified candidates (do not need a score to name): see below.
- [ ] **[REPO OR DEMO LINK]** (Segment 9) — final repo or demo URL for the closing card.

### Verified token identities — safe to name (no score needed)

Source: `~/workspace/stocksage/research/minted.csv` (72 Coinbase tokenized stocks on Base, pulled 2026-11-12). Symbols and contracts below are real; use them for examples, the title-card token pan, and Segment 8. **Do not attach any price, score or holding to these names unless the dashboard shows it.**

| Symbol | Contract (Base) | Notes |
|---|---|---|
| AAPLc | `0xb200000000000000000000C2e324d24d7eEcd1fb` | Apple; NAV $356.475 at 2026-11-12 17:21 UTC per source data — snapshot only, do **not** quote on video unless the dashboard shows a live price |
| NVDAc | `0xb20000000000000000000078ee7ce2fE4908108C` | Nvidia; largest supply in the set (46,713 tokens) |
| TSLAc | `0xb2000000000000000000001e800a7f5189430cD0` | Tesla |
| MSFTc | `0xB200000000000000000000Ab99cFa739E253872B` | Microsoft |
| AMZNc | `0xb200000000000000000000d9192b6B456483C2E8` | Amazon |
| GOOGLc | `0xb2000000000000000000002D0BA3164cc74f58B7` | Alphabet |
| METAc | `0xb2000000000000000000008bC8786B856E61707C` | Meta |
| AMDc | `0xB2000000000000000000000d8Ce462E99ee7A47B` | AMD |

Full universe (72 tokens) is in `minted.csv`. Note: only 12 of the 72 had a NAV price in the source pull — a missing price is a data gap, not a zero.

### Still missing (not in any source yet — dashboard must supply)

- Research scores and score components for every stock (Segment 4).
- Portfolio holdings, weights and value (Segment 5).
- Rebalance history and logged reasons (Segment 6).
- The CLI command(s) to show in Segment 7 (exact command TBD from the real CLI — confirm it runs cleanly before recording).
- The research report itself (`~/workspace/stocksage/research/research-report.md` does not exist yet) — when it lands, cross-check the top stock / top score against it.

## Pre-record checklist

- [ ] Dashboard is up and showing live data (not a mock).
- [ ] All live-data slots above are filled in `script.md` and match the dashboard on record day.
- [ ] No placeholder text (`[...]`) remains anywhere in the narration, captions, or on-screen text.
- [ ] "Paper trading — no real funds" is visible during Segment 5.
- [ ] No invented tickers, prices, scores or performance claims appear on screen or in narration.
- [ ] Captions (.srt or burned-in) match the final spoken words exactly.
- [ ] Final video ≤ 2:20 (target 2:00) for the X post tagging @buildonbase.
