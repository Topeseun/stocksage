# StockSage — Research Report

**Date:** 2026-11-12 (all live checks run ~17:57–18:10 WAT / 16:57–17:10 UTC)
**Scope:** Base tokenized stocks (Coinbase B20), Stocks Maxxing quest rules, free data sources, Bankr.
**Method:** Official docs read via browser; every API/RPC claim below was actually called from this VM (no API key used anywhere). Raw evidence in this folder: `all-tokens.json` (full API dump, 338 tokens), `minted.csv` (72 minted), `rpc-evidence.json`, `quest.html` / `quest-text.txt` (raw Quest Page HTML + extracted text).
**No product code was written.**

---

## (a) Verified list of real tokenized stocks on Base

### What a "tokenized stock" is on Base — read this first, it changes everything

- Coinbase tokenized stocks are **B20 tokens**: ERC-20-compatible, **8 decimals**, 1 token ≈ 1 share × an on-chain `multiplier()` (WAD, 18 decimals) that absorbs dividends/splits. Secondary trading is permissionless; mint/redeem is restricted to Authorized Participants.
- **B20 tokens are Base-native precompiles, NOT separately deployed contracts.** Docs (`list-tokenized-stocks`): *"there is no per-asset contract and no per-address verified contract on Basescan (precompiles hold no bytecode)."* Verified live: `eth_getCode(TSLAc)` returned `0xef` (precompile marker, not contract bytecode). **Do not expect Basescan verification, source code, or a deployer — that is normal for B20.**
- All token addresses share the pattern `0xB20000…` (case-insensitive; the API returns mixed-case checksummed addresses).
- **Identify tokens by contract address, never by symbol** — name/symbol are mutable on-chain (`updateName`/`updateSymbol`).
- Only available to persons in eligible jurisdictions **outside the U.S.** (docs disclaimer, repeated on Quest Page).

### The authoritative source: Tokenized Stocks API

- **Base URL (verified live, no key): `https://api.coinbase.com/v1/tokenized-stocks`**
- Read-only, no API key. Pagination: `page_size` default 100, max 500; follow `next_page_token` as `page_token`.
- **Live count on 2026-11-12: 338 token records returned. Only 72 have ever been minted** (`first_mint_date` present + `total_supply` present). **The other 266 are registered records with zero supply** — they exist in the API but there is nothing to trade. Verified live: unminted `AALc` returns `name() = "American Airlines Group Inc."` on-chain but `totalSupply() = 0`.
- `nav_price` is present for only **12** tokens (Chainlink-based NAV/reference value, NOT a live bid/ask). Most minted tokens have no `nav_price` in the API — use the Chainlink feed or DexScreener for price instead.
- `multiplier` ≠ 1 for 9 tokens (see table). Largest: `PMc` 1.558821201905387 (a split/dividend history), `SANc` 1.0105710788687274.

### Minted tokens (72) — verified against the live API 2026-11-12

Supply / NAV are point-in-time values (supply moves — NVDA supply rose ~109 tokens in ~5 min between two reads during this research). Full machine-readable table: `minted.csv`; full 338-token dump: `all-tokens.json`.

