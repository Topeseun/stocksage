"""StockSage dashboard — standard library only.

Serves a single-page app (inline HTML/CSS/JS, no external assets) that
reads the state files written by the core engine:

    data/state.json      (scores, portfolio, recent decisions)
    data/decisions.jsonl (full rebalance history)

Run:  python -m stocksage dashboard [--port 8000] [--data-dir DIR] [--sample]

By default the dashboard reads data/state.json only. If that file does not
exist yet, the JSON endpoints return 503 with a clear message and the page
says so plainly. Pass --sample to preview the clearly-labelled sample file
(data/sample-state.json) instead — sample data is never presented as live.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "data"
STATE_FILE = "state.json"
SAMPLE_STATE_FILE = "sample-state.json"
DECISIONS_FILE = "decisions.jsonl"
SAMPLE_DECISIONS_FILE = "sample-decisions.jsonl"

NO_STATE_MSG = (
    "No live state yet — the core engine has not written data/state.json. "
    "Run `python -m stocksage run` first, or start the dashboard with "
    "--sample to preview the labelled sample data."
)


def resolve_data_dir(explicit: str | None) -> Path:
    """Data directory: explicit flag wins, then $STOCKSAGE_DATA_DIR, else repo data/."""
    if explicit:
        return Path(explicit)
    env = os.environ.get("STOCKSAGE_DATA_DIR")
    if env:
        return Path(env)
    return DEFAULT_DATA_DIR


def load_state(data_dir: Path, sample: bool = False) -> dict | None:
    """Load the state file. Returns None when it does not exist or is unreadable."""
    name = SAMPLE_STATE_FILE if sample else STATE_FILE
    path = data_dir / name
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict):
        return None
    return state


def load_decisions(data_dir: Path, state: dict | None, sample: bool = False) -> list:
    """Full rebalance history from decisions.jsonl, falling back to state['decisions']."""
    name = SAMPLE_DECISIONS_FILE if sample else DECISIONS_FILE
    path = data_dir / name
    rows: list = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    if rows:
        return rows
    if state and isinstance(state.get("decisions"), list):
        return list(state["decisions"])
    return []


def status_payload(data_dir: Path, sample: bool = False) -> dict:
    state = load_state(data_dir, sample=sample)
    if state is None:
        return {"ok": False, "source": "none", "state_exists": False,
                "message": NO_STATE_MSG}
    universe = state.get("universe") or {}
    return {
        "ok": True,
        "source": "sample" if sample or state.get("sample") else "live",
        "state_exists": True,
        "as_of": state.get("as_of"),
        "universe": universe,
        "scored": len(state.get("scores") or []),
        "positions": len((state.get("portfolio") or {}).get("positions") or []),
        "message": state.get("sample_note") if state.get("sample") else None,
    }


def make_handler(data_dir: Path, sample: bool = False):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # keep stdout clean
            pass

        # -- helpers ------------------------------------------------------
        def _send_json(self, status: int, payload) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _state_or_503(self):
            state = load_state(data_dir, sample=sample)
            if state is None:
                self._send_json(503, {"error": NO_STATE_MSG})
                return None
            return state

        # -- routing ------------------------------------------------------
        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                self._send_html(200, INDEX_HTML.encode("utf-8"))
            elif path == "/api/status":
                self._send_json(200, status_payload(data_dir, sample=sample))
            elif path == "/api/scores":
                state = self._state_or_503()
                if state is not None:
                    self._send_json(200, {
                        "as_of": state.get("as_of"),
                        "universe": state.get("universe"),
                        "scores": state.get("scores") or [],
                    })
            elif path == "/api/portfolio":
                state = self._state_or_503()
                if state is not None:
                    self._send_json(200, {
                        "as_of": state.get("as_of"),
                        "portfolio": state.get("portfolio") or {},
                    })
            elif path == "/api/decisions":
                state = self._state_or_503()
                if state is not None:
                    self._send_json(200, {
                        "as_of": state.get("as_of"),
                        "decisions": load_decisions(data_dir, state, sample=sample),
                    })
            else:
                self._send_json(404, {"error": f"Not found: {path}"})

    return Handler


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StockSage — Autonomous AI agent for tokenized stocks on Base</title>
<style>
  :root { --bg:#0d1117; --panel:#161b22; --line:#30363d; --text:#e6edf3;
          --muted:#8b949e; --accent:#2f81f7; --green:#3fb950; --amber:#d29922; --red:#f85149; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
         background:var(--bg); color:var(--text); }
  header { padding:20px 24px 12px; border-bottom:1px solid var(--line); }
  header h1 { margin:0; font-size:28px; }
  header h1 span { color:var(--accent); }
  header p { margin:6px 0 0; color:var(--muted); }
  .badges { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
  .badge { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px;
           border:1px solid var(--line); color:var(--muted); }
  .badge.live { color:var(--green); border-color:var(--green); }
  .badge.sample { color:var(--amber); border-color:var(--amber); }
  .badge.warn { color:var(--red); border-color:var(--red); }
  main { max-width:1100px; margin:0 auto; padding:16px 24px 40px; }
  nav.tabs { display:flex; gap:8px; margin:8px 0 16px; flex-wrap:wrap; }
  nav.tabs button { background:var(--panel); color:var(--text); border:1px solid var(--line);
    border-radius:8px; padding:8px 16px; font-size:14px; cursor:pointer; }
  nav.tabs button.active { background:var(--accent); border-color:var(--accent); color:#fff; }
  section.view { display:none; }
  section.view.active { display:block; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px 20px; margin-bottom:16px; }
  .card h2 { margin:0 0 8px; font-size:18px; }
  .card h3 { margin:0 0 6px; font-size:15px; }
  .card p, .card li { color:var(--muted); line-height:1.5; }
  .stat-grid { display:flex; gap:16px; flex-wrap:wrap; }
  .stat { flex:1; min-width:140px; }
  .stat .num { font-size:26px; font-weight:700; }
  .stat .lbl { color:var(--muted); font-size:13px; }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th, td { padding:8px 10px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }
  th { color:var(--muted); font-weight:600; cursor:pointer; white-space:nowrap; }
  th:hover { color:var(--text); }
  td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
  tr.detail-row td { background:#0d1117; }
  .bar { height:8px; border-radius:4px; background:#21262d; overflow:hidden; min-width:70px; }
  .bar > i { display:block; height:100%; background:var(--accent); }
  .bar.onchain > i { background:#a371f7; }
  .bar.momentum > i { background:var(--green); }
  .bar.market > i { background:var(--amber); }
  .score { font-weight:700; font-size:16px; }
  .why { color:var(--muted); font-size:13px; line-height:1.5; }
  .why ul { margin:6px 0 0; padding-left:18px; }
  .why-btn { background:none; border:1px solid var(--line); color:var(--accent);
    border-radius:6px; padding:3px 10px; font-size:12px; cursor:pointer; }
  .pill { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }
  .pill.increase, .pill.open { background:#1a3a24; color:var(--green); }
  .pill.decrease, .pill.close { background:#3d1d1d; color:var(--red); }
  .pill.hold { background:#2d2a16; color:var(--amber); }
  .mono { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:12px; word-break:break-all; }
  code { background:#21262d; padding:1px 5px; border-radius:4px; font-size:13px; }
  .empty { color:var(--muted); padding:24px; text-align:center; }
  footer { color:var(--muted); font-size:12px; text-align:center; padding:0 24px 24px; }
</style>
</head>
<body>
<header>
  <h1>Stock<span>Sage</span></h1>
  <p>An autonomous AI agent that researches, scores and rebalances tokenized stocks on Base.</p>
  <div class="badges">
    <span class="badge live" id="badge-live">● live Base data</span>
    <span class="badge sample" id="badge-sample" style="display:none">⚠ SAMPLE DATA — not live</span>
    <span class="badge warn" id="badge-none" style="display:none">No live state yet</span>
    <span class="badge" id="badge-asof">as of —</span>
    <span class="badge" id="badge-universe">universe —</span>
  </div>
</header>
<main>
  <nav class="tabs">
    <button data-view="research" class="active">Research</button>
    <button data-view="portfolio">Portfolio</button>
    <button data-view="decisions">Decisions</button>
    <button data-view="scoring">How scoring works</button>
  </nav>

  <section class="view active" id="view-research">
    <div class="card">
      <h2>Research — every scored stock</h2>
      <p>Click a column header to sort. Click “Why this score” to see the plain-language reasons behind a score.</p>
      <div id="scores-table"><p class="empty">Loading…</p></div>
    </div>
  </section>

  <section class="view" id="view-portfolio">
    <div class="card">
      <h2>Portfolio — paper trading</h2>
      <p>This is a <strong>paper portfolio</strong> starting at $100,000. No real money, no real trades, no signing. It exists to show what the agent would do.</p>
      <div id="portfolio-summary"><p class="empty">Loading…</p></div>
      <div id="portfolio-table"></div>
    </div>
  </section>

  <section class="view" id="view-decisions">
    <div class="card">
      <h2>Decisions — rebalance history</h2>
      <p>Every rebalance the agent made, with the reason written out in full. The newest decision is first.</p>
      <div id="decisions-table"><p class="empty">Loading…</p></div>
    </div>
  </section>

  <section class="view" id="view-scoring">
    <div class="card">
      <h2>How scoring works</h2>
      <p>Every tokenized stock in the universe gets one score from 0 to 100. The score is a weighted mix of three parts:</p>
      <p><code>score = 0.4 × on-chain + 0.3 × momentum + 0.3 × market</code></p>
      <ul>
        <li><strong>On-chain (40%)</strong> — what is happening on Base itself: tokens minted, holders, transfers and other activity the chain records.</li>
        <li><strong>Momentum (30%)</strong> — how the price has been moving recently, relative to the other stocks.</li>
        <li><strong>Market (30%)</strong> — how tradable it is: price source, liquidity and 24-hour trading volume.</li>
      </ul>
      <p>Each part is a <strong>percentile rank from 0 to 100 within the universe</strong> — a stock's on-chain value of 90 means it beats 90% of the other stocks on that part. So a score of 90 does not mean “90% good” in absolute terms; it means the stock ranks near the top of this universe, right now.</p>
      <h3>What happens next</h3>
      <p>The agent rebalances the paper portfolio toward the highest scores: it raises the weight of stocks whose scores rose, lowers or closes stocks whose scores fell, and writes down why for every change. The loop is research → score → rebalance, and it repeats on every run.</p>
      <h3>Data sources</h3>
      <p>Coinbase Tokenized Stocks API (the list of stocks and supplies), public Base RPC (on-chain reads), DexScreener (DEX prices, liquidity, volume) and Chainlink price feeds (NAV reference prices). All free, all keyless.</p>
    </div>
  </section>
</main>
<footer>StockSage — paper trading only. Not investment advice. Tokenized stocks are only available outside the U.S.</footer>

<script>
let scores = [];
let sortKey = "score", sortDir = -1;

const fmtUsd = v => v == null ? "—" : "$" + Number(v).toLocaleString("en-US", {maximumFractionDigits: 2});
const fmtNum = v => v == null ? "—" : Number(v).toLocaleString("en-US", {maximumFractionDigits: 2});
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function fetchJson(url) {
  const r = await fetch(url);
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.error || ("HTTP " + r.status)); }
  return r.json();
}

function bar(cls, v) {
  return '<div class="bar ' + cls + '" title="' + (v ?? "—") + '"><i style="width:' + (v ?? 0) + '%"></i></div>';
}

function renderScores() {
  const rows = [...scores].sort((a, b) => {
    const av = a[sortKey], bv = b[sortKey];
    if (av == null && bv == null) return 0;
    if (av == null) return 1; if (bv == null) return -1;
    return (av < bv ? -1 : av > bv ? 1 : 0) * sortDir;
  });
  let h = '<table><thead><tr>'
    + '<th data-k="symbol">Symbol</th><th data-k="name">Name</th>'
    + '<th data-k="score" class="num">Score</th>'
    + '<th>On-chain</th><th>Momentum</th><th>Market</th>'
    + '<th data-k="price_usd" class="num">Price</th><th>Source</th>'
    + '<th data-k="liquidity_usd" class="num">Liquidity</th>'
    + '<th data-k="volume_24h_usd" class="num">Vol 24h</th>'
    + '<th data-k="supply" class="num">Supply</th><th></th></tr></thead><tbody>';
  rows.forEach((s, i) => {
    const c = s.components || {};
    h += '<tr><td><strong>' + esc(s.symbol) + '</strong></td><td>' + esc(s.name) + '</td>'
      + '<td class="num score">' + (s.score ?? "—") + '</td>'
      + '<td>' + bar("onchain", c.onchain) + ' ' + (c.onchain ?? "—") + '</td>'
      + '<td>' + bar("momentum", c.momentum) + ' ' + (c.momentum ?? "—") + '</td>'
      + '<td>' + bar("market", c.market) + ' ' + (c.market ?? "—") + '</td>'
      + '<td class="num">' + fmtUsd(s.price_usd) + '</td><td>' + esc(s.price_source) + '</td>'
      + '<td class="num">' + fmtUsd(s.liquidity_usd) + '</td>'
      + '<td class="num">' + fmtUsd(s.volume_24h_usd) + '</td>'
      + '<td class="num">' + fmtNum(s.supply) + '</td>'
      + '<td><button class="why-btn" data-i="' + i + '">Why this score</button></td></tr>'
      + '<tr class="detail-row" id="why-' + i + '" style="display:none"><td colspan="12"><div class="why">'
      + '<strong>' + esc(s.symbol) + ' — ' + esc(s.name) + '</strong><br>'
      + 'Score ' + (s.score ?? "—") + ' = 0.4 × on-chain ' + (c.onchain ?? "—")
      + ' + 0.3 × momentum ' + (c.momentum ?? "—")
      + ' + 0.3 × market ' + (c.market ?? "—") + '.<br>'
      + '<span class="mono">' + esc(s.address) + '</span> · multiplier ' + (s.multiplier ?? "—")
      + '<ul>' + (s.reasons || []).map(r => '<li>' + esc(r) + '</li>').join("") + '</ul>'
      + '</div></td></tr>';
  });
  h += '</tbody></table>';
  document.getElementById("scores-table").innerHTML = h;
  document.querySelectorAll("#scores-table th[data-k]").forEach(th => {
    th.onclick = () => {
      const k = th.dataset.k;
      if (sortKey === k) sortDir *= -1; else { sortKey = k; sortDir = k === "symbol" ? 1 : -1; }
      renderScores();
    };
  });
  document.querySelectorAll(".why-btn").forEach(b => {
    b.onclick = () => {
      const row = document.getElementById("why-" + b.dataset.i);
      const open = row.style.display !== "none";
      row.style.display = open ? "none" : "";
      b.textContent = open ? "Why this score" : "Hide";
    };
  });
}

function renderPortfolio(p) {
  const pos = p.positions || [];
  document.getElementById("portfolio-summary").innerHTML =
    '<div class="stat-grid">'
    + '<div class="stat"><div class="num">' + fmtUsd(p.total_value_usd) + '</div><div class="lbl">Total value (paper)</div></div>'
    + '<div class="stat"><div class="num">' + fmtUsd(p.cash_usd) + '</div><div class="lbl">Cash</div></div>'
    + '<div class="stat"><div class="num">' + pos.length + '</div><div class="lbl">Positions</div></div></div>';
  let h = '<table><thead><tr><th>Symbol</th><th class="num">Shares</th><th class="num">Price</th>'
    + '<th class="num">Value</th><th class="num">Weight</th><th>Weight</th></tr></thead><tbody>';
  pos.forEach(x => {
    h += '<tr><td><strong>' + esc(x.symbol) + '</strong></td>'
      + '<td class="num">' + fmtNum(x.shares) + '</td><td class="num">' + fmtUsd(x.price_usd) + '</td>'
      + '<td class="num">' + fmtUsd(x.value_usd) + '</td><td class="num">' + (x.weight_pct ?? "—") + '%</td>'
      + '<td>' + bar("", x.weight_pct) + '</td></tr>';
  });
  h += '</tbody></table>';
  document.getElementById("portfolio-table").innerHTML = h;
}

function renderDecisions(list) {
  const rows = [...list].reverse();
  if (!rows.length) { document.getElementById("decisions-table").innerHTML = '<p class="empty">No rebalance decisions yet.</p>'; return; }
  let h = '<table><thead><tr><th>Time</th><th>Action</th><th>Symbol</th><th class="num">From → To</th><th class="num">Score</th><th>Reason (verbatim)</th></tr></thead><tbody>';
  rows.forEach(d => {
    h += '<tr><td>' + esc(d.ts) + '</td><td><span class="pill ' + esc(d.action) + '">' + esc(d.action) + '</span></td>'
      + '<td><strong>' + esc(d.symbol) + '</strong></td>'
      + '<td class="num">' + (d.from_weight_pct ?? "—") + '% → ' + (d.to_weight_pct ?? "—") + '%</td>'
      + '<td class="num">' + (d.score ?? "—") + '</td><td>' + esc(d.reason) + '</td></tr>';
  });
  h += '</tbody></table>';
  document.getElementById("decisions-table").innerHTML = h;
}

function showNoState(msg) {
  document.getElementById("badge-live").style.display = "none";
  document.getElementById("badge-none").style.display = "";
  document.getElementById("badge-asof").textContent = "as of —";
  const note = '<p class="empty">' + esc(msg) + '</p>';
  document.getElementById("scores-table").innerHTML = note;
  document.getElementById("portfolio-summary").innerHTML = note;
  document.getElementById("decisions-table").innerHTML = note;
}

async function load() {
  try {
    const st = await fetchJson("/api/status");
    if (!st.ok) { showNoState(st.message || "No live state yet."); return; }
    const isSample = st.source === "sample";
    document.getElementById("badge-live").style.display = isSample ? "none" : "";
    document.getElementById("badge-sample").style.display = isSample ? "" : "none";
    document.getElementById("badge-asof").textContent = "as of " + (st.as_of || "—");
    const u = st.universe || {};
    document.getElementById("badge-universe").textContent =
      "universe " + (u.count ?? "—") + " tokens · " + (u.minted ?? "—") + " minted";
    const [sc, pf, dc] = await Promise.all([
      fetchJson("/api/scores"), fetchJson("/api/portfolio"), fetchJson("/api/decisions")]);
    scores = sc.scores || [];
    renderScores();
    renderPortfolio(pf.portfolio || {});
    renderDecisions(dc.decisions || []);
  } catch (e) {
    showNoState(String(e.message || e));
  }
}

document.querySelectorAll("nav.tabs button").forEach(b => {
  b.onclick = () => {
    document.querySelectorAll("nav.tabs button").forEach(x => x.classList.remove("active"));
    document.querySelectorAll("section.view").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    document.getElementById("view-" + b.dataset.view).classList.add("active");
  };
});
load();
</script>
</body>
</html>
"""


def create_server(data_dir: Path, port: int = 8000, sample: bool = False) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(data_dir, sample=sample))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stocksage dashboard",
                                     description="StockSage dashboard (stdlib http.server).")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--data-dir", default=None,
                        help="Directory holding state.json / decisions.jsonl "
                             "(default: repo data/; or $STOCKSAGE_DATA_DIR)")
    parser.add_argument("--sample", action="store_true",
                        help="Serve the clearly-labelled sample state "
                             "(data/sample-state.json) instead of live state.")
    args = parser.parse_args(argv)
    data_dir = resolve_data_dir(args.data_dir)
    server = create_server(data_dir, port=args.port, sample=args.sample)
    state = load_state(data_dir, sample=args.sample)
    print(f"StockSage dashboard at http://127.0.0.1:{args.port}/")
    print(f"Data dir: {data_dir}  (source: {'sample' if args.sample else 'live'})")
    if state is None:
        print("NOTE: " + NO_STATE_MSG)
    else:
        print(f"State loaded: as of {state.get('as_of')}, "
              f"{len(state.get('scores') or [])} scored stocks.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
