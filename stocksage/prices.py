"""Prices: DexScreener (primary) + Chainlink NAV (cross-check, 10 feeds only).

DexScreener public API, no key: GET /token-pairs/v1/base/{address}
returns every pool for a token. We pick the deepest pool by
liquidity_usd and ALWAYS record liquidity_usd — prices from pools with
tiny liquidity are distrusted (flagged low_liquidity, never silently
trusted). BaseScan/Etherscan API is NOT used (not free for Base).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from . import chain, config


def _http_get_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    last_exc: Exception | None = None
    for _ in range(config.HTTP_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=config.HTTP_TIMEOUT) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
    raise RuntimeError(f"GET {url} failed: {last_exc}")


def _safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def pick_deepest_pool(pairs: list[dict]) -> dict | None:
    """Pick the pool with the highest liquidity.usd (None if none usable)."""
    best = None
    best_liq = -1.0
    for pair in pairs or []:
        price = _safe_float((pair or {}).get("priceUsd"), 0.0)
        if price <= 0:
            continue
        liq = _safe_float(((pair or {}).get("liquidity") or {}).get("usd"), 0.0)
        if liq > best_liq:
            best_liq = liq
            best = pair
    return best


def fetch_token_price(address: str) -> dict:
    """DexScreener price for one token address.

    Returns {price_usd, price_source, liquidity_usd, volume_24h_usd,
    price_change_24h_pct, txns_24h, pool_count, low_liquidity, error}.
    price_usd is None when no usable pool exists — never fabricated.
    """
    url = config.DEXSCREENER_TOKEN_PAIRS.format(address=address)
    try:
        pairs = _http_get_json(url)
    except Exception as exc:  # noqa: BLE001 - network failure -> no price
        return {"price_usd": None, "price_source": None, "liquidity_usd": 0.0,
                "volume_24h_usd": 0.0, "price_change_24h_pct": 0.0,
                "txns_24h": 0, "pool_count": 0, "low_liquidity": True,
                "error": str(exc)}
    if not isinstance(pairs, list):
        pairs = []
    best = pick_deepest_pool(pairs)
    if best is None:
        return {"price_usd": None, "price_source": None, "liquidity_usd": 0.0,
                "volume_24h_usd": 0.0, "price_change_24h_pct": 0.0,
                "txns_24h": 0, "pool_count": len(pairs),
                "low_liquidity": True, "error": "no DexScreener pool with a price"}
    volume = (best.get("volume") or {}).get("h24")
    txns = (best.get("txns") or {}).get("h24") or {}
    price_change = (best.get("priceChange") or {}).get("h24")
    liquidity = _safe_float((best.get("liquidity") or {}).get("usd"), 0.0)
    return {
        "price_usd": _safe_float(best.get("priceUsd")),
        "price_source": f"dexscreener:{best.get('dexId')}:{best.get('pairAddress')}",
        "liquidity_usd": liquidity,
        "volume_24h_usd": _safe_float(volume, 0.0),
        "price_change_24h_pct": _safe_float(price_change, 0.0),
        "txns_24h": int(_safe_float(txns.get("buys"), 0.0)
                         + _safe_float(txns.get("sells"), 0.0)),
        "pool_count": len(pairs),
        "low_liquidity": liquidity < config.LOW_LIQUIDITY_USD,
        "error": None,
    }


def fetch_all_prices(addresses: list[str], max_workers: int = 8) -> dict[str, dict]:
    """DexScreener prices for many tokens (threaded, stdlib only)."""
    out: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for addr, result in zip(addresses, pool.map(fetch_token_price, addresses)):
            out[addr.lower()] = result
    return out


def chainlink_nav_cross_check(symbol: str, dex_price: float | None) -> dict | None:
    """Chainlink NAV vs DexScreener price for the 10 feed tokens.

    Returns {"nav_usd", "dex_price_usd", "deviation_pct", "updated_at",
    "feed"} or None when no feed exists / the feed call fails.
    """
    base_symbol = (symbol or "").removesuffix("c")
    nav = chain.get_chainlink_nav(base_symbol)
    if nav is None or dex_price is None or dex_price <= 0:
        return None
    deviation = (dex_price - nav["nav_usd"]) / nav["nav_usd"] * 100.0 \
        if nav["nav_usd"] else None
    return {
        "nav_usd": nav["nav_usd"],
        "dex_price_usd": dex_price,
        "deviation_pct": deviation,
        "updated_at": nav["updated_at"],
        "feed": nav["feed"],
    }