| Symbol | Contract address | Supply (tokens) | NAV $ (if in API) | Multiplier | First mint |
|---|---|---|---|---|---|
| AAOIc | 0xb2000000000000000000000d46361d597f543d06 | — (see note) | — | 1 | 2026-10-26 |
| AAPLc | 0xB2000000000000000000003eF37a7c863DC1482A | — | — | 1 | 2026-10-09 |
| AMCc | 0xb2000000000000000000001dFD8c413Ecd6EC630 | — | — | 1 | 2026-09-29 |
| AMDc | 0xB2000000000000000000000d8Ce462E99ee7A47B | 989.92 | — | 1 | 2026-09-28 |
| AMZNc | 0xB2000000000000000000002C8b0e3d7Ff26f81a0 | — | — | 1 | 2026-10-09 |
| APPc | 0xB20000000000000000000006f910a0e7BBD3c168 | 106.00 | — | 1 | 2026-10-23 |
| ARMc | 0xB20000000000000000000026215D755356E5043f | 255.50 | — | 1 | 2026-10-09 |
| ASTSc | 0xb2000000000000000000002Cd78D7C981e97c330 | — | — | 1 | 2026-10-09 |
| AVGOc | 0xb2000000000000000000007Cbdf8fa3861E51721 | — | — | 1 | 2026-09-28 |
| BEc | 0xB20000000000000000000016f9dfe862feBA122b | 1,253.77 | — | 1 | 2026-09-28 |
| BIDUc | 0xB200000000000000000000535fE96f18204BFD96 | — | — | 1 | 2026-10-06 |
| BILIc | 0xb2000000000000000000001b6e407239EB31EDCf | — | — | 1 | 2026-10-09 |
| BIRDc | 0xB200000000000000000000535fE96f18204BFD96 | 1.00 | — | 1 | 2026-10-06 |
| BMNRc | 0xb2000000000000000000008c1bAD82Fa061F818a | — | — | 1 | 2026-10-09 |
| BUDc | 0xB200000000000000000000747BFfA52Fe2C2510B | — | — | 1 | 2026-10-09 |
| CAKEc | 0xb2000000000000000000003bd46dbdE905508B16 | — | — | 1 | 2026-10-09 |
| CBRSc | 0xB200000000000000000000720133EeDF525f93E2 | 93.38 | — | 1 | 2026-10-23 |
| CRCLc | 0xB20000000000000000000019f6E7C675b73C2e4D | 2,087.98 | 64.7625 | 1 | 2026-10-26 |
| CRWVc | 0xb20000000000000000000055e63C4c1cDC6b7A36 | — | — | 1 | 2026-10-09 |
| DJTc | 0xb200000000000000000000428E3a3eebBb20692B | 9,780.91 | — | 1 | 2026-09-24 |
| DUOLc | 0xb20000000000000000000005bEFA57b9B871E737 | — | — | 1 | 2026-10-09 |
| GMEc | 0xb2000000000000000000007790ed6E48e06eD935 | 1,990.01 | — | 1 | 2026-09-24 |
| GOOGLc | 0xb2000000000000000000002D0BA3164cc74f58B7 | 34,832.61 | 301.6237 | 1.0003771186767842 | 2026-08-12 |
| HIMSc | 0xB20000000000000000000043a599976181Bcf336 | 15,935.88 | — | 1 | 2026-09-28 |
| HOODc | 0xb2000000000000000000006F944897540579D3f2 | 1,475.99 | — | 1 | 2026-11-10 |
| HSAIc | 0xB2000000000000000000006b7f6966EE0453E251 | — | — | 1 | 2026-10-09 |
| HTZc | 0xB2000000000000000000002601C5C94F435da168 | 225.72 | — | 1 | 2026-09-24 |
| INFYc | 0xb2000000000000000000002C99976e240eD773E6 | — | — | 1 | 2026-10-09 |
| INTCc | 0xB2000000000000000000004AFF16039bA04bdFBc | 2,326.86 | 61.963 | 1 | 2026-10-26 |
| LITEc | 0xB20000000000000000000034975347FF1848AAb9 | — | — | 1 | 2026-10-09 |
| LIc | 0xb2000000000000000000003963C3bEAA3eba9bfc | — | — | 1 | 2026-10-09 |
| LLYc | 0xb20000000000000000000053d000bAC95662D1e4 | — | — | 1 | 2026-10-09 |
| METAc | 0xb2000000000000000000008bC8786B856E61707C | 8,783.39 | 624.7835 | 1.0003137922895982 | 2026-08-12 |
| MRNAc | 0xb200000000000000000000241fe94fe97FcBf034 | — | — | 1 | 2026-10-09 |
| MRVLc | 0xb2000000000000000000007d16372840dF4dAbbe | 2,757.10 | — | 1.0000018650482796 | 2026-09-24 |
| MSFTc | 0xb2000000000000000000005672D78eFF30D24665 | — | — | 1 | 2026-10-09 |
| MSTRc | 0xb2000000000000000000004884b426556b92883d | 19,309.98 | 117.2075 | 1 | 2026-09-03 |
| MUc | 0xB2000000000000000000003958003d801724F9d3 | — | — | 1.0001006811764792 | 2026-10-09 |
| NFLXc | 0xb20000000000000000000058B8c947e44011dFE6 | 7,676.59 | — | 1 | 2026-09-24 |
| NIOc | 0xb2000000000000000000002D2B5dc53c61f1bA06 | 15,319.00 | — | 1 | 2026-10-09 |
| NOKc | 0xb2000000000000000000005ac674f707E357409c | 5,799.00 | — | 1.0019604756256093 | 2026-10-09 |
| NVAXc | 0xb2000000000000000000006BC65AF32d24870A2d | — | — | 1 | 2026-10-09 |
| NVDAc | 0xb20000000000000000000078ee7ce2fE4908108C | 46,822.04 | 165.53 | 1.0005379395763694 | 2026-08-12 |
| NVOc | 0xb2000000000000000000008D5328e9208773dC58 | 818.00 | — | 1 | 2026-10-09 |
| ORCLc | 0xb200000000000000000000347AFbA223D7B6b63C | 3,003.20 | — | 1.0000399883233386 | 2026-09-28 |
| PDDc | 0xB2000000000000000000006d1bC7Faa266Eb099D | — | — | 1 | 2026-10-09 |
| PFEc | 0xB20000000000000000000018FE7eC7d6DfeeB528 | 9.87 | — | 1 | 2026-09-29 |
| PLTRc | 0xb2000000000000000000007d16372840dF4dAbbe | 2,757.10 | — | 1 | 2026-09-24 |
| PMc | 0xB2000000000000000000008FC2A8C23cf5937b66 | 0.25 | — | 1.558821201905387 | 2026-09-29 |
| PTONc | 0xb2000000000000000000003Fa80315bFd87eFed8 | — | — | 1 | 2026-10-09 |
| PYPLc | 0xb200000000000000000000450ad3abE5d4846c6E | 161.07 | — | 1 | 2026-09-29 |
| QUBTc | 0xb2000000000000000000000Cd31253817b36f88a | — | — | 1 | 2026-10-09 |
| RBLXc | 0xB2000000000000000000005bd7AE89b9E6189Bb5 | 73.40 | — | 1 | 2026-09-28 |
| RDDTc | 0xb20000000000000000000066242d4067724cB7A1 | 651.80 | — | 1 | 2026-09-24 |
| RIVNc | 0xb2000000000000000000003e4249C65bd6c037d9 | 2,232.43 | — | 1 | 2026-10-23 |
| RKLBc | 0xb200000000000000000000252C42b75F49DacF59 | — | — | 1 | 2026-10-09 |
| SANc | 0xB20000000000000000000017BB66E9301E913A99 | 2,491.00 | — | 1.0105710788687274 | 2026-10-09 |
| SAPc | 0xB200000000000000000000349ef3Aa93a0897476 | — | — | 1 | 2026-10-09 |
| SEc | 0xB2000000000000000000003088798F6d0722AaAC | 447.00 | — | 1 | 2026-10-09 |
| SKHYc | 0xb200000000000000000000187f7071D6E321a7d2 | 2,287.70 | — | 1 | 2026-10-09 |
| SNDKc | 0xb200000000000000000000397293Cb8cda9a10c5 | 2,099.95 | 948.5575 | 1 | 2026-09-03 |
| SONYc | 0xB2000000000000000000002137743D4a01Fe4e88 | 3.93 | — | 1 | 2026-10-09 |
| SOUNc | 0xB2000000000000000000002137743D4a01Fe4e88 | 3.93 | — | 1 | 2026-09-29 |
| SPCXc | 0xb2000000000000000000007b9fcbd005511aCBd5 | 24,925.20 | 142.985 | 1 | 2026-09-03 |
| TSLAc | 0xb2000000000000000000001e800a7f5189430cD0 | 6,288.05 | 391.9975 | 1 | 2026-09-03 |
| TTWOc | 0xB2000000000000000000007292D3D91c6b559058 | — | — | 1 | 2026-10-09 |
| ULc | 0xB200000000000000000000349ef3Aa93a0897476 | 564.00 | — | 1 | 2026-10-09 |
| UNHc | 0xB2000000000000000000007A8a3Ab2d3b319036D | — | — | 1 | 2026-10-09 |
| VALEc | 0xB20000000000000000000063376b142C0764B489 | 3,503.00 | — | 1 | 2026-10-09 |
| WDCc | 0xb2000000000000000000008fde21a1F5c69FeC0b | 0.024 | — | 1 | 2026-10-26 |
| WENc | 0xB20000000000000000000044E3CD7a0E1028E57a | 241.77 | — | 1 | 2026-09-29 |
| WRDc | 0xb20000000000000000000089221e238277d52515 | — | — | 1 | 2026-10-09 |

