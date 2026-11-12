"""Persistence: state.json + decisions.jsonl under ~/workspace/stocksage/data/.

EXACT state.json schema (dashboard builder depends on it — do not
change field names):
{"as_of": ISO8601 UTC, "universe": {"count": N, "minted": M},
 "scores": [{"address","symbol","name","score",
             "components":{"onchain","momentum","market"},
             "price_usd","price_source","liquidity_usd","volume_24h_usd",
             "supply","multiplier","reasons":[strings]}],
 "portfolio": {"cash_usd","total_value_usd",
               "positions":[{"symbol","address","shares","price_usd",
                             "value_usd","weight_pct"}]},
 "decisions": [last 20 decision objects]}
decisions.jsonl lines (append-only):
{"ts","type":"rebalance","action":"increase|decrease|open|close|hold",
 "symbol","from_weight_pct","to_weight_pct","reason","score"}
"""
from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_FILE = DATA_DIR / "state.json"
DECISIONS_FILE = DATA_DIR / "decisions.jsonl"


def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def load_decisions(limit: int | None = None) -> list[dict]:
    if not DECISIONS_FILE.exists():
        return []
    out: list[dict] = []
    for line in DECISIONS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out[-limit:] if limit else out


def save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def append_decisions(decisions: list[dict]) -> None:
    if not decisions:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DECISIONS_FILE.open("a") as fh:
        for d in decisions:
            fh.write(json.dumps(d) + "\n")


def build_state(as_of: str, universe: dict, scores: list[dict],
                portfolio: dict, decisions: list[dict]) -> dict:
    return {
        "as_of": as_of,
        "universe": {"count": universe.get("count", 0),
                     "minted": universe.get("minted", 0)},
        "scores": scores,
        "portfolio": portfolio,
        "decisions": decisions[-20:],
    }
