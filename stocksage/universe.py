"""Universe: the list of real, minted tokenized stocks on Base.

Source of truth is the Coinbase Tokenized Stocks API (free, no key).
Only tokens with total_supply present and > 0 are kept — the other ~266
registered records have nothing to trade.

Duplicate-address guard (research report §(e) item 6): the captured dump
showed SONYc/SOUNc, PLTRc/MRVLc and BIRDc/BIDUc sharing addresses. A
re-pull with page_size=500 on 2026-11-12 resolved all three — each symbol
now has its own address and there are no duplicate addresses in the live
API (338 records, 72 minted). The guard stays in the code anyway: any
row whose contract address is duplicated across two symbols is DROPPED
and logged, never used, until a re-pull resolves it.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

logger = logging.getLogger("stocksage.universe")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
UNIVERSE_CACHE = DATA_DIR / "universe.json"


def _http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    last_exc: Exception | None = None
    for _ in range(config.HTTP_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=config.HTTP_TIMEOUT) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
    raise RuntimeError(f"GET {url} failed: {last_exc}")


def fetch_all_tokens() -> list[dict]:
    """Fetch every page of the Tokenized Stocks API (page_size=500)."""
    tokens: list[dict] = []
    page_token: str | None = None
    while True:
        params = {"page_size": config.TOKENIZED_STOCKS_PAGE_SIZE}
        if page_token:
            params["page_token"] = page_token
        url = config.TOKENIZED_STOCKS_API + "?" + urllib.parse.urlencode(params)
        page = _http_get_json(url)
        tokens.extend(page.get("tokens") or [])
        page_token = page.get("next_page_token")
        if not page_token:
            break
    return tokens


def build_universe(raw_tokens: list[dict]) -> tuple[list[dict], list[dict]]:
    """Filter to minted tokens, dedupe by address, drop duplicates.

    Returns (minted_tokens, dropped_rows). A row is dropped when:
    - it has no contract address, or
    - its address (case-insensitive) is shared by two different symbols
      (duplicate-address guard — see module docstring), or
    - total_supply is missing / <= 0 (unminted: nothing to trade).
    Kept rows are normalised to {address, symbol, name, total_supply,
    multiplier, nav_price, first_mint_date}.
    """
    dropped: list[dict] = []

    # First pass: group by lower-cased address to find duplicates.
    by_address: dict[str, list[dict]] = {}
    for tok in raw_tokens:
        addr = (tok.get("contract_address") or "").strip()
        if not addr:
            dropped.append({**tok, "drop_reason": "missing contract_address"})
            continue
        by_address.setdefault(addr.lower(), []).append(tok)

    duplicate_addresses = {
        addr for addr, rows in by_address.items() if len(rows) > 1
    }
    # A duplicate address shared by the SAME symbol twice is a harmless
    # pagination repeat; only cross-symbol sharing is a data problem.
    for addr in list(duplicate_addresses):
        symbols = {r.get("symbol") for r in by_address[addr]}
        if len(symbols) <= 1:
            duplicate_addresses.discard(addr)

    minted: list[dict] = []
    seen: set[str] = set()
    for tok in raw_tokens:
        addr = (tok.get("contract_address") or "").strip()
        if not addr:
            continue
        key = addr.lower()
        if key in duplicate_addresses:
            dropped.append({
                "symbol": tok.get("symbol"), "address": addr,
                "drop_reason": (
                    "duplicate contract address shared across symbols "
                    f"({sorted({r.get('symbol') for r in by_address[key]})}); "
                    "dropped until a re-pull resolves it"
                ),
            })
            continue
        if key in seen:
            continue  # exact pagination repeat of the same token
        seen.add(key)
        supply = tok.get("total_supply")
        if supply is None:
            continue  # unminted — not dropped, just not in the universe
        try:
            supply_f = float(supply)
        except (TypeError, ValueError):
            dropped.append({"symbol": tok.get("symbol"), "address": addr,
                            "drop_reason": "total_supply not numeric"})
            continue
        if supply_f <= 0:
            continue  # unminted / burned to zero
        minted.append({
            "address": addr,
            "symbol": tok.get("symbol"),
            "name": tok.get("name"),
            "total_supply": supply_f,
            "multiplier": tok.get("multiplier"),
            "nav_price": tok.get("nav_price"),
            "first_mint_date": tok.get("first_mint_date"),
        })
    minted.sort(key=lambda t: (t["symbol"] or ""))
    return minted, dropped


def fetch_universe(refresh: bool = False) -> dict:
    """Return {"count", "minted", "tokens", "dropped"}.

    Uses the on-disk cache unless refresh=True or the cache is missing.
    Cache lives at data/universe.json.
    """
    if not refresh and UNIVERSE_CACHE.exists():
        try:
            cached = json.loads(UNIVERSE_CACHE.read_text())
            if cached.get("tokens"):
                return cached
        except (json.JSONDecodeError, OSError):
            pass
    raw = fetch_all_tokens()
    minted, dropped = build_universe(raw)
    result = {
        "count": len(raw),
        "minted": len(minted),
        "tokens": minted,
        "dropped": dropped,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UNIVERSE_CACHE.write_text(json.dumps(result, indent=2))
    for row in dropped:
        logger.warning("Dropped token %s (%s): %s",
                       row.get("symbol"), row.get("address"),
                       row.get("drop_reason"))
    return result