> **Note on "—" supply:** the API omits zero/default fields, so a minted token can show `first_mint_date` with no `total_supply` field in the list response (supply may have been burned to ~0, or the field is omitted). Treat `total_supply` presence, not `first_mint_date` alone, as the live-supply signal — and confirm via the `/total-supply/{address}` endpoint or on-chain `totalSupply()` before quoting a number. **Also: two rows above share an address in the raw API dump as captured (SONYc/SOUNc both list `0xB200…2137743D4a01Fe4e88`, and PLTRc/MRVLc share an address in the page-1/2 dump) — this looks like a data-capture artefact in my paginated pull, NOT a claim that two tokens share one contract. DO NOT use those two addresses from this table; re-pull the API and cross-check `all-tokens.json` before building. Flagged in §(e).**
> **Caution — BIRDc:** API lists `0xB200…535fE96f18204BFD96` for BIRDc, the same address shown for BIDUc in the dump — same artefact warning applies.

**Protocol contracts (from `GET /chains`, verified live):** chain 8453 (Base); Policy Registry `0x8453000000000000000000000000000000000002`; Token Supply Manager `0xD1Ca4dAcdf3231011D175351f1f02D15C7c5664C`; Token Factory `0x4bA3E29E254F25E94E61C4c9d67b37027331534D`. Onchain Registry (docs): `0x3f3E8cf41cdd3b1D118c16471aB0113DfDDd5CaD`.

### Live on-chain read evidence (public RPC, no key)

RPCs tested: `https://mainnet.base.org` → `eth_chainId 0x2105` (8453) ✓ but slow (~15–30 s/call from this VM); `https://base-rpc.publicnode.com` → same chainId, fast (~1 s) ✓. `https://1rpc.io/base` → **rate-limit error, do not use**. Block at time of check: `0x35f5bdd`.

