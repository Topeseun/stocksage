# StockSage

StockSage is an autonomous AI agent for tokenized stocks on Base. It reads live activity on Base and market data for every Coinbase tokenized stock, gives each one a single explainable score, and manages a paper portfolio — shifting money toward the strongest scores and writing down why for every change. It runs the whole loop by itself, in the open, on live Base data.

Built for the **Base Stocks Maxxing** hackathon, **Agentic Stock Finance** track — "build agents that research, earn or trade around tokenized stocks in novel ways." See [base.org/stocksmaxxing](https://www.base.org/stocksmaxxing). (Prize split verified from the official Quest page: $50,000 across the Base tracks + $48,000 in partner prizes + a $6,000 build-in-public award. Per-track amounts are not published, so none is quoted here.)

## The loop: research → score → rebalance

1. **Research.** The agent pulls the list of tokenized stocks from the Coinbase Tokenized Stocks API (338 tokens on 2026-11-12, 72 ever minted), reads on-chain state over public Base RPC (supply, multiplier, holders, transfers), and fetches prices, liquidity and volume from DexScreener and Chainlink NAV feeds.
2. **Score.** Every stock gets one score from 0 to 100 (see "How scoring works" below), with plain-language reasons attached.
3. **Rebalance.** The paper portfolio shifts toward the highest scores — raising, lowering, opening or closing positions — and every decision is written to `data/decisions.jsonl` with its reason.

The full verified research behind the data sources is in [`research/research-report.md`](research/research-report.md).

## Architecture

```
                          +---------------------------+
                          |  Coinbase Tokenized       |
                          |  Stocks API (no key)      |
                          +-------------+-------------+
                                        |
  +-------------------+   +-------------v-------------+   +-------------------+
  | Public Base RPC   |-->|  stocksage core engine    |-->|  DexScreener API  |
  | (on-chain reads)  |   |  universe / chain /       |   |  (prices, liq,    |
  +-------------------+   |  prices / research /      |   |   volume)         |
                          |  portfolio                |   +-------------------+
                          +------+------+------+------+
                                 |      |      |
                    data/state.json  data/decisions.jsonl
                                 |      |
              +------------------v------v------------------+
              |  stocksage/dashboard.py (stdlib http.server)|
              |  single-page app: Research / Portfolio /    |
              |  Decisions / How scoring works + JSON API   |
              +--------------------------------------------+
                                 |
                          demo.py (narrated live run)
```

State files (written by the core engine, read by the dashboard and demo):

- `data/state.json` — `as_of`, `universe` (count/minted), `scores` (address, symbol, name, score, components, price, source, liquidity, volume, supply, multiplier, reasons), `portfolio` (cash, total value, positions), `decisions` (last 20).
- `data/decisions.jsonl` — one JSON object per rebalance: `ts`, `type`, `action` (increase/decrease/open/close/hold), `symbol`, `from_weight_pct`, `to_weight_pct`, `reason`, `score`.

## How to run it

Prerequisites: **Python 3.11+**. No install step — standard library only, no dependencies (see `requirements.txt`).

```bash
# 1. One full live cycle: research -> score -> rebalance
python -m stocksage run

# 2. Start the dashboard (default http://127.0.0.1:8000/)
python -m stocksage dashboard

# 3. Or run the narrated demo (one live cycle + plain-language summary)
python demo.py
```

Other core commands: `python -m stocksage score`, `python -m stocksage portfolio`, `python -m stocksage decisions`. Dashboard options: `--port 8000`, `--data-dir DIR`, `--sample` (preview the clearly-labelled sample state instead of live state).

### Reproduction steps (expected output)

```bash
cd stocksage
python -m stocksage run
# expected: the core prints its progress and exits 0, and data/state.json
#           appears with an "as_of" timestamp from just now.

python -m stocksage dashboard --port 8000
# expected: "StockSage dashboard at http://127.0.0.1:8000/" — open it in a
#           browser: Research shows a sortable table of scored stocks,
#           Portfolio shows cash/total/positions, Decisions shows the
#           rebalance history, and "How scoring works" explains the formula.

python demo.py
# expected: "StockSage — LIVE DATA", an as-of timestamp, the top 3 stocks
#           with scores and reasons, portfolio totals, and the latest
#           rebalance decision with its reason.

python -m unittest discover -s tests -v
# expected: all tests pass (see tests/test_dashboard.py).
```

If `data/state.json` does not exist yet, the dashboard's JSON endpoints return HTTP 503 with the message "No live state yet — the core engine has not written data/state.json…", and the page says so plainly. To preview the dashboard before the core has run, use the labelled sample data:

```bash
python -m stocksage dashboard --sample
```

The sample file (`data/sample-state.json`) is clearly marked `sample: true`, carries a `sample_note`, and the dashboard shows a "SAMPLE DATA — not live" badge whenever it is served. Sample data is never presented as live.

## How the scoring works

```
score = 0.4 × on-chain + 0.3 × momentum + 0.3 × market
```

Each component is a **percentile rank from 0 to 100 within the universe**:

- **On-chain (40%)** — what is happening on Base itself: tokens minted, holders, transfers and other activity the chain records.
- **Momentum (30%)** — how the price has been moving recently, relative to the other stocks.
- **Market (30%)** — how tradable it is: price source, liquidity and 24-hour trading volume.

A score of 90 means the stock ranks near the top of this universe right now — not that it is "90% good" in absolute terms. Every score carries plain-language reasons, shown in the dashboard's "Why this score" panel.

## Data sources

All free, all keyless, no sign-up:

| Source | Used for |
|---|---|
| Coinbase Tokenized Stocks API (`api.coinbase.com/v1/tokenized-stocks`) | The list of stocks, supplies, multipliers, NAV prices |
| Public Base RPC (`base-rpc.publicnode.com`, fallback `mainnet.base.org`) | On-chain reads: name, symbol, supply, multiplier, balances |
| DexScreener (`api.dexscreener.com`) | DEX prices, liquidity, 24h volume |
| Chainlink price feeds | NAV reference prices for the 10 documented feeds (AAPL, AMZN, GOOGL, META, MSFT, MSTR, NVDA, SNDK, SPCX, TSLA) |

Notes from the research: B20 tokens are Base-native precompiles (no contract bytecode on Basescan — that is normal); only 72 of the 338 listed tokens have ever been minted; identify tokens by contract address, never by symbol. BaseScan/Etherscan API needs a paid plan for Base and is not used.

## Paper-trading disclaimer

StockSage trades a **paper portfolio starting at $100,000**. No real funds, no real trades, no transaction is ever signed, and no token has been launched. Nothing here is investment advice. Tokenized stocks are only available to persons in eligible jurisdictions outside the U.S.

## License

MIT — see [LICENSE](LICENSE).
