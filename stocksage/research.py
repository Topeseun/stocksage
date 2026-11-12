"""Research: transparent, explainable scoring. No black box.

Formula (visible here and in every output):
    score = 0.4 * onchain + 0.3 * momentum + 0.3 * market
Each component is a percentile rank (0-100) within the scored universe:

- onchain activity  = mean( percentile(volume_24h_usd),
                            percentile(txns_24h) )
  gated on supply > 0 (universe tokens are minted, so this holds; a
  token with supply <= 0 scores 0 on this component).
- momentum         = percentile( clip(price_change_24h_pct, -20, +20) )
  Clipping stops one parabolic token stretching the whole scale.
- market/tradability = mean( percentile(liquidity_usd),
                             percentile(pool_count) )

Percentile rank used: (count_below + 0.5 * count_equal) / n * 100.
Every scored token carries its component values and 1-3 plain-language
reasons. Tokens without a price are unscored (see signals.py) and are
never given a fabricated score.
"""
from __future__ import annotations

from . import config


def percentile_rank(values: list[float], value: float) -> float:
    """Percentile rank of *value* within *values* (0-100)."""
    n = len(values)
    if n == 0:
        return 0.0
    if n == 1:
        return 50.0
    below = sum(1 for v in values if v < value)
    equal = sum(1 for v in values if v == value)
    return (below + 0.5 * equal) / n * 100.0


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _fmt_usd(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}k"
    return f"${value:.0f}"


def build_reasons(feat: dict, comp: dict, ranks: dict) -> list[str]:
    """1-3 plain-language reasons for a token's score."""
    reasons: list[str] = []
    vol = feat.get("volume_24h_usd") or 0.0
    txns = feat.get("txns_24h") or 0
    liq = feat.get("liquidity_usd") or 0.0
    chg = feat.get("price_change_24h_pct") or 0.0
    pools = feat.get("pool_count") or 0

    if ranks.get("volume", 0) >= 75:
        reasons.append(f"Top-quartile 24h volume ({_fmt_usd(vol)}) with {txns:,} trades")
    elif ranks.get("volume", 0) >= 50:
        reasons.append(f"Above-median 24h volume ({_fmt_usd(vol)})")
    if chg >= 5:
        reasons.append(f"Strong 24h momentum (+{chg:.1f}%)")
    elif chg <= -5:
        reasons.append(f"Weak 24h momentum ({chg:.1f}%) — drags the score down")
    if ranks.get("liquidity", 0) >= 75:
        reasons.append(f"Deep liquidity ({_fmt_usd(liq)} across {pools} pool(s)) — easy to trade")
    elif liq < config.LOW_LIQUIDITY_USD:
        reasons.append("Thin liquidity — price may be unreliable, trade with care")
    if feat.get("nav_deviation_pct") is not None:
        dev = feat["nav_deviation_pct"]
        if abs(dev) <= 1.0:
            reasons.append(f"DEX price tracks Chainlink NAV within {abs(dev):.2f}%")
        elif abs(dev) > 5.0:
            reasons.append(f"DEX price deviates {dev:+.1f}% from Chainlink NAV — check before trusting it")
    if not reasons:
        reasons.append("Mid-pack on volume, momentum and liquidity — no standout signal")
    return reasons[:3]


def score_tokens(features: list[dict]) -> list[dict]:
    """Score every priced feature dict; returns scored tokens sorted desc.

    Output dict per token: address, symbol, name, score,
    components {onchain, momentum, market}, price_usd, price_source,
    liquidity_usd, volume_24h_usd, supply, multiplier, reasons.
    """
    scored = [f for f in features if f.get("price_usd") is not None]
    if not scored:
        return []
    vols = [f.get("volume_24h_usd") or 0.0 for f in scored]
    txnss = [float(f.get("txns_24h") or 0) for f in scored]
    changes = [_clip(f.get("price_change_24h_pct") or 0.0,
                     -config.MOMENTUM_CLIP_PCT, config.MOMENTUM_CLIP_PCT)
               for f in scored]
    liqs = [f.get("liquidity_usd") or 0.0 for f in scored]
    pools = [float(f.get("pool_count") or 0) for f in scored]

    out: list[dict] = []
    for feat, chg in zip(scored, changes):
        vol_rank = percentile_rank(vols, feat.get("volume_24h_usd") or 0.0)
        txn_rank = percentile_rank(txnss, float(feat.get("txns_24h") or 0))
        liq_rank = percentile_rank(liqs, feat.get("liquidity_usd") or 0.0)
        pool_rank = percentile_rank(pools, float(feat.get("pool_count") or 0))
        mom_rank = percentile_rank(changes, chg)
        supply = feat.get("supply") or 0.0
        onchain = round((vol_rank + txn_rank) / 2.0, 2) if supply and supply > 0 else 0.0
        momentum = round(mom_rank, 2)
        market = round((liq_rank + pool_rank) / 2.0, 2)
        score = round(
            config.WEIGHT_ONCHAIN * onchain
            + config.WEIGHT_MOMENTUM * momentum
            + config.WEIGHT_MARKET * market, 2)
        score = max(0.0, min(100.0, score))
        components = {"onchain": onchain, "momentum": momentum, "market": market}
        ranks = {"volume": vol_rank, "liquidity": liq_rank}
        out.append({
            "address": feat["address"],
            "symbol": feat["symbol"],
            "name": feat["name"],
            "score": score,
            "components": components,
            "price_usd": feat["price_usd"],
            "price_source": feat["price_source"],
            "liquidity_usd": feat.get("liquidity_usd") or 0.0,
            "volume_24h_usd": feat.get("volume_24h_usd") or 0.0,
            "supply": supply,
            "multiplier": feat.get("multiplier"),
            "reasons": build_reasons(feat, components, ranks),
        })
    out.sort(key=lambda t: t["score"], reverse=True)
    return out