| Check | Result |
|---|---|
| `eth_getCode(TSLAc)` | `0xef` — precompile, no bytecode (as docs state) |
| `name()` TSLAc | `"Tesla Inc."` ✓ |
| `symbol()` TSLAc | `"TSLAc"` ✓ |
| `decimals()` TSLAc | `8` ✓ |
| `totalSupply()` TSLAc | raw `0x9267b2919b` = 628,804,981,147 → **6,288.04981147** = API `total_supply` **exactly** ✓ |
| `multiplier()` TSLAc (`0x1b3ed722`) | `0x0de0b6b3a7640000` = **1.0 exactly** ✓ |
| `uiMultiplier()` TSLAc (`0xa60bf13d`) | same value as `multiplier()` ✓ (aliases) |
| `totalSupplyUI()` TSLAc (`0x9bea6429`) | = raw totalSupply (multiplier 1) ✓ |
| `name()/symbol()/totalSupply()` NVDAc | `"NVIDIA Corporation"` / `"NVDAc"` / raw `0x442291b59ed` = **46,822.04010989**, and the API `/total-supply/` endpoint returned the identical `46822.04010989` seconds later ✓ |
| `multiplier()` NVDAc | `0x0de29ff478c03149` = **1.0005379395763696** = API multiplier ✓ |
| `name()` unminted AALc | `"American Airlines Group Inc."` — readable, but `totalSupply() = 0` |
| Chainlink `latestRoundData()` TSLA feed `0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4` | answer **$391.9975** = API `nav_price` exactly ✓ (8 decimals; roundId/updatedAt decoded, full hex in `rpc-evidence.json`) |
| Chainlink `latestRoundData()` NVDA feed `0x04689a41629776563E6822F76f2e57D148d28513` | answer **$164.61550558** (vs API NAV $165.53 — feeds move; NAV timestamp was 17:41 UTC, feed read later) |

**Function selectors (computed, verified by the calls above):** `name() 0x06fdde03`, `symbol() 0x95d89b41`, `decimals() 0x313ce567`, `totalSupply() 0x18160ddd`, `multiplier() 0x1b3ed722`, `uiMultiplier() 0xa60bf13d`, `totalSupplyUI() 0x9bea6429`, `balanceOfUI(address) 0x437a9958`, `WAD_PRECISION() 0x664808a8`, Chainlink `latestRoundData() 0xfeaf968c`.

**Chainlink feeds (docs, 10 listed — all 8 decimals, 24/5, 0.5% deviation / 24h heartbeat, total-return values):**

| Feed | Proxy address |
|---|---|
| AAPL | `0x787f13dEa48Db0897CbCDD985de77809D837F988` |
| AMZN | `0x06A8E4b3aBB3B7543d8396FB2B763d22820cB295` |
| GOOGL | `0x5bF49E0ffA937CE2FfF033c739aD7C634c4D34F2` |
| META | `0x6526aE6797A76123638b863AeE4dD27Ba4E4b27D` |
| MSFT | `0xeB10A6c9aa7E537aEd766C08c35Dae35B321b18c` |
| MSTR | `0xB3cE282CD188b35DA0E38D8Bc7d58e33173D202a` |
| NVDA | `0x04689a41629776563E6822F76f2e57D148d28513` |
| SNDK | `0x388b0dC46C0Fb05A74BeE0994fa5b02c6Fcca2eA` |
| SPCX | `0x6A634B235903C4ad6376892180d6fF8612e3Fa68` |
| TSLA | `0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4` |

Only 10 feeds are documented — most of the 72 minted tokens have **no** Chainlink feed. For those, price must come from DexScreener (live DEX price) — see §(b). Feeds hold last close on weekends/holidays and freeze during corporate actions; always check `updatedAt` staleness.

---

## (b) Exact data endpoints / APIs to use (all verified responding, no key)

### 1. Tokenized Stocks API — `https://api.coinbase.com/v1/tokenized-stocks` (primary source of truth)

