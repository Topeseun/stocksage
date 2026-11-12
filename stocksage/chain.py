"""Minimal JSON-RPC client for Base over urllib (stdlib only).

Read-only: eth_call / eth_getCode / eth_chainId only. Never signs, never
sends a transaction. Primary RPC with fallback, one retry, 15 s timeout.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from . import config

# ---------------------------------------------------------------- helpers --

def _post(url: str, payload) -> object:
    """POST JSON to *url* with one retry. Raises on failure."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": config.USER_AGENT},
        method="POST",
    )
    last_exc: Exception | None = None
    for _ in range(config.HTTP_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=config.HTTP_TIMEOUT) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
    raise RuntimeError(f"RPC request to {url} failed: {last_exc}")


def _rpc_call(payload, method_name: str):
    """Try each RPC URL in order; raise RuntimeError if all fail."""
    errors = []
    for url in config.RPC_URLS:
        try:
            result = _post(url, payload)
            if isinstance(result, dict) and "error" in result:
                errors.append(f"{url}: {result['error']}")
                continue
            return result
        except Exception as exc:  # noqa: BLE001 - try next RPC
            errors.append(f"{url}: {exc}")
    raise RuntimeError(f"{method_name} failed on all RPCs: {'; '.join(errors)}")


# ------------------------------------------------------------------ calls --

def eth_call(to_address: str, data: str, block: str = "latest") -> str:
    """Single eth_call. Returns the raw hex result string."""
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": to_address, "data": data}, block],
    }
    result = _rpc_call(payload, "eth_call")
    return result["result"]


def batch_eth_call(calls: list[tuple[str, str]]) -> list[str | None]:
    """Batch eth_call: list of (to_address, data) -> list of raw hex results.

    A failed / reverted entry yields None at that position instead of
    aborting the whole batch. Falls back to one-by-one calls if the
    endpoint rejects the batch.
    """
    if not calls:
        return []
    payload = [
        {"jsonrpc": "2.0", "id": i, "method": "eth_call",
         "params": [{"to": to, "data": data}, "latest"]}
        for i, (to, data) in enumerate(calls)
    ]
    try:
        results = _rpc_call(payload, "batch eth_call")
    except Exception:
        # Batch unsupported — degrade to individual calls.
        out: list[str | None] = []
        for to, data in calls:
            try:
                out.append(eth_call(to, data))
            except Exception:
                out.append(None)
        return out
    if not isinstance(results, list):
        # Server answered a single object (not a batch) — retry individually.
        return batch_eth_call_fallback(calls)
    by_id: dict[int, str | None] = {}
    for item in results:
        if isinstance(item, dict) and "result" in item:
            by_id[item.get("id", 0)] = item["result"]
        elif isinstance(item, dict):
            by_id[item.get("id", 0)] = None
    return [by_id.get(i) for i in range(len(calls))]


def batch_eth_call_fallback(calls: list[tuple[str, str]]) -> list[str | None]:
    out: list[str | None] = []
    for to, data in calls:
        try:
            out.append(eth_call(to, data))
        except Exception:
            out.append(None)
    return out


def eth_get_code(address: str) -> str:
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
        "params": [address, "latest"],
    }
    return _rpc_call(payload, "eth_getCode")["result"]


def eth_chain_id() -> int:
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}
    return int(_rpc_call(payload, "eth_chainId")["result"], 16)


# -------------------------------------------------------------- decoding --

def decode_uint256(hex_result: str | None) -> int | None:
    """Decode a uint256 return value; None if missing/invalid."""
    if not hex_result or not isinstance(hex_result, str):
        return None
    try:
        return int(hex_result, 16)
    except ValueError:
        return None


def decode_string(hex_result: str | None) -> str | None:
    """Decode an ABI-encoded string return value; None if invalid."""
    if not hex_result or not isinstance(hex_result, str):
        return None
    try:
        raw = bytes.fromhex(hex_result[2:] if hex_result.startswith("0x") else hex_result)
    except ValueError:
        return None
    if len(raw) < 64:
        return None
    try:
        length = int.from_bytes(raw[32:64], "big")
        text = raw[64:64 + length].decode("utf-8")
        return text or None
    except (ValueError, UnicodeDecodeError):
        return None


def decode_latest_round_data(hex_result: str | None) -> dict | None:
    """Decode Chainlink latestRoundData() -> {round_id, answer, updated_at}.

    Returns (roundId uint80, answer int256, startedAt, updatedAt,
    answeredInRound uint80) — 5 x 32-byte words. answer has 8 decimals.
    """
    if not hex_result or not isinstance(hex_result, str):
        return None
    try:
        raw = bytes.fromhex(hex_result[2:] if hex_result.startswith("0x") else hex_result)
    except ValueError:
        return None
    if len(raw) < 160:
        return None
    round_id = int.from_bytes(raw[0:32], "big")
    answer_raw = int.from_bytes(raw[32:64], "big", signed=True)
    updated_at = int.from_bytes(raw[96:128], "big")
    return {
        "round_id": round_id,
        "answer": answer_raw / (10 ** config.CHAINLINK_DECIMALS),
        "answer_raw": answer_raw,
        "updated_at": updated_at,
    }


# ----------------------------------------------------------- token reads --

def get_supply_and_multiplier(addresses: list[str]) -> dict[str, dict]:
    """Batch-read totalSupply() + multiplier() for each token address.

    Returns {lowercase_address: {"supply": float|None, "multiplier": float|None}}.
    supply is in whole tokens (8 decimals); multiplier is the WAD value
    as a float (1.0 = no split/dividend adjustment).
    """
    calls: list[tuple[str, str]] = []
    for addr in addresses:
        calls.append((addr, config.SEL_TOTAL_SUPPLY))
        calls.append((addr, config.SEL_MULTIPLIER))
    results = batch_eth_call(calls)
    out: dict[str, dict] = {}
    for i, addr in enumerate(addresses):
        supply_raw = decode_uint256(results[2 * i])
        mult_raw = decode_uint256(results[2 * i + 1])
        out[addr.lower()] = {
            "supply": (supply_raw / (10 ** config.TOKEN_DECIMALS)
                       if supply_raw is not None else None),
            "multiplier": (mult_raw / config.MULTIPLIER_WAD
                           if mult_raw is not None else None),
        }
    return out


def get_token_meta(address: str) -> dict:
    """Read name()/symbol()/decimals() for one token (best effort)."""
    results = batch_eth_call([
        (address, config.SEL_NAME),
        (address, config.SEL_SYMBOL),
        (address, config.SEL_DECIMALS),
    ])
    return {
        "name": decode_string(results[0]),
        "symbol": decode_string(results[1]),
        "decimals": decode_uint256(results[2]),
    }


def get_chainlink_nav(symbol: str) -> dict | None:
    """Chainlink latestRoundData for a token symbol (without trailing 'c').

    Returns {"nav_usd", "updated_at", "round_id", "feed"} or None when
    there is no documented feed for the symbol or the call fails.
    Feeds are 24/5 and freeze on weekends/holidays — check updated_at.
    """
    feed = config.CHAINLINK_FEEDS.get(symbol.upper())
    if not feed:
        return None
    try:
        raw = eth_call(feed, config.SEL_LATEST_ROUND_DATA)
    except Exception:
        return None
    decoded = decode_latest_round_data(raw)
    if decoded is None:
        return None
    return {
        "nav_usd": decoded["answer"],
        "updated_at": decoded["updated_at"],
        "round_id": decoded["round_id"],
        "feed": feed,
    }
