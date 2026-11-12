# 01 — Base Tokenized Stocks docs (docs.base.org)

Read 2026-11-12. Pages:
- https://docs.base.org/sdks/tokenized-stocks/overview (API overview; updated 2026-11-09)
- https://docs.base.org/build-on-base/integrate-defi/list-tokenized-stocks (integration guide; updated 2026-11-09)
- https://docs.base.org/specifications/builder-codes/overview (Builder Codes; updated 2026-11-06)

## Tokenized Stocks API
- Base URL: **https://api.coinbase.com/v1/tokenized-stocks** (found in the API-reference page source; `api.base.org` candidates 404). Read-only, **no API key**.
- Endpoints: `GET /` (list), `GET /chains`, `GET /total-supply/{contract_address}` (returns a bare number, not JSON), `GET /metadata/{ticker}`, `GET /images/{symbol}` (302), `GET /prospectus/{ticker}` (302), `GET /prospectuses`, `GET /corporate-actions/{id}`.
- List pagination: `page_size` default 100, max 500; `next_page_token` → `page_token`. Tokens ordered by contract address. JSON omits default-valued fields (missing `total_supply` ≠ 0 — check the dedicated endpoint).
- Fields: contract_address, symbol, name, decimals, icon_url, isin, adgm_isin, multiplier, total_supply (token units, normalised by decimals — NOT share count), nav_price, nav_price_updated_at, first_mint_date (UTC block time of first positive mint), description, paused_features.
- `multiplier`: token units → shares. Changes on dividends/splits. `nav_price`: latest Chainlink-based NAV/reference value — NOT a live bid/ask; check `nav_price_updated_at` staleness (feeds update on 0.5% deviation or 24h heartbeat, hold last close out of hours).
- No wallet endpoints: no positions, cost basis, trade history, P&L. Holder position = on-chain `balanceOfUI(account)`.

## B20 standard (integration guide)
- B20 = Base-native token standard, ERC-20 extension, asset-agnostic. Tokenized stocks are one use case. Product details: coinbase.com/tokenize.
- **B20 tokens are native precompiles: no per-asset contract, no verified contract on Basescan, no bytecode.** Audited by Base + Spearbit (Beryl upgrade); Cantina + HackerOne coverage.
- 8 decimals for stocks. Name/symbol mutable on-chain (`updateName`/`updateSymbol`) — **identify by address**.
- New tokens: watch the `B20Created` event.
- Multipliers: scheduled via ERC-8056 `updateUIMultiplier` (preferred); instant `updateMultiplier` is deprecated emergency failsafe; `cancelUIMultiplierUpdate` cancels pending. Helpers: `uiMultiplier()` (= `multiplier()`), `balanceOfUI()`, `totalSupplyUI()`, `toUIAmount(raw)`, `fromUIAmount(ui)`; `toScaledBalance`/`toRawBalance` deprecated. Multiplier is WAD (1e18); read scale via `WAD_PRECISION()` (= 1e18). Example in docs: dividend → multiplier 1.02 (1 token = 1.02 shares); cash dividends are converted to shares, not paid out.
- Policies: `isAuthorized(policyID, account)` (never reverts — check `policyExists` first); allow/block lists can make transfers revert. Pauses: specific functions can be paused. Announcements: `announce` → `Announcement(id, description, uri)` → `EndAnnouncement`; index for corporate actions. No built-in timelock on admin/multiplier actions.
- Memos: `transferWithMemo` / `transferFromWithMemo` (bytes32, `Memo` event). Optional supply cap. `extraMetadata(key)` for ISIN/CUSIP etc.
- Compliance: secondary holding/trading permissionless; KYC only for mint/redeem by Authorized Participants. Only for eligible jurisdictions outside the U.S.

## Price feeds (Chainlink, on-chain)
- 10 documented feeds, all 8 decimals, 24/5, total-return values (include corporate-action adjustments): AAPL `0x787f13dEa48Db0897CbCDD985de77809D837F988`, AMZN `0x06A8E4b3aBB3B7543d8396FB2B763d22820cB295`, GOOGL `0x5bF49E0ffA937CE2FfF033c739aD7C634c4D34F2`, META `0x6526aE6797A76123638b863AeE4dD27Ba4E4b27D`, MSFT `0xeB10A6c9aa7E537aEd766C08c35Dae35B321b18c`, MSTR `0xB3cE282CD188b35DA0E38D8Bc7d58e33173D202a`, NVDA `0x04689a41629776563E6822F76f2e57D148d28513`, SNDK `0x388b0dC46C0Fb05A74BeE0994fa5b02c6Fcca2eA`, SPCX `0x6A634B235903C4ad6376892180d6fF8612e3Fa68`, TSLA `0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4`.
- Read via `latestRoundData()` on the proxy. Feed = underlying price × multiplier (from Coinbase's on-chain oracle registry); paused → holds last good value; freezes during corporate actions; total-return so no price discontinuity at splits.
- Historical: Chainlink round history by `roundId`; reconstruct multiplier history from `UIMultiplierUpdated` events dated by `effectiveAtTimestamp` (drop updates later cancelled by `UIMultiplierUpdateCancelled`).
- Off-chain: CoinGecko / CoinMarketCap / RWA aggregators track live DEX prices (24/7 secondary market).

## Protocol contracts (from `GET /chains`, live)
- Chain 8453 Base; Policy Registry `0x8453000000000000000000000000000000000002`; Token Supply Manager `0xD1Ca4dAcdf3231011D175351f1f02D15C7c5664C`; Token Factory `0x4bA3E29E254F25E94E61C4c9d67b37027331534D`. Onchain Registry (docs): `0x3f3E8cf41cdd3b1D118c16471aB0113DfDDd5CaD`.

## Builder Codes (ERC-8021)
- ERC-721 NFT collection; a code (e.g. "abc123") minted at **base.dev** identifies the builder on-chain; on-chain metadata = payout address; off-chain = app name/site.
- Attribution: suffix appended to transaction calldata; contracts ignore it; off-chain indexers attribute usage → rewards, Base Dashboard analytics (spot volume, borrow/lending TVL), discovery surfaces (leaderboards, Base App store).
- No contract changes needed; works with EOAs (all support `dataSuffix`) and ERC-5792 smart wallets (`DataSuffixCapability`); Privy and Turnkey support it. Cost: 16 gas per non-zero byte. No identity exposure beyond public on-chain data.
- Verify: Basescan input data — last 16 bytes are the `8021` repeating marker; or the Builder Code Validation Tool (`builder-code-checker.vercel.app`).
- StockSage action: register a code at base.dev before launch; append suffix to every agent transaction.