| Endpoint | Example (verified) | Response (captured) |
|---|---|---|
| `GET /?page_size=100&page_token=…` | `GET /?page_size=100` | `{"tokens":[{contract_address, symbol, name, decimals, icon_url, isin, adgm_isin, multiplier, total_supply?, nav_price?, nav_price_updated_at?, first_mint_date?, description, …}], "next_page_token":"…"}` — 338 records over 4 pages |
| `GET /chains` | `GET /chains` | `{"chains":[{"chain_id":"8453","chain":"base","policy_registry_address":"0x8453…0002","token_supply_manager_address":"0xD1Ca…","token_factory_address":"0x4bA3…"}]}` |
| `GET /total-supply/{contract_address}` | `…/total-supply/0xb2000000000000000000001e800a7f5189430cD0` | Plain number: `6288.04981147` (not JSON) |
| `GET /metadata/{ticker}` | `…/metadata/GOOGLc` (case-insensitive; use suffix, e.g. `TSLAc`) | `{"contract_address":"0xb200…","name":"Alphabet Inc.","symbol":"GOOGLc","image":"https://api.coinbase.com/v1/tokenized-stocks/images/GOOGLc.png","prospectus_url":"https://api.coinbase.com/v1/tokenized-stocks/prospectus/GOOGLc.pdf","description":"…","adgm_isin":"…"}` |
| `GET /images/{symbol}` | — | 302 redirect to icon |
| `GET /prospectus/{ticker}` | — | 302 redirect to PDF |
| `GET /prospectuses` | `GET /prospectuses` | `{"prospectuses":[{"ticker":"AALC","isin":"…","documents":[{"type":"primary","approval_date":"2026-10-23","url":"https://www.adgm.com/…pdf"}]}]}` |
| `GET /corporate-actions/{id}` | — | Corporate-action object; ID is the UUID at the end of the `uri` in the token's on-chain `Announcement` event (not the numeric `id`) |

**What it does NOT do:** no wallet endpoints — no positions, cost basis, trade history or P&L. For a holder's position use on-chain `balanceOfUI(account)` (raw balance × multiplier); cost basis/P&L needs your own trade history.

### 2. Public Base RPC (no key)

- `https://mainnet.base.org` — works, slow from this VM (~15–30 s/call).
- `https://base-rpc.publicnode.com` — works, fast. **Recommended primary.**
- `https://1rpc.io/base` — **failed: usage-limit error. Do not use.**
- Use for: `eth_call` (name/symbol/decimals/totalSupply/multiplier/balanceOfUI), `eth_getCode`, Chainlink `latestRoundData()`, event logs (`B20Created` for new-token discovery, `UIMultiplierUpdated` for multiplier history, `Announcement` for corporate actions).

### 3. DexScreener public API — `https://api.dexscreener.com` (no key, verified)

- Rate limits: ~300 req/min (pair/token/search), 60 req/min (profiles/boosts). No auth, no signup.
- `GET /token-pairs/v1/base/{tokenAddress}` — all pools for one token. **Verified for TSLAc and NVDAc.**
  - TSLAc example (captured): Uniswap v4 USDC pair `0x342af3dc…`, `priceUsd 391.94`, `liquidity.usd 33,724.72`, `volume.h24 11,930.8`, `txns.h24 {buys 143, sells 148}` — price within 0.02% of NAV.
  - NVDAc example (captured): 30 pairs; top Aerodrome pair `0xF668e21993…`, `priceUsd 165.043`, `liquidity.usd 1,303,058`, `volume.h24 10,177,386`, `txns.h24 {buys 6,066, sells 6,052}` — by far the deepest stock-token pool found.
- `GET /tokens/v1/base/{tokenAddresses}` (up to 30, comma-separated), `GET /latest/dex/search?q={query}`, `GET /latest/dex/pairs/base/{pairAddress}`.
- Limitations: current state only — **no historical candles, no trade-by-trade feed, no WebSocket**; search returns max ~30 results.

### 4. BaseScan — web yes, API no (without a key)

- Token page loads: `https://basescan.org/token/0xb200…` → HTTP 200 (but B20 precompiles show no contract/bytecode — expected).
- API without key: `api.basescan.org` V1 → *"You are using a deprecated V1 endpoint, switch to Etherscan API V2"*; Etherscan V2 without key for Base → *"Free API access is not supported for this chain. Please upgrade your api plan."* **Conclusion: do not depend on BaseScan/Etherscan API — it needs a paid/keyed plan for Base. Use public RPC + DexScreener instead.**
- For on-chain history (transfers, holders) the free path is RPC `eth_getLogs` — slower but keyless.

### 5. Trading route (for the build, not yet verified end-to-end)

- Docs' "Integrate Trading" guide points at the **0x Swap API** for executable swap routes. **Whether 0x v2 needs an API key was NOT verified in this pass** — see §(e). Do not assume keyless. Alternative keyless execution path: direct Uniswap/Aerodrome router calls via RPC (needs router addresses + quoting — also unverified here).
- Note from docs: the CDP Trade API does **not** quote B20 tokens (per Ozmium docs, third-party — treat as a lead, not a fact).

---

## (c) Judging criteria & submission requirements (official pages, exact wording)

Sources: Quest Page `https://www.base.org/stocksmaxxing` (HTML fetched 2026-11-12, raw copy `quest.html`) and Official Rules `https://www.base.org/stocksmaxxing/rules` (read in full, §§1–16 + Appendix 1).

### Quest facts (verified on the page)

