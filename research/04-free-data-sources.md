# 04 — Free data sources for prices & DEX activity on Base (no key)

All verified live from this VM on 2026-11-12 unless stated.

## 1. Tokenized Stocks API (Coinbase) — primary reference data
- `https://api.coinbase.com/v1/tokenized-stocks` — no key, read-only.
- List / chains / total-supply (bare number) / metadata / prospectuses / corporate-actions. See `01-tokenized-stocks-api.md` and §(b) of the main report for exact endpoints + captured responses.
- Gaps: NAV for only 12/338 tokens; no wallet/position data; no DEX prices.

## 2. Public Base RPC — on-chain reads
- `https://base-rpc.publicnode.com` (fast, recommended) and `https://mainnet.base.org` (works, slow ~15–30 s/call here). `https://1rpc.io/base` FAILED (usage-limit error).
- `eth_call`: name/symbol/decimals/totalSupply/multiplier/balanceOfUI/totalSupplyUI; Chainlink `latestRoundData()`; `eth_getLogs` for `B20Created`, `UIMultiplierUpdated`, `Announcement`, Transfer events.

## 3. DexScreener public API — `https://api.dexscreener.com` — VERIFIED
- No key, no signup. Limits: ~300 req/min (pair/token/search), 60 req/min (profiles/boosts).
- Endpoints: `GET /token-pairs/v1/base/{tokenAddress}`; `GET /tokens/v1/base/{addr1,addr2…}` (≤30); `GET /latest/dex/search?q=`; `GET /latest/dex/pairs/base/{pairAddress}`.
- Verified: TSLAc → Uniswap v4 USDC pair `0x342af3dc…`, priceUsd 391.94 (≈ NAV 391.9975), liquidity $33,724.72, vol24h $11,930.8, txns h24 143 buys / 148 sells. NVDAc → 30 pairs; top Aerodrome `0xF668e21993…`, priceUsd 165.043, liquidity $1,303,058, vol24h $10,177,386, txns h24 6,066 buys / 6,052 sells.
- Limits: current state only — no historical candles, no trade feed, no WebSocket; search max ~30 results. Thin liquidity on many stock tokens — always check `liquidity.usd` before trusting a price.

## 4. BaseScan — web OK, API NOT free for Base
- Token page `https://basescan.org/token/<addr>` → HTTP 200 (but B20 precompiles show no contract/bytecode — expected, not an error).
- `api.basescan.org` V1 without key → "deprecated V1 endpoint, switch to Etherscan API V2". Etherscan V2 without key for Base (chainId 8453) → "Free API access is not supported for this chain. Please upgrade your api plan." **Do not build on BaseScan/Etherscan API.** Use RPC `eth_getLogs` for history instead.

## 5. Not verified in this pass (do not assume)
- **0x Swap API** (docs' recommended trading route): key requirement / free tier not checked.
- Direct Uniswap/Aerodrome router addresses + quoting for B20 swaps: not checked.
- CoinGecko / CoinMarketCap free tiers: not checked (docs list them as off-chain price options; both now generally require a key even on free tiers — verify before use).
- CDP Trade API: third-party docs (Ozmium) say it does NOT quote B20 tokens — lead only, not verified.
