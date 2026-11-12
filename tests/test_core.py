"""Tests for the StockSage core engine (stdlib unittest only).

Run from the repo root:  python -m unittest discover -s tests -v
Covers: scoring math, portfolio target-weight math, rebalance decision
logging, universe dedupe / duplicate-address guard. No network calls.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stocksage import config, portfolio as pf, research, universe as uni_mod


def feat(symbol, score_hint, vol, txns, chg, liq, pools, price=100.0, supply=1000.0):
    return {
        "address": f"0xB20000000000000000000000000000000000{hash(symbol) % 10000:04d}",
        "symbol": symbol, "name": symbol, "supply": supply, "multiplier": 1.0,
        "price_usd": price, "price_source": "dexscreener:test",
        "liquidity_usd": liq, "volume_24h_usd": vol,
        "price_change_24h_pct": chg, "txns_24h": txns, "pool_count": pools,
        "low_liquidity": False, "nav_usd": None, "nav_deviation_pct": None,
        "unscored_reason": None,
    }


def scored_token(symbol, score, price=100.0):
    return {"address": f"0xaddr-{symbol}", "symbol": symbol, "name": symbol,
            "score": score, "components": {"onchain": score, "momentum": score, "market": score},
            "price_usd": price, "price_source": "dexscreener:test",
            "liquidity_usd": 10000.0, "volume_24h_usd": 1000.0,
            "supply": 1000.0, "multiplier": 1.0, "reasons": ["test"]}


class TestPercentileRank(unittest.TestCase):
    def test_bounds_and_monotonic(self):
        vals = [0, 10, 20, 30, 40]
        self.assertAlmostEqual(research.percentile_rank(vals, 0), 10.0)
        self.assertAlmostEqual(research.percentile_rank(vals, 40), 90.0)
        self.assertAlmostEqual(research.percentile_rank(vals, 20), 50.0)
        self.assertLess(research.percentile_rank(vals, 10),
                        research.percentile_rank(vals, 30))

    def test_single_value(self):
        self.assertEqual(research.percentile_rank([5], 5), 50.0)

    def test_empty(self):
        self.assertEqual(research.percentile_rank([], 5), 0.0)

    def test_all_equal(self):
        self.assertAlmostEqual(research.percentile_rank([7, 7, 7], 7), 50.0)


class TestScoring(unittest.TestCase):
    def _features(self):
        # Distinct values on every axis so ranks are unambiguous.
        return [
            feat("AAAAc", 0, vol=100, txns=10, chg=-10, liq=100, pools=1),
            feat("BBBBc", 0, vol=200, txns=20, chg=-5, liq=200, pools=2),
            feat("CCCCc", 0, vol=300, txns=30, chg=0, liq=300, pools=3),
            feat("DDDDc", 0, vol=400, txns=40, chg=5, liq=400, pools=4),
            feat("EEEEc", 0, vol=500, txns=50, chg=10, liq=500, pools=5),
        ]

    def test_scores_sorted_desc_and_bounded(self):
        out = research.score_tokens(self._features())
        self.assertEqual(len(out), 5)
        scores = [t["score"] for t in out]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for s in scores:
            self.assertGreaterEqual(s, 0.0)
            self.assertLessEqual(s, 100.0)
        self.assertEqual(out[0]["symbol"], "EEEEc")
        self.assertEqual(out[-1]["symbol"], "AAAAc")

    def test_weights_sum_and_formula(self):
        out = research.score_tokens(self._features())
        for t in out:
            c = t["components"]
            expected = (config.WEIGHT_ONCHAIN * c["onchain"]
                        + config.WEIGHT_MOMENTUM * c["momentum"]
                        + config.WEIGHT_MARKET * c["market"])
            self.assertAlmostEqual(t["score"], round(expected, 2), places=2)
            for v in c.values():
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 100.0)
        self.assertAlmostEqual(config.WEIGHT_ONCHAIN + config.WEIGHT_MOMENTUM
                               + config.WEIGHT_MARKET, 1.0)

    def test_momentum_clipping(self):
        # A +1000% token and a +25% token must rank identically on momentum
        # (both clip to +20) — clipping stops one outlier stretching the scale.
        feats = [
            feat("LOWc", 0, vol=100, txns=10, chg=0, liq=100, pools=1),
            feat("MIDc", 0, vol=100, txns=10, chg=25, liq=100, pools=1),
            feat("HIGc", 0, vol=100, txns=10, chg=1000, liq=100, pools=1),
        ]
        out = {t["symbol"]: t for t in research.score_tokens(feats)}
        self.assertEqual(out["MIDc"]["components"]["momentum"],
                         out["HIGc"]["components"]["momentum"])

    def test_reasons_present_and_bounded(self):
        out = research.score_tokens(self._features())
        for t in out:
            self.assertTrue(1 <= len(t["reasons"]) <= 3)
            self.assertTrue(all(isinstance(r, str) and r for r in t["reasons"]))

    def test_unpriced_token_unscored(self):
        feats = self._features()
        feats[0]["price_usd"] = None
        out = research.score_tokens(feats)
        self.assertEqual(len(out), 4)
        self.assertNotIn("AAAAc", [t["symbol"] for t in out])

    def test_no_features_no_scores(self):
        self.assertEqual(research.score_tokens([]), [])


class TestTargetWeights(unittest.TestCase):
    def test_proportional_above_floor(self):
        # Ten tokens, scores 60..51 -> excess 10..1, total 55; top weight
        # 10/55 = 18.18% (below the 25% cap, so no capping kicks in).
        scored = [scored_token(f"T{i}", 60 - i) for i in range(10)]
        w = pf.compute_target_weights(scored)
        self.assertAlmostEqual(w["0xaddr-T0"], 10 / 55 * 100, places=3)
        self.assertAlmostEqual(w["0xaddr-T9"], 1 / 55 * 100, places=3)
        self.assertAlmostEqual(sum(w.values()), 100.0, places=2)

    def test_score_floor(self):
        scored = [scored_token("A", 90), scored_token("B", 50), scored_token("C", 40)]
        w = pf.compute_target_weights(scored)
        self.assertEqual(list(w.keys()), ["0xaddr-A"])
        self.assertAlmostEqual(w["0xaddr-A"], 100.0 if False else 25.0, places=2)
        # Single token above floor is capped at 25%; the rest stays cash.

    def test_cap_25_redistributed(self):
        # Ten tokens, one dominant: excess 50 vs nine x 5 -> uncapped
        # dominant would be 52.6%; capped at 25%, rest redistributed.
        scored = [scored_token("DOM", 100)] + [scored_token(f"T{i}", 55) for i in range(9)]
        w = pf.compute_target_weights(scored)
        self.assertLessEqual(max(w.values()), 25.0 + 1e-9)
        self.assertAlmostEqual(w["0xaddr-DOM"], 25.0, places=2)
        self.assertAlmostEqual(sum(w.values()), 100.0, places=2)

    def test_top_10_only(self):
        scored = [scored_token(f"T{i}", 90 - i) for i in range(15)]
        w = pf.compute_target_weights(scored)
        self.assertEqual(len(w), 10)

    def test_no_scores_above_floor(self):
        self.assertEqual(pf.compute_target_weights([scored_token("A", 50)]), {})
        self.assertEqual(pf.compute_target_weights([]), {})


class TestRebalance(unittest.TestCase):
    def test_open_positions_first_cycle(self):
        scored = [scored_token("A", 90), scored_token("B", 70)]
        portfolio = pf.new_portfolio()
        decisions = pf.execute_rebalance(portfolio, scored, "2026-11-12T00:00:00Z")
        self.assertEqual(len(portfolio["positions"]), 2)
        self.assertTrue(all(d["action"] == "open" for d in decisions))
        self.assertAlmostEqual(portfolio["total_value_usd"], 100000.0, places=1)
        # Capped weights: A 25% (cap), B 25% (redistributed remainder is
        # capped too with only 2 tokens) -> cash holds the rest.
        self.assertLessEqual(max(p["weight_pct"] for p in portfolio["positions"]), 25.0)

    def test_min_trade_skips_small_rebalance(self):
        # Token already at ~target weight: a <5pp drift must be a hold.
        scored = [scored_token("A", 90, price=100.0)]
        portfolio = pf.new_portfolio()
        pf.execute_rebalance(portfolio, scored, "2026-11-12T00:00:00Z")
        # Second cycle, same scores/prices: no trade, only holds.
        decisions = pf.execute_rebalance(portfolio, scored, "2026-11-12T01:00:00Z")
        self.assertTrue(all(d["action"] == "hold" for d in decisions))
        self.assertEqual(len(portfolio["positions"]), 1)

    def test_rebalance_threshold(self):
        # Current 25% vs a much lower target: >=5pp -> decrease; a new
        # top-10 token opens. (Nine moderate tokens dilute A so the cap
        # redistribution cannot push A back up.)
        scored = [scored_token("A", 90, price=100.0)]
        portfolio = pf.new_portfolio()
        pf.execute_rebalance(portfolio, scored, "2026-11-12T00:00:00Z")
        scored2 = [scored_token("A", 51, price=100.0)] + [
            scored_token(f"B{i}", 60, price=100.0) for i in range(9)]
        decisions = pf.execute_rebalance(portfolio, scored2, "2026-11-12T01:00:00Z")
        actions = {d["symbol"]: d["action"] for d in decisions}
        self.assertEqual(actions.get("A"), "decrease")
        self.assertEqual(actions.get("B0"), "open")

    def test_close_when_leaving_top10(self):
        scored = [scored_token(f"T{i}", 90 - i) for i in range(10)]
        portfolio = pf.new_portfolio()
        pf.execute_rebalance(portfolio, scored, "2026-11-12T00:00:00Z")
        self.assertEqual(len(portfolio["positions"]), 10)
        # New top 10 excludes T9 entirely (score collapsed below floor).
        scored2 = [scored_token(f"T{i}", 90 - i) for i in range(9)] + [scored_token("NEW", 95)]
        decisions = pf.execute_rebalance(portfolio, scored2, "2026-11-12T01:00:00Z")
        actions = {d["symbol"]: d["action"] for d in decisions}
        self.assertEqual(actions.get("T9"), "close")
        self.assertNotIn("0xaddr-T9", [p["address"] for p in portfolio["positions"]])

    def test_decision_log_shape(self):
        scored = [scored_token("A", 90)]
        portfolio = pf.new_portfolio()
        decisions = pf.execute_rebalance(portfolio, scored, "2026-11-12T00:00:00Z")
        for d in decisions:
            self.assertEqual(set(d.keys()),
                             {"ts", "type", "action", "symbol",
                              "from_weight_pct", "to_weight_pct", "reason", "score"})
            self.assertEqual(d["type"], "rebalance")
            self.assertIn(d["action"], {"open", "increase", "decrease", "close", "hold"})
            self.assertTrue(d["reason"])  # plain-language reason, always present


class TestUniverse(unittest.TestCase):
    def _raw(self, symbol, address, supply=100.0):
        return {"contract_address": address, "symbol": symbol, "name": symbol,
                "total_supply": supply, "multiplier": 1}

    def test_duplicate_address_dropped(self):
        # The exact artefact from the research dump: two symbols, one address.
        raw = [
            self._raw("SONYc", "0xB2000000000000000000002137743D4a01Fe4e88", 3.93),
            self._raw("SOUNc", "0xB2000000000000000000002137743D4a01Fe4e88", 3.93),
            self._raw("NVDAc", "0xB20000000000000000000078ee7ce2fE4908108C", 46822.0),
        ]
        minted, dropped = uni_mod.build_universe(raw)
        self.assertEqual([t["symbol"] for t in minted], ["NVDAc"])
        self.assertEqual(len(dropped), 2)
        self.assertTrue(all("duplicate" in d["drop_reason"].lower() for d in dropped))

    def test_duplicate_address_case_insensitive(self):
        raw = [
            self._raw("PLTRc", "0xb2000000000000000000007d16372840dF4dAbbe", 2757.0),
            self._raw("MRVLc", "0xB2000000000000000000007D16372840DF4DABBE", 2757.0),
        ]
        minted, dropped = uni_mod.build_universe(raw)
        self.assertEqual(minted, [])
        self.assertEqual(len(dropped), 2)

    def test_same_symbol_repeat_not_a_drop(self):
        # Pagination repeat of the same token: deduped, not dropped.
        raw = [self._raw("NVDAc", "0xB20000000000000000000078ee7ce2fE4908108C", 46822.0),
               self._raw("NVDAc", "0xB20000000000000000000078ee7ce2fE4908108C", 46822.0)]
        minted, dropped = uni_mod.build_universe(raw)
        self.assertEqual(len(minted), 1)
        self.assertEqual(dropped, [])

    def test_unminted_excluded_not_dropped(self):
        raw = [self._raw("AALc", "0xB200000000000000000000000000000000000001", None),
               self._raw("ZZZc", "0xB200000000000000000000000000000000000002", 0)]
        minted, dropped = uni_mod.build_universe(raw)
        self.assertEqual(minted, [])
        self.assertEqual(dropped, [])

    def test_minted_kept_sorted(self):
        raw = [self._raw("TSLAc", "0xB2000000000000000000001e800a7f5189430cD0", 6288.0),
               self._raw("AAPLc", "0xB2000000000000000000003eF37a7c863DC1482A", 100.0)]
        minted, _ = uni_mod.build_universe(raw)
        self.assertEqual([t["symbol"] for t in minted], ["AAPLc", "TSLAc"])


if __name__ == "__main__":
    unittest.main()