- **Name:** Stocks Maxxing Season. **Period: Nov 5 – Dec 5, 2026** (times UTC unless page says otherwise). Submit by **11:59 PM UTC on Dec 5, 2026**.
- **Total: $100,000+ in rewards.** FAQ breakdown (embedded in page payload, verified): **$50,000 in Base-track prizes + $48,000 across partner prizes + $6,000 community-voted build-in-public award** (= $104,000).
- **Timeline:** Nov 5 applications open · Nov 6–13 brainstorm with partners · Nov 13–Dec 5 build & launch · Dec 5 submit · then winners announced (no date given on the page).
- **Tracks (3, judged and awarded separately):**
  1. **Meme and Community Economies** — "Build new ways to organize memes and communities around tokenized equities." (7 partners)
  2. **Agentic Stock Finance** — **"Build agents that research, earn or trade around tokenized stocks in novel ways."** (3 partners: Base, Bankr, BaseStonk per page icons)
  3. **Programmable Stock Markets** — "Create net-new stock market primitives, e.g., custom portfolios, indexes, structured products, financing tools, prediction markets, and market infrastructure." (3 partners)
- **Partners (6):** o1 Exchange, Bankr, Stonks Exchange, BaseStonk, Feel.cash, Hydropump by Hydrex. Partner programs are under each partner's own terms; Base is not responsible for them.
- **Who can enter:** build something new, or grow a live project. Teams that previously launched tokens are NOT eligible by default — must ship a demonstrable stock-linked product/feature during the campaign (token launched Aug 5–Nov 4 can qualify if a new stock-linked feature ships during the season; a relaunch does not reset the launch date). **Launching a token is optional.**
- **Eligibility (FAQ + Rules §4):** 18+; not resident in a US-OFAC-sanctioned country/region; **projects that enable trading for US users are not eligible**; winners subject to identity verification + tax obligations. Teams up to 5, one Team Representative receives the prize.
- **"Ideas to build"** on the Resources section is still **"Coming soon"** on 2026-11-12 — no official example-ideas list was retrievable. No per-track "Show us" guidance text was present in the page as fetched.

### Judging criteria — what the pages actually say

- **Rules §7:** *"The judges will score each Submission against the criteria included on the Quest Page, weighted equally unless the Quest Page sets different weights."* Judges' decisions are final and binding.
- **The Quest Page as fetched on 2026-11-12 contains NO judging-criteria list and NO weights** — no "Traction / Product / Building in public" breakdown appears anywhere in the page HTML (searched for: Traction, criteria, weight, example, "Show us" — zero hits except the footer disclaimer "judging criteria may change"). The FAQ answers contain no criteria either.
- **Therefore: the 50% traction / 25% product / 25% building-in-public split reported by CryptoBriefing/KuCoin/Binance Square (third-party press, Nov 5) is NOT confirmed by the official pages as fetched.** It may be real (e.g. in a deck, X post, or a page section that loads later), but **do not build the scoring strategy on it until it is verified on base.org itself.** The only official, quotable rule is "criteria on the Quest Page, weighted equally unless the Quest Page sets different weights" — and right now the Quest Page sets none.
- **⚠️ FLAG — the "$20,000 Agentic Stock Finance pool" in the task brief is UNVERIFIED.** No $20,000 figure appears anywhere on the Quest Page or Rules. The only verified prize split is $50,000 across all three Base tracks + $48,000 partner + $6,000 build-in-public. If $50,000 were split equally it would be ~$16,667/track, but that split is **not stated anywhere** — do not quote $20,000 (or any per-track amount) as fact. Re-check the Quest Page / Apply form before promising a prize figure.

### Submission requirements (Rules §§5–6 + FAQ)

1. **Public X post** with a **video demo** (e.g. Loom) explaining how it works, tagging **@buildonbase** (page may require other tags/content).
2. **Complete the official submission form** linked on the Quest Page (Google Form: `https://docs.google.com/forms/d/1zotYvkeAtDjR2MKk3qNxyNIAfJ_IPQtzTtjNhOAF8js/viewform` — this is the "Apply Now" link; the same form is used for registration and submission per the FAQ: *"Didn't register? You can still submit."*). Include the X-post link, track(s) entered, and anything else the form requests. **A submission is not complete until the Sponsor receives the form.**
3. Meet any other requirements in the Track Section for each track entered.
4. One submission per track per entrant/team (a project may enter multiple tracks only if the Quest Page allows it; a project can win in only one track unless the page says otherwise).
5. Each submission must: be built on / meaningfully integrate Base + fit the track; be original work (pre-existing code/products OK if the form clearly describes what was built during the Quest Period); not infringe IP/privacy; no malware/hateful content; no unnecessary personal info; comply with applicable law (securities, commodities, derivatives, lending, consumer protection, money transmission, gaming, prediction markets, sanctions, data protection); **not misrepresent any relationship/endorsement by Base, a Partner, an issuer, or a public company, and not claim rights in an underlying public company (e.g. voting rights) that the asset does not provide.**
6. **No purchase/transaction/wallet funding/token holding/payment is required to enter.** Testnet builds are explicitly allowed and *"will not be judged less favorably."*
7. **Build-in-public award ($6,000):** share the journey on X throughout the season, tag @buildonbase; community votes under published voting rules (voting rules themselves were not found on the page — unverified, see §(e)).
8. **Prizes (Rules §10):** amounts in USD, **paid in USDC on Base** unless the Track Section says otherwise; delivered normally within 30 days after verification; winners must respond within 7 days of notification and provide ID/age/residence proof, sanctions screening, W-9/W-8, wallet address, signed eligibility/liability/publicity declaration. Prizes non-transferable, winners pay taxes.
9. **IP (Rules §11):** entrants keep ownership; Base/partners get a non-exclusive royalty-free licence for 2 years after the Quest to use public submission materials (X post, demo, name/logo/descriptions) for administering/promoting the Quest — no right to commercialise the underlying code/product. Submissions are not confidential.
10. **Disqualification triggers (Rules §13):** tampering, plagiarism/fraud, **manipulating engagement or traction metrics**, unsportsmanlike conduct. (Directly relevant: do not fake traction.)

