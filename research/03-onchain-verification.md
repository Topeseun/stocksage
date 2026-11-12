# 03 — On-chain verification (live, no key, 2026-11-12)

## RPCs tested
| RPC | Result |
|---|---|
| https://mainnet.base.org | `eth_chainId` → `0x2105` (8453) ✓ — but very slow from this VM (~15–30 s per call) |
| https://base-rpc.publicnode.com | `eth_chainId` → `0x2105` ✓ — fast (~1 s). Recommended primary. |
| https://1rpc.io/base | Error `-32001`: "You've reached the usage limit for your current plan" — DO NOT USE |

Block at check time: `0x35f5bdd`.

## Method
`eth_call` with standard selectors (verified by the responses): `name() 0x06fdde03`, `symbol() 0x95d89b41`, `decimals() 0x313ce567`, `totalSupply() 0x18160ddd`, `multiplier() 0x1b3ed722`, `uiMultiplier() 0xa60bf13d`, `totalSupplyUI() 0x9bea6429`, `balanceOfUI(address) 0x437a9958`, `WAD_PRECISION() 0x664808a8`, Chainlink `latestRoundData() 0xfeaf968c`.

## Results

### TSLAc — `0xb2000000000000000000001e800a7f5189430cD0`
- `eth_getCode` → `0xef` (precompile marker; no bytecode — matches docs: B20s are native precompiles)
- `name()` → `"Tesla Inc."`; `symbol()` → `"TSLAc"`; `decimals()` → `8`
- `totalSupply()` → raw `0x9267b2919b` = 628,804,981,147 → **6,288.04981147**, exactly the API `total_supply`
- `multiplier()` → `0x0de0b6b3a7640000` = **1.0**; `uiMultiplier()` identical (aliases confirmed)
- `totalSupplyUI()` → same as raw totalSupply (multiplier 1)
- Chainlink feed `0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4`, `latestRoundData()` → roundId 36893488147419104602, **answer $391.9975** (8 decimals), updatedAt 1794499709 — exactly the API `nav_price` (391.9975). Full hex in `rpc-evidence.json`.

### NVDAc — `0xb20000000000000000000078ee7ce2fE4908108C`
- `name()` → `"NVIDIA Corporation"`; `symbol()` → `"NVDAc"`
- `totalSupply()` → raw `0x442291b59ed` = **46,822.04010989**; the API `/total-supply/` endpoint returned the identical `46822.04010989` seconds later. (An earlier API snapshot read 46,713.09 — supply moved ~109 tokens in ~5 min; supply is live.)
- `multiplier()` → `0x0de29ff478c03149` = **1.0005379395763696** = API multiplier
- Chainlink feed `0x04689a41629776563E6822F76f2e57D148d28513`, `latestRoundData()` → **answer $164.61550558** (API NAV was $165.53 at 17:41 UTC — feeds move; check timestamps)

### Unminted token — AALc `0xB2000000000000000000004FeB8D277Dd14b08Bb`
- `name()` → `"American Airlines Group Inc."` (readable), but `totalSupply()` → `0`. Lesson: name/symbol readability does NOT mean a token is tradable — gate on `total_supply > 0` / `first_mint_date` / DexScreener liquidity.

## API census (live, 2026-11-12)
- `GET https://api.coinbase.com/v1/tokenized-stocks?page_size=100`, 4 pages via `next_page_token`: **338 token records total; 72 minted** (`first_mint_date` present), 266 registered-only (zero supply). `nav_price` present for 12 tokens only. Multiplier ≠ 1 for 9 tokens (PMc 1.5588, SANc 1.0106, GOOGLc 1.00038, NOKc 1.00196, NVDAc 1.00054, METAc 1.00031, ORCLc 1.00004, MRVLc 1.0000019, MUc 1.00010).
- Full dump: `all-tokens.json`; minted table: `minted.csv`.
- **Data-quality flag:** in the paginated pull as captured, SONYc/SOUNc share address `0xB200…2137743D4a01Fe4e88`, PLTRc/MRVLc share one, BIRDc/BIDUc share one. Almost certainly a capture/merge artefact, not reality — re-pull with `page_size=500` and diff before using those rows. All other addresses are verbatim from API responses.
