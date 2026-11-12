"""Paper portfolio (paper only — no real funds, never signed).

Starting cash $100,000. Target weights are proportional to
max(score - 50, 0) across the top 10 scored tokens, capped at 25% per
position, with the capped excess redistributed to uncapped positions.
A rebalance happens only when a target weight differs from the current
weight by >= 5 percentage points, or a new token enters the top 10.
Trades smaller than $500 are skipped. Every action is logged with a
plain-language reason.
"""
from __future__ import annotations

from . import config


def compute_target_weights(scored: list[dict]) -> dict[str, float]:
    """Target weight % per token address (top 10, score > 50 only).

    Proportional to max(score-50, 0), capped at 25% with iterative
    redistribution of the capped excess. Returns {address: weight_pct}
    summing to <= 100 (less when fewer than 10 tokens clear the floor
    or all excess is capped away — the remainder stays in cash).
    """
    top = [t for t in scored[:config.TOP_N] if t["score"] > config.SCORE_FLOOR]
    if not top:
        return {}
    excess = {t["address"]: max(t["score"] - config.SCORE_FLOOR, 0.0) for t in top}
    total_excess = sum(excess.values())
    if total_excess <= 0:
        return {}
    weights = {addr: e / total_excess * 100.0 for addr, e in excess.items()}
    # Iterative cap + redistribute.
    capped: set[str] = set()
    for _ in range(len(weights) + 1):
        over = {a for a, w in weights.items()
                if w > config.MAX_POSITION_WEIGHT_PCT and a not in capped}
        if not over:
            break
        for addr in over:
            capped.add(addr)
            weights[addr] = config.MAX_POSITION_WEIGHT_PCT
        remaining = 100.0 - sum(weights[a] for a in capped)
        free = {a: e for a, e in excess.items() if a not in capped}
        free_total = sum(free.values())
        if not free or free_total <= 0 or remaining <= 0:
            break
        for addr, e in free.items():
            weights[addr] = e / free_total * remaining
    return {addr: round(w, 4) for addr, w in weights.items() if w > 0}


def current_weights(portfolio: dict) -> dict[str, float]:
    """Current weight % per address from a portfolio dict."""
    total = portfolio.get("total_value_usd") or 0.0
    if total <= 0:
        return {}
    return {p["address"]: p["value_usd"] / total * 100.0
            for p in portfolio.get("positions", [])}