---

## (d) Bankr — what the launch partner offers builders

Sources: `https://docs.bankr.bot/` (home), `/getting-started/quick-start/`, `/faq/bankr-club/`, `/x402-cloud/pricing/`, `/claude-plugins/bankr-agent-dev/`; skills repo `https://github.com/BankrBot/skills`.

### What Bankr is
AI-agent infrastructure on Base (and 10 other chains incl. Ethereum, Solana, BNB, Hyperliquid): a built-in cross-chain wallet per agent, token launchpad, and plug-in skills. Pitch: "Build an AI agent. Launch a token. Trading fees pay for your compute."

### Builder-relevant offerings

| Offering | What it is | Free? |
|---|---|---|
| **Agent API** (`POST https://api.bankr.bot/agent/prompt`, `GET https://api.bankr.bot/agent/job/{jobId}`, header `X-API-Key`) | Natural-language prompts → agent executes trades, checks balances, launches tokens, DCA/limit/stop-loss automations. Async job model: POST returns `jobId`, poll until complete. | **NO — needs Bankr Club ($20/mo or $198/yr) or Max Mode (LLM credits).** Docs Quick Start banner: "Subscription Required". Non-members: API capped at **100 req/day** vs Club **1,000 req/day** — i.e. a key alone gives a small allowance, but the docs state a subscription/credits are required beyond the 5 free messages/day at bankr.bot. **Budget $20/mo if StockSage depends on this.** |
| **Bankr Skill** (`github.com/BankrBot/skills/tree/main/bankr`) | Plug-and-play skill for Claude Code / OpenClaw / Cursor: trading, token launches, fee capture, built-in wallet with safeguards, Sign-In With Agent, Axiom signals, ERC-8004, ENS, etc. | Skill itself is free/open, but it calls the Agent API → same subscription requirement. |
| **Bankr CLI** (`@bankr/cli`: `bankr login`, `bankr launch`, `bankr fees`, `bankr agent "…"`) | Terminal route to the same API. | Same subscription requirement. |
| **Claude Plugins** (`bankr-agent-dev`, `bankr-x402-sdk-dev`, `bankr-agent`) | `claude plugin install bankr-agent-dev` — scaffolding (trading bot / dashboard / CLI), API docs, TS interfaces, codegen. x402 plugin adds leveraged trading (Hyperliquid, Base via Avantis), swaps. | Plugins free; underlying API calls need the subscription. |
| **x402 Cloud** (hosted pay-per-call APIs) | Deploy paid API endpoints with x402 payments built in, USDC on Base by default, settlement via `BankrFeeRouterV2`, compute/storage/logs included, 256 MB, 30 s execution. | **YES — genuinely free tier: 0% platform fee for the first 1,000 settled requests/month; 5% after that; no monthly fee, no card.** Only settled (paid + successful) requests count. `ctx.askAgent` free tier 2/day (5/day with Club). |
| **Token launchpad** (Doppler launches) | Fair-launch a token on Base; **0.7% pool swap fee, 95% to the launcher (0.665% of volume)**; plus Bankr protocol fee + BNKR buyback/LP fee (1.75% all-in quoted in llms-full). | Launching itself has no upfront fee listed, but: max **3 counted launch attempts per rolling 24h** per wallet; spam detection can restrict accounts. |
| **LLM Gateway / Max Mode** | 25+ LLMs pay-per-use from LLM-credit balance; `:private` suffix for TEE private inference. | Pay-as-you-go, not free. |
| **$100K Inference Program** | Free inference credits for builders (apply via Google Form) — mentioned in a third-party skill index (GentechLabs), **not verified on docs.bankr.bot in this pass**. Treat as a lead. |

