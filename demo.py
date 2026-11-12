"""StockSage demo — runs one full live cycle and narrates the result.

Usage:  python demo.py            (from the repo root)

What it does:
  1. Runs one full live cycle via the core engine: `python -m stocksage run`.
  2. Reads the state the core just wrote (data/state.json).
  3. Prints a plain-language summary for the video: top 3 stocks with
     scores and reasons, portfolio totals, and the latest rebalance
     decision with its reason.

It only ever reports LIVE data. If the core has not produced live state
yet — the run failed, or data/state.json is missing — it says so plainly
and prints no numbers. It never prints sample or invented figures.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
STATE_FILE = DATA_DIR / "state.json"
DECISIONS_FILE = DATA_DIR / "decisions.jsonl"


def run_core_cycle() -> bool:
    """Run one full live cycle. Returns True if the core exited cleanly."""
    print("Step 1 — running one full live cycle (python -m stocksage run)…")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "stocksage", "run"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("The core run timed out after 10 minutes. No live state to report.")
        return False
    except OSError as exc:
        print(f"Could not start the core engine: {exc}")
        return False
    if result.stdout.strip():
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(f"The core run failed (exit code {result.returncode}).")
        if result.stderr.strip():
            print(result.stderr.rstrip())
        return False
    print("Core run finished cleanly.")
    return True


def load_live_state() -> dict | None:
    """Load data/state.json, rejecting sample data. None if absent/unusable."""
    if not STATE_FILE.exists():
        return None
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict) or not state.get("scores"):
        return None
    if state.get("sample"):
        return None  # sample data must never be narrated as live
    return state


def load_latest_decision(state: dict) -> dict | None:
    """Newest rebalance decision: decisions.jsonl last line, else state['decisions']."""
    rows: list = []
    try:
        for line in DECISIONS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        rows = []
    if rows:
        return rows[-1]
    decisions = state.get("decisions") or []
    return decisions[-1] if decisions else None


def fmt_usd(value) -> str:
    if value is None:
        return "not reported"
    return f"${value:,.2f}"


def narrate(state: dict) -> None:
    as_of = state.get("as_of", "unknown time")
    universe = state.get("universe") or {}
    scores = sorted(state.get("scores") or [], key=lambda s: s.get("score") or 0,
                    reverse=True)
    portfolio = state.get("portfolio") or {}

    print()
    print("=" * 64)
    print("StockSage — LIVE DATA")
    print(f"As of {as_of} (UTC)")
    print(f"Universe: {universe.get('count', '?')} tokenized stocks on Base, "
          f"{universe.get('minted', '?')} ever minted; {len(scores)} scored.")
    print("=" * 64)
    print()
    print("Top 3 stocks by score")
    print("---------------------")
    for i, s in enumerate(scores[:3], start=1):
        comp = s.get("components") or {}
        print(f"{i}. {s.get('symbol')} — {s.get('name')} — score {s.get('score')} out of 100")
        print(f"   On-chain {comp.get('onchain')}, momentum {comp.get('momentum')}, "
              f"market {comp.get('market')}; price {fmt_usd(s.get('price_usd'))} "
              f"({s.get('price_source') or 'no price source'})")
        for reason in s.get("reasons") or []:
            print(f"   • {reason}")
        print()
    print("Portfolio (paper trading — no real money)")
    print("------------------------------------------")
    print(f"Total value: {fmt_usd(portfolio.get('total_value_usd'))}")
    print(f"Cash: {fmt_usd(portfolio.get('cash_usd'))}")
    for pos in portfolio.get("positions") or []:
        print(f"  {pos.get('symbol')}: {pos.get('shares')} shares at "
              f"{fmt_usd(pos.get('price_usd'))} = {fmt_usd(pos.get('value_usd'))} "
              f"({pos.get('weight_pct')}% of the portfolio)")
    print()
    print("Latest rebalance decision")
    print("-------------------------")
    decision = load_latest_decision(state)
    if decision:
        print(f"{decision.get('ts')}: {decision.get('action')} {decision.get('symbol')} — "
              f"weight {decision.get('from_weight_pct')}% → {decision.get('to_weight_pct')}%, "
              f"score {decision.get('score')}.")
        print(f"Reason: {decision.get('reason')}")
    else:
        print("No rebalance decision has been recorded yet.")
    print()
    print("Paper trading only. Not investment advice.")


def main() -> int:
    print("StockSage demo — one live cycle, narrated.")
    print()
    if not run_core_cycle():
        print()
        print("NO LIVE DATA: the core engine did not produce a live cycle, "
              "so there is nothing to narrate.")
        print("Fix the core run first, then run this demo again.")
        return 1
    state = load_live_state()
    if state is None:
        print()
        print("NO LIVE DATA: the core run finished but data/state.json is "
              "missing, empty, or sample data. Nothing to narrate — no "
              "numbers have been printed.")
        return 1
    narrate(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
