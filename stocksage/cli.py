"""CLI: `python -m stocksage run|score|portfolio|decisions` from the repo root.

No install step beyond Python 3.11+ itself (stdlib only).
"""
from __future__ import annotations

import argparse
import json
import sys

from . import agent, portfolio as portfolio_mod, research, signals, state as state_mod, universe as universe_mod


def cmd_run(args) -> int:
    st = agent.run_cycle(refresh=args.refresh)
    print(f"Cycle complete at {st['as_of']}")
    print(f"Universe: {st['universe']['count']} records, "
          f"{st['universe']['minted']} minted")
    print(f"Scored: {len(st['scores'])} tokens")
    print("Top 5:")
    for s in st["scores"][:5]:
        print(f"  {s['symbol']:8s} score {s['score']:6.2f}  "
              f"${s['price_usd']:,.2f}  via {s['price_source']}")
    pf = st["portfolio"]
    print(f"Portfolio: ${pf['total_value_usd']:,.2f} total "
          f"(cash ${pf['cash_usd']:,.2f}, {len(pf['positions'])} positions)")
    print(f"Decisions this cycle: {len(st['decisions'])} (last 20 in state.json)")
    return 0


def cmd_score(args) -> int:
    uni = universe_mod.fetch_universe(refresh=args.refresh)
    feats = signals.gather_signals(uni["tokens"])
    scores = research.score_tokens(feats["tokens"])
    print("Top 10 scored stocks")
    print("score = 0.4*onchain + 0.3*momentum + 0.3*market "
          "(percentile ranks within the scored universe)")
    for s in scores[:10]:
        c = s["components"]
        print(f"{s['symbol']:8s} {s['score']:6.2f}  "
              f"onchain {c['onchain']:5.1f} momentum {c['momentum']:5.1f} "
              f"market {c['market']:5.1f}  ${s['price_usd']:,.2f}  {s['price_source']}")
        for r in s["reasons"]:
            print(f"           - {r}")
    if feats["unscored"]:
        print(f"\nUnscored ({len(feats['unscored'])}): "
              + ", ".join(u["symbol"] for u in feats["unscored"][:10]))
    return 0


def cmd_portfolio(args) -> int:
    st = state_mod.load_state()
    if not st:
        print("No portfolio yet — run `python -m stocksage run` first.")
        return 1
    pf = st["portfolio"]
    print(f"Portfolio as of {st['as_of']}")
    print(f"Total value: ${pf['total_value_usd']:,.2f}   "
          f"Cash: ${pf['cash_usd']:,.2f} (paper only)")
    for p in pf["positions"]:
        print(f"  {p['symbol']:8s} {p['shares']:>12,.4f} shares @ "
              f"${p['price_usd']:,.2f} = ${p['value_usd']:,.2f} "
              f"({p['weight_pct']:.1f}%)")
    return 0


def cmd_decisions(args) -> int:
    decisions = state_mod.load_decisions()
    if not decisions:
        print("No decisions yet — run `python -m stocksage run` first.")
        return 1
    for d in decisions[-args.limit:]:
        print(f"{d['ts']}  {d['action']:8s} {d['symbol']:8s} "
              f"{d['from_weight_pct']:5.1f}% -> {d['to_weight_pct']:5.1f}%  "
              f"score {d.get('score')}  {d['reason']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stocksage",
                                     description="StockSage — paper-trading agent for Base tokenized stocks")
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="run one full live cycle")
    p_run.add_argument("--refresh", action="store_true", help="force universe refresh")
    p_run.set_defaults(func=cmd_run)
    p_score = sub.add_parser("score", help="print top 10 scores with components")
    p_score.add_argument("--refresh", action="store_true", help="force universe refresh")
    p_score.set_defaults(func=cmd_score)
    p_pf = sub.add_parser("portfolio", help="print the paper portfolio")
    p_pf.set_defaults(func=cmd_portfolio)
    p_dec = sub.add_parser("decisions", help="print the decision log")
    p_dec.add_argument("--limit", type=int, default=20)
    p_dec.set_defaults(func=cmd_decisions)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