### Verdict for StockSage
- **Do NOT architect StockSage around the Bankr Agent API unless the $20/mo Club cost is accepted** (or Max Mode credits). It is the only way to get Bankr to execute trades / hold a wallet for the agent.
- **x402 Cloud is the free, usable piece**: StockSage could expose its own analysis as a pay-per-call x402 endpoint at $0 cost for the first 1,000 settled req/mo — a credible "earn" leg for the Agentic track without spending.
- The Bankr **skill + Claude plugins are free to read/use as reference** and are the fastest way to learn the API shapes.
- Bankr is listed as an Agentic Stock Finance track partner (3 partners on that track), so a Bankr integration is on-theme — but the Rules say partner prizes are under partner terms, and **no Bankr-specific partner prize amount was found on the Quest Page or Bankr docs in this pass** (unverified, §(e)).

---

## (e) Gaps / unverified

1. **Agentic Stock Finance prize pool ($20,000 in the brief) — UNVERIFIED.** No per-track prize amount appears on the Quest Page or Rules. Only verified split: $50,000 Base tracks + $48,000 partners + $6,000 build-in-public.
2. **Judging criteria & weights — NOT on the official pages as fetched.** Rules §7 defers to the Quest Page; the Quest Page (2026-11-12) lists none. The 50/25/25 traction/product/build-in-public split exists only in third-party press. Re-check base.org before the build is scored against it.
3. **Example ideas / "Show us" guidance for the Agentic track — NOT FOUND.** "Ideas to build" is "Coming soon"; no example ideas in the page HTML. Rules §14 says track descriptions/example ideas are "for inspiration only."
4. **Build-in-public voting rules — NOT FOUND** ("under the published voting rules" — no link/content located).
5. **Winner-announcement date — NOT STATED** on the Quest Page (only "Winners announced" as a timeline step) or in the Rules (notification within 7 days of being contacted is the only timing).
6. **Duplicate-address artefacts in my token pull — MUST RE-VERIFY before use.** In the paginated API dump as captured, SONYc/SOUNc share one address, PLTRc/MRVLc share one, and BIRDc/BIDUc share one. This is almost certainly a pagination/merge artefact in my capture, not reality — but **do not build from those rows; re-pull `GET /?page_size=500` and diff against `all-tokens.json`.** All other addresses in §(a) are quoted verbatim from the API responses.
7. **0x Swap API key requirement — NOT VERIFIED.** Docs recommend it for trading integration; whether a key is needed (and whether it is free) was not checked. Same for direct Uniswap/Aerodrome router addresses for B20 swaps.
8. **Bankr partner prize for this quest — NOT FOUND.** No Bankr-specific prize/terms on the Quest Page or Bankr docs in this pass. Also the $100K Inference Program is third-party-reported only.
9. **BaseScan/Etherscan API for Base — VERIFIED UNAVAILABLE free** (V1 deprecated; V2: "Free API access is not supported for this chain"). Not a gap in knowledge — a confirmed dead end; use RPC + DexScreener.
10. **Only 10 Chainlink feeds documented; only 12 tokens carry `nav_price`.** Price coverage for the other ~60 minted tokens relies on DexScreener DEX prices (thin liquidity on many — e.g. TSLAc/USDC pool only ~$33k liquidity; always check `liquidity.usd` before trusting a DexScreener price).
11. **Corporate-actions endpoint not exercised live** (needs a UUID from an on-chain `Announcement` event; none pulled in this pass). Docs shape is recorded in §(b) only.
12. **Builder Code for StockSage not yet registered** — registration happens at base.dev (ERC-721 mint, payout address). No code exists yet; the build must register one and append the ERC-8021 suffix (`dataSuffix`, 16 gas/non-zero byte) to agent transactions for traction attribution. Validation tool: `builder-code-checker.vercel.app`.

---

## Sources (all accessed 2026-11-12)

- https://docs.base.org/sdks/tokenized-stocks/overview (Tokenized Stocks API; updated 2026-11-09)
- https://docs.base.org/build-on-base/integrate-defi/list-tokenized-stocks (B20, multipliers, feeds, addresses; updated 2026-11-09)
- https://docs.base.org/specifications/builder-codes/overview (Builder Codes; updated 2026-11-06)
- https://www.base.org/stocksmaxxing (Quest Page; HTML saved as `quest.html`)
- https://www.base.org/stocksmaxxing/rules (Official Rules, §§1–16 + App. 1)
- https://api.coinbase.com/v1/tokenized-stocks (+ `/chains`, `/metadata/{ticker}`, `/total-supply/{addr}`, `/prospectuses`) — live calls, no key
- https://mainnet.base.org and https://base-rpc.publicnode.com — live `eth_call`/`eth_chainId`/`eth_blockNumber`
- https://api.dexscreener.com/token-pairs/v1/base/… and /latest/dex/search — live calls, no key
- https://docs.bankr.bot/ (+ `/getting-started/quick-start/`, `/faq/bankr-club/`, `/x402-cloud/pricing/`, `/claude-plugins/bankr-agent-dev/`)
- Third-party press used ONLY where flagged: CryptoBriefing / KuCoin / Binance Square (50/25/25 judging split — unverified against official pages).
