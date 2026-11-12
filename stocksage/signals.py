"""Signals: per-token feature gathering (read-only, no signing).

For each universe token:
- on-chain: totalSupply + multiplier via batched eth_call (chain.py)
- market: price / volume / liquidity / txns / pool count via DexScreener
- NAV: Chainlink latestRoundData cross-check where a feed exists (10 tokens)

Raw features are cached to data/features.json. A token with no usable
price is marked unscored with a reason — its price/score is never
fabricated.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import chain, prices

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FEATURES_CACHE = DATA_DIR / "features.json"


def gather_signals(universe_tokens: list[dict]) -> dict:
    """Gather features for every universe token.

    Returns {"tokens": [feature dicts], "unscored": [reason dicts]}.
    Feature dict: address, symbol, name, supply, multiplier,
    price_usd, price_source, liquidity_usd, volume_24h_usd,
    price_change_24h_pct, txns_24h, pool_count, low_liquidity,
    nav_usd, nav_deviation_pct, unscored_reason (None when scored).
    """
    addresses = [t["address"] for t in universe_tokens]
    onchain = {}
    try:
        onchain = chain.get_supply_and_multiplier(addresses)
    except Exception as exc:  # noqa: BLE001 - RPC down: features still gathered
        onchain = {addr.lower(): {"supply": None, "multiplier": None}
                   for addr in addresses}
        print(f"WARNING: on-chain supply/multiplier read failed: {exc}")

    dex = prices.fetch_all_prices(addresses)

    features: list[dict] = []
    unscored: list[dict] = []
    for tok in universe_tokens:
        key = tok["address"].lower()
        oc = onchain.get(key, {"supply": None, "multiplier": None})
        px = dex.get(key, {})
        price = px.get("price_usd")
        nav_check = None
        if price is not None:
            nav_check = prices.chainlink_nav_cross_check(tok["symbol"], price)
        unscored_reason = None
        if price is None:
            unscored_reason = (
                "no DexScreener pool with a usable price "
                f"({px.get('error') or 'no pools'}); price not fabricated"
            )
        elif px.get("low_liquidity"):
            # Still scored, but flagged — the score's market component
            # will be low because liquidity ranks near the bottom.
            pass
        feat = {
            "address": tok["address"],
            "symbol": tok["symbol"],
            "name": tok["name"],
            "supply": oc.get("supply") if oc.get("supply") is not None
                      else tok.get("total_supply"),
            "multiplier": oc.get("multiplier"),
            "price_usd": price,
            "price_source": px.get("price_source"),
            "liquidity_usd": px.get("liquidity_usd", 0.0),
            "volume_24h_usd": px.get("volume_24h_usd", 0.0),
            "price_change_24h_pct": px.get("price_change_24h_pct", 0.0),
            "txns_24h": px.get("txns_24h", 0),
            "pool_count": px.get("pool_count", 0),
            "low_liquidity": bool(px.get("low_liquidity")),
            "nav_usd": (nav_check or {}).get("nav_usd"),
            "nav_deviation_pct": (nav_check or {}).get("deviation_pct"),
            "unscored_reason": unscored_reason,
        }
        features.append(feat)
        if unscored_reason:
            unscored.append({"address": tok["address"], "symbol": tok["symbol"],
                             "reason": unscored_reason})
    result = {"tokens": features, "unscored": unscored}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_CACHE.write_text(json.dumps(result, indent=2))
    return result
