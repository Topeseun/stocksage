"""Agent: one live cycle — refresh universe (if stale) -> gather signals
-> score -> compute target weights -> execute paper rebalances -> write outputs.

Read-only plus paper trading only. No signing, no real funds.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from . import portfolio as portfolio_mod
from . import research, signals, state as state_mod, universe as universe_mod

logger = logging.getLogger("stocksage.agent")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _universe_is_stale() -> bool:
    from . import config
    cache = universe_mod.UNIVERSE_CACHE
    if not cache.exists():
        return True
    age = time.time() - cache.stat().st_mtime
    return age > config.UNIVERSE_STALE_SECONDS


def run_cycle(refresh: bool = False) -> dict:
    """Run one full cycle against live data; returns the state dict."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    now = _utcnow_iso()

    uni = universe_mod.fetch_universe(refresh=refresh or _universe_is_stale())
    logger.info("Universe: %d records, %d minted, %d dropped",
                uni["count"], uni["minted"], len(uni.get("dropped", [])))
    for row in uni.get("dropped", []):
        logger.warning("Dropped unverified token %s: %s",
                       row.get("symbol"), row.get("drop_reason"))

    feats = signals.gather_signals(uni["tokens"])
    logger.info("Features gathered: %d tokens, %d unscored",
                len(feats["tokens"]), len(feats["unscored"]))
    for u in feats["unscored"]:
        logger.warning("Unscored %s: %s", u["symbol"], u["reason"])

    scores = research.score_tokens(feats["tokens"])
    logger.info("Scored %d tokens; top: %s",
                len(scores),
                ", ".join(f"{s['symbol']} {s['score']}" for s in scores[:5]))

    prev = state_mod.load_state()
    pf = (prev or {}).get("portfolio") or portfolio_mod.new_portfolio()
    # Revalue existing positions at today's prices before rebalancing.
    price_map = {s["address"].lower(): s["price_usd"] for s in scores
                 if s.get("price_usd")}
    portfolio_mod.revalue_portfolio(pf, price_map)

    decisions = portfolio_mod.execute_rebalance(pf, scores, now)
    for d in decisions:
        logger.info("Decision %s %s: %s", d["action"], d["symbol"], d["reason"])

    all_decisions = state_mod.load_decisions() + decisions
    state_mod.append_decisions(decisions)
    new_state = state_mod.build_state(now, uni, scores, pf, all_decisions)
    state_mod.save_state(new_state)
    logger.info("Cycle done: portfolio $%.2f (cash $%.2f, %d positions)",
                pf["total_value_usd"], pf["cash_usd"], len(pf["positions"]))
    return new_state