def execute_rebalance(portfolio: dict, scored: list[dict], ts: str) -> list[dict]:
    """Apply target weights to *portfolio* in place; return decisions.

    Each decision: {ts, type="rebalance", action, symbol,
    from_weight_pct, to_weight_pct, reason, score}. Actions:
    open / increase / decrease / close / hold.
    """
    targets = compute_target_weights(scored)
    by_addr = {t["address"]: t for t in scored}
    total = portfolio.get("total_value_usd") or 0.0
    if total <= 0:
        total = portfolio.get("cash_usd", config.STARTING_CASH_USD)
        portfolio["total_value_usd"] = total
    cur = current_weights(portfolio)
    positions = {p["address"]: p for p in portfolio.get("positions", [])}
    decisions: list[dict] = []

    def decide(addr: str, from_w: float, to_w: float, score: float | None,
               symbol: str, reason: str, action: str):
        decisions.append({
            "ts": ts, "type": "rebalance", "action": action,
            "symbol": symbol,
            "from_weight_pct": round(from_w, 2),
            "to_weight_pct": round(to_w, 2),
            "reason": reason,
            "score": score,
        })

    # Buys / increases / holds for target tokens.
    for addr, target_w in targets.items():
        tok = by_addr[addr]
        price = tok["price_usd"]
        from_w = cur.get(addr, 0.0)
        target_value = total * target_w / 100.0
        current_value = positions.get(addr, {}).get("value_usd", 0.0)
        trade = target_value - current_value
        if addr not in positions:
            if target_value < config.MIN_TRADE_USD:
                decide(addr, 0.0, 0.0, tok["score"], tok["symbol"],
                       f"Skipped opening {tok['symbol']}: target "
                       f"${target_value:,.0f} is below the ${config.MIN_TRADE_USD:,.0f} minimum trade.",
                       "hold")
                continue
            shares = target_value / price if price else 0.0
            positions[addr] = {"symbol": tok["symbol"], "address": addr,
                               "shares": shares, "price_usd": price,
                               "value_usd": target_value, "weight_pct": target_w}
            decide(addr, 0.0, target_w, tok["score"], tok["symbol"],
                   f"Opened {tok['symbol']} at {target_w:.1f}% of portfolio "
                   f"(score {tok['score']:.1f}, ${target_value:,.0f}).", "open")
        elif abs(target_w - from_w) < config.REBALANCE_THRESHOLD_PP:
            decide(addr, from_w, from_w, tok["score"], tok["symbol"],
                   f"Held {tok['symbol']}: target {target_w:.1f}% is within "
                   f"{config.REBALANCE_THRESHOLD_PP:.0f}pp of current {from_w:.1f}%.",
                   "hold")
        elif abs(trade) < config.MIN_TRADE_USD:
            decide(addr, from_w, from_w, tok["score"], tok["symbol"],
                   f"Held {tok['symbol']}: rebalance of ${abs(trade):,.0f} is below "
                   f"the ${config.MIN_TRADE_USD:,.0f} minimum trade.", "hold")
        else:
            action = "increase" if trade > 0 else "decrease"
            shares = target_value / price if price else 0.0
            positions[addr].update({"shares": shares, "price_usd": price,
                                    "value_usd": target_value,
                                    "weight_pct": target_w})
            decide(addr, from_w, target_w, tok["score"], tok["symbol"],
                   f"{'Increased' if trade > 0 else 'Decreased'} {tok['symbol']} "
                   f"from {from_w:.1f}% to {target_w:.1f}% "
                   f"(${abs(trade):,.0f} {'bought' if trade > 0 else 'sold'}; "
                   f"score {tok['score']:.1f}).", action)

    # Sells / closes for positions no longer in the top-10 targets.
    for addr, pos in list(positions.items()):
        if addr in targets:
            continue
        from_w = cur.get(addr, 0.0)
        tok = by_addr.get(addr)
        score = tok["score"] if tok else None
        if from_w <= 0:
            continue
        trade_value = pos.get("value_usd", 0.0)
        if trade_value < config.MIN_TRADE_USD:
            decide(addr, from_w, from_w, score, pos["symbol"],
                   f"Held {pos['symbol']}: closing ${trade_value:,.0f} is below "
                   f"the ${config.MIN_TRADE_USD:,.0f} minimum trade.", "hold")
            continue
        del positions[addr]
        decide(addr, from_w, 0.0, score, pos["symbol"],
               f"Closed {pos['symbol']}: it left the top {config.TOP_N} "
               f"(sold ${trade_value:,.0f}).", "close")

    # Recompute cash / totals from positions.
    invested = sum(p["value_usd"] for p in positions.values())
    portfolio["positions"] = sorted(
        ({**p, "weight_pct": round(p["value_usd"] / total * 100.0, 2)
          if total > 0 else 0.0} for p in positions.values()),
        key=lambda p: p["value_usd"], reverse=True)
    portfolio["cash_usd"] = round(total - invested, 2)
    portfolio["total_value_usd"] = round(
        portfolio["cash_usd"] + sum(p["value_usd"] for p in portfolio["positions"]), 2)
    return decisions


def revalue_portfolio(portfolio: dict, price_by_address: dict[str, float]) -> dict:
    """Re-price existing positions at current prices; update totals.

    Positions whose token has no current price keep their last price.
    """
    total = portfolio.get("cash_usd", 0.0)
    for pos in portfolio.get("positions", []):
        price = price_by_address.get(pos["address"].lower())
        if price:
            pos["price_usd"] = price
            pos["value_usd"] = round(pos["shares"] * price, 2)
        total += pos.get("value_usd", 0.0)
    portfolio["total_value_usd"] = round(total, 2)
    for pos in portfolio.get("positions", []):
        pos["weight_pct"] = round(pos["value_usd"] / total * 100.0, 2) if total > 0 else 0.0
    return portfolio


def new_portfolio() -> dict:
    return {"cash_usd": config.STARTING_CASH_USD,
            "total_value_usd": config.STARTING_CASH_USD, "positions": []}
