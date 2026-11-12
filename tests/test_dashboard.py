"""Tests for the StockSage dashboard (stdlib unittest only).

Run from the repo root:  python -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stocksage import dashboard  # noqa: E402


def make_state() -> dict:
    return {
        "as_of": "2026-11-12T17:00:00Z",
        "universe": {"count": 338, "minted": 72},
        "scores": [
            {
                "address": "0xb20000000000000000000078ee7ce2fE4908108C",
                "symbol": "NVDAc",
                "name": "NVIDIA Corporation",
                "score": 90.2,
                "components": {"onchain": 92, "momentum": 88, "market": 90},
                "price_usd": 165.043,
                "price_source": "DexScreener",
                "liquidity_usd": 1303058,
                "volume_24h_usd": 10177386,
                "supply": 46822.04,
                "multiplier": 1.0005379395763696,
                "reasons": ["Deepest stock-token pool on Base."],
            }
        ],
        "portfolio": {
            "cash_usd": 12450.0,
            "total_value_usd": 100000.0,
            "positions": [
                {
                    "symbol": "NVDAc",
                    "address": "0xb20000000000000000000078ee7ce2fE4908108C",
                    "shares": 151.03,
                    "price_usd": 165.043,
                    "value_usd": 25000.0,
                    "weight_pct": 25.0,
                }
            ],
        },
        "decisions": [
            {
                "ts": "2026-11-12T16:30:00Z",
                "type": "rebalance",
                "action": "increase",
                "symbol": "NVDAc",
                "from_weight_pct": 18.0,
                "to_weight_pct": 25.0,
                "reason": "NVDAc leads the universe on all three components.",
                "score": 90.2,
            }
        ],
    }


class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        self.server = None
        self.thread = None

    def tearDown(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join(timeout=5)
        self.tmp.cleanup()

    def start_server(self, sample: bool = False):
        self.server = dashboard.create_server(self.data_dir, port=0, sample=sample)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def get(self, url: str):
        """GET returning (status, content-type, body). HTTP errors included."""
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.status, resp.headers.get("Content-Type", ""), resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.headers.get("Content-Type", ""), exc.read()

    def test_index_serves_200(self):
        (self.data_dir / "state.json").write_text(json.dumps(make_state()))
        base = self.start_server()
        status, ctype, body = self.get(base + "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"StockSage", body)
        self.assertIn(b"Why this score", body)
        self.assertIn(b"How scoring works", body)

    def test_status_returns_json_when_state_present(self):
        (self.data_dir / "state.json").write_text(json.dumps(make_state()))
        base = self.start_server()
        status, ctype, body = self.get(base + "/api/status")
        self.assertEqual(status, 200)
        self.assertIn("application/json", ctype)
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["source"], "live")
        self.assertEqual(payload["as_of"], "2026-11-12T17:00:00Z")
        self.assertEqual(payload["universe"], {"count": 338, "minted": 72})

    def test_api_endpoints_return_state_data(self):
        state = make_state()
        (self.data_dir / "state.json").write_text(json.dumps(state))
        base = self.start_server()
        for path, key in (("/api/scores", "scores"),
                          ("/api/portfolio", "portfolio"),
                          ("/api/decisions", "decisions")):
            status, _, body = self.get(base + path)
            self.assertEqual(status, 200, path)
            payload = json.loads(body)
            self.assertIn(key, payload)
        scores = json.loads(self.get(base + "/api/scores")[2])["scores"]
        self.assertEqual(scores[0]["symbol"], "NVDAc")
        self.assertEqual(scores[0]["score"], 90.2)

    def test_api_returns_503_when_state_absent(self):
        # No state.json in the data dir at all.
        base = self.start_server()
        for path in ("/api/status", "/api/scores", "/api/portfolio", "/api/decisions"):
            status, _, body = self.get(base + path)
            if path == "/api/status":
                # /api/status always answers 200 with ok=false.
                self.assertEqual(status, 200, path)
                payload = json.loads(body)
                self.assertFalse(payload["ok"])
                self.assertIn("No live state yet", payload["message"])
            else:
                self.assertEqual(status, 503, path)
                payload = json.loads(body)
                self.assertIn("error", payload)
                self.assertIn("No live state yet", payload["error"])

    def test_index_still_serves_without_state(self):
        base = self.start_server()
        status, _, body = self.get(base + "/")
        self.assertEqual(status, 200)
        self.assertIn(b"StockSage", body)

    def test_sample_mode_serves_labelled_sample(self):
        sample = make_state()
        sample["sample"] = True
        sample["sample_note"] = "SAMPLE DATA — not live."
        (self.data_dir / "sample-state.json").write_text(json.dumps(sample))
        base = self.start_server(sample=True)
        status, _, body = self.get(base + "/api/status")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["source"], "sample")
        self.assertIn("SAMPLE DATA", payload["message"])


if __name__ == "__main__":
    unittest.main()
