"""StockSage command line:  python -m stocksage <run|score|portfolio|decisions|dashboard>

The core engine subcommands (run, score, portfolio, decisions) are
implemented by the core engine package. The dashboard subcommand lives in
stocksage.dashboard and is wired here so `python -m stocksage dashboard`
works even before the core engine lands.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: python -m stocksage <run|score|portfolio|decisions|dashboard> [options]")
        print("  run         one full live cycle: research -> score -> rebalance")
        print("  score       score the universe and print the top stocks")
        print("  portfolio   show the paper portfolio")
        print("  decisions   show the rebalance history")
        print("  dashboard   start the web dashboard (see: python -m stocksage dashboard --help)")
        return 0 if argv else 2

    cmd, rest = argv[0], argv[1:]
    if cmd == "dashboard":
        from .dashboard import main as dashboard_main

        return dashboard_main(rest)
    if cmd in ("run", "score", "portfolio", "decisions"):
        try:
            from .cli import main as core_main
        except ImportError:
            print(f"Core engine not available yet: `python -m stocksage {cmd}` "
                  "needs the core engine (stocksage.cli), which has not landed. "
                  "The dashboard is available: `python -m stocksage dashboard --sample`.")
            return 1
        return core_main([cmd, *rest])
    print(f"Unknown subcommand: {cmd}")
    print("Usage: python -m stocksage <run|score|portfolio|decisions|dashboard>")
    return 2


if __name__ == "__main__":
    sys.exit(main())
