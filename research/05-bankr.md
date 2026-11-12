# 05 — Bankr (Agentic Stock Finance track partner)

Sources read 2026-11-12: https://docs.bankr.bot/ (home), /getting-started/quick-start/, /faq/bankr-club/, /x402-cloud/pricing/, /claude-plugins/bankr-agent-dev/; skills repo https://github.com/BankrBot/skills.

## What it is
Infrastructure for self-sustaining AI agents. Built-in cross-chain wallet per agent, token launchpad, plug-in skills. Chains: Base, Ethereum, Polygon, Unichain, World Chain, Arbitrum, BNB, Robinhood Chain, Arc, Solana, Hyperliquid. Tagline: "Build an AI agent. Launch a token. Trading fees pay for your compute."

## Offerings for builders

### Agent API — the trading brain (NOT free)
- `POST https://api.bankr.bot/agent/prompt` with header `X-API-Key: <key>`, body `{"prompt": "buy $10 of ETH on base"}` → returns `{jobId}`; poll `GET https://api.bankr.bot/agent/job/{jobId}` with the same key.
- API key: sign up at `bankr.bot/api-keys`; new keys have Agent API + Wallet API access on by default.
- **Cost gate (docs Quick Start banner: "Subscription Required"):** Agent prompts from the skill, Agent API, plugins and CLI need **Bankr Club ($20/mo or $198/yr)** or **Max Mode with LLM credits**. At bankr.bot you get 5 free messages/day. Club caps the Agent API at **1,000 req/day vs 100/day for non-members**; Max Mode (non-Club) also caps at 100/day. Pay Club with USDC (default), BNKR, ETH, or any Base ERC-20.
- Club extras: unlimited messages at bankr.bot, scheduled agent commands (≤20 active), browser sessions, advanced research (Bankr score, PnL & volume analytics, web search, social sentiment, asset news), 5 free `bankr.askAgent`/`ctx.askAgent` runs/day for deployed apps (vs 2 without Club; both pause after 14 days without a signed-in visit), early access / airdrops / private chat.
- HISS docs (third-party) corroborate: "Bankr requires either a Bankr Club subscription or Max Mode (LLM credits) to use — there is no free tier, and a valid API key alone is not enough" (403 `subscription_required`).

### Bankr Skill + Claude Plugins (free to install; API calls still gated)
- Skill: `github.com/BankrBot/skills/tree/main/bankr` — install into Claude Code / OpenClaw / Cursor; covers token launches, trading-fee capture, built-in wallet with safeguards, Sign-In With Agent, Axiom signals, Botchan, ERC-8004, ENS, OnchainKit, QRcoin, Veil, Yoink, Neynar, Hydrex.
- Plugins: `claude plugin marketplace add BankrBot/claude-plugins`, then `claude plugin install bankr-agent-dev` (scaffolding: trading bot / dashboard / CLI / web service; API docs; TS interfaces; codegen) or `bankr-x402-sdk-dev` (advanced: leveraged trading via Hyperliquid / Base via Avantis, swaps).
- CLI: `npm i -g @bankr/cli`; `bankr login` / `bankr launch` / `bankr fees` / `bankr agent "…"`.

### x402 Cloud — genuinely FREE tier (the usable piece)
- Deploy pay-per-call API endpoints with x402 payments built in; USDC on Base by default (any ERC-20 possible); settlement via `BankrFeeRouterV2` smart contract, atomic, straight to your wallet.
- Pricing: **Free — 0% platform fee, up to 1,000 settled requests/month, $0, no card, no monthly fee.** Pro: 5% after 1,000/mo. Enterprise: 3%, contact sales. Only successful, settled requests count (402s and failed handlers are free). Min price $0.000001/request. Compute/storage/bandwidth/logs (90 days) included; 256 MB, 30 s execution; 25 services/deploy; unlimited services/account.
- Rate limits: deploys 20/hour/IP; 60 req/min per paying wallet per endpoint; discovery search 30/min/IP; `ctx.askAgent` 5/min per wallet, free tier 2/day (5/day Club), 0/day after 14 days inactive (Max Mode uncapped).

### Token launchpad
- Fair-launch a token on Base (Doppler). **0.7% pool swap fee, 95% to the launcher (0.665% of volume)**; plus Bankr protocol fee + BNKR buyback/LP fee (1.75% all-in, per llms-full.txt). Fees fund LLM costs via the LLM Gateway.
- Limits: max **3 counted launch attempts per rolling 24h** per wallet; automated spam detection can restrict accounts (appeal via Help Center).

### LLM Gateway / Max Mode
- 25+ LLMs pay-per-use from an LLM-credit balance; `:private` model suffix for TEE private inference. Not free.

### $100K Inference Program
- Free inference credits for builders, apply via Google Form — reported in a third-party skill index (GentechLabs), **not verified on docs.bankr.bot in this pass**. Lead only.

## Verdict for StockSage
- Do not depend on the Agent API unless the $20/mo Club (or Max Mode credits) is budgeted.
- x402 Cloud is the free, credible "earn" leg: expose StockSage analysis as a pay-per-call endpoint at zero cost for the first 1,000 settled req/mo.
- Skill + plugins are free reference material for API shapes.
- No Bankr-specific partner prize amount for this quest was found on the Quest Page or Bankr docs — unverified.
