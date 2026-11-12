"""StockSage core — configuration.

All constants in one place. Every URL, address and selector below was
verified live on 2026-11-12 in ~/workspace/stocksage/research/research-report.md.
Do not invent tickers, contracts or prices: if a value is not here, it is
not used.
"""
from __future__ import annotations

# --- Tokenized Stocks API (Coinbase, free, no key) -------------------------
# NOTE: no trailing slash — https://api.coinbase.com/v1/tokenized-stocks/
# returns 404. The bare path (no slash) is the working endpoint.
TOKENIZED_STOCKS_API = "https://api.coinbase.com/v1/tokenized-stocks"
TOKENIZED_STOCKS_PAGE_SIZE = 500
TOKENIZED_STOCKS_CHAIN_ID = 8453  # Base

# --- Base RPC (public, no key) ---------------------------------------------
# Primary is fast; fallback is slow (~15-30 s/call from this VM).
# NEVER use https://1rpc.io/base — rate-limited (verified 2026-11-12).
RPC_PRIMARY = "https://base-rpc.publicnode.com"
RPC_FALLBACK = "https://mainnet.base.org"
RPC_URLS = [RPC_PRIMARY, RPC_FALLBACK]

# --- HTTP ------------------------------------------------------------------
HTTP_TIMEOUT = 15  # seconds, per call
HTTP_RETRIES = 1   # one retry after the first attempt
USER_AGENT = "StockSage/1.0 (paper-trading research agent; Base tokenized stocks)"

# --- Function selectors (verified live, research report §(a)) --------------
SEL_NAME = "0x06fdde03"
SEL_SYMBOL = "0x95d89b41"
SEL_DECIMALS = "0x313ce567"
SEL_TOTAL_SUPPLY = "0x18160ddd"
SEL_MULTIPLIER = "0x1b3ed722"
SEL_UI_MULTIPLIER = "0xa60bf13d"
SEL_TOTAL_SUPPLY_UI = "0x9bea6429"
SEL_LATEST_ROUND_DATA = "0xfeaf968c"  # Chainlink AggregatorV3Interface

TOKEN_DECIMALS = 8       # B20 tokens: 8 decimals
MULTIPLIER_WAD = 10 ** 18  # multiplier() is WAD (18 decimals)
CHAINLINK_DECIMALS = 8   # Chainlink stock feeds: 8 decimals

# --- Chainlink NAV feeds (docs, 10 listed; all 8 decimals) -----------------
# Symbol (without the trailing 'c') -> feed proxy address on Base.
# Only these 10 tokens have a documented Chainlink feed. Everything else
# is priced from DexScreener only; NAV is a cross-check, never a price
# source for a token without a feed.
CHAINLINK_FEEDS = {
    "AAPL": "0x787f13dEa48Db0897CbCDD985de77809D837F988",
    "AMZN": "0x06A8E4b3aBB3B7543d8396FB2B763d22820cB295",
    "GOOGL": "0x5bF49E0ffA937CE2FfF033c739aD7C634c4D34F2",
    "META": "0x6526aE6797A76123638b863AeE4dD27Ba4E4b27D",
    "MSFT": "0xeB10A6c9aa7E537aEd766C08c35Dae35B321b18c",
    "MSTR": "0xB3cE282CD188b35DA0E38D8Bc7d58e33173D202a",
    "NVDA": "0x04689a41629776563E6822F76f2e57D148d28513",
    "SNDK": "0x388b0dC46C0Fb05A74BeE0994fa5b02c6Fcca2eA",
    "SPCX": "0x6A634B235903C4ad6376892180d6fF8612e3Fa68",
    "TSLA": "0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4",
}

# --- DexScreener (public, no key) ------------------------------------------
DEXSCREENER_BASE = "https://api.dexscreener.com"
DEXSCREENER_TOKEN_PAIRS = DEXSCREENER_BASE + "/token-pairs/v1/base/{address}"
# Prices from pools with tiny liquidity are distrusted (see prices.py).
LOW_LIQUIDITY_USD = 1_000.0

# --- Scoring (research.py) --------------------------------------------------
# Final score = 0.4 * onchain + 0.3 * momentum + 0.3 * market.
# Each component is a percentile rank (0-100) within the scored universe,
# so scores are relative and explainable. Weights are visible here and
# are echoed in every scored token's output.
WEIGHT_ONCHAIN = 0.4
WEIGHT_MOMENTUM = 0.3
WEIGHT_MARKET = 0.3
# Momentum uses the 24h price change clipped to this band before ranking,
# so one parabolic token cannot stretch the whole scale.
MOMENTUM_CLIP_PCT = 20.0

# --- Paper portfolio (portfolio.py) -----------------------------------------
STARTING_CASH_USD = 100_000.0  # paper only — no real funds, never signed
TOP_N = 10                     # hold at most the top 10 scored tokens
MAX_POSITION_WEIGHT_PCT = 25.0  # cap per position
MIN_TRADE_USD = 500.0          # ignore rebalances smaller than this
REBALANCE_THRESHOLD_PP = 5.0   # rebalance only if |target - current| >= 5 pp
SCORE_FLOOR = 50.0             # only scores above this earn weight

# --- Agent ------------------------------------------------------------------
UNIVERSE_STALE_SECONDS = 6 * 3600  # refresh universe if cache older than 6h
