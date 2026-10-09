"""Integration tests use real loopback HTTP requests, ephemeral ports and synthetic data."""

import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from server import MAX_BODY_BYTES, ReviewServer

PAGE = {"page_id": "page_demo_001", "impressions_90d": 1200, "ctr_pct": .4,
        "avg_position": 8, "days_since_last_update": 220, "word_count": 850}


class APIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.metrics_path = Path(self.temp.name) / "metrics.json"
        self.server = ReviewServer(("127.0.0.1", 0), self.metrics_path)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)
        self.temp.cleanup()

    def request(self, method, path="/api/v1/review-priorities", payload=None, raw=None, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        body = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        connection.request(method, path, body=body, headers=hdrs)
        response = connection.getresponse()
        content = response.read()
        result = (response.status, json.loads(content) if content else None, dict(response.getheaders()))
        connection.close()
        return result

    def test_health_has_no_persistence(self):
        status, body, headers = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["persistence"], "none")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_deterministic_ranking_and_known_score(self):
        second = dict(PAGE, page_id="page_demo_002", impressions_90d=20)
        payload = {"pages": [second, PAGE]}
        first = self.request("POST", payload=payload)
        repeated = self.request("POST", payload=payload)
        self.assertEqual(first[0], 200)
        self.assertEqual(first[1], repeated[1])
        recommendations = first[1]["recommendations"]
        self.assertEqual(recommendations[0]["page_id"], PAGE["page_id"])
        self.assertEqual(recommendations[0]["review_score"], 9.24)
        self.assertEqual(recommendations[1]["action"], "monitor")
        self.assertEqual(first[1]["method"], "transparent_fixed_rule_v1")
        self.assertIn("stale_visible_page", recommendations[0]["reason_codes"])
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_stable_ties_and_eligibility_boundary(self):
        pages = [dict(PAGE, page_id="page_z", impressions_90d=500),
                 dict(PAGE, page_id="page_a", impressions_90d=500),
                 dict(PAGE, page_id="page_low", impressions_90d=499),
                 dict(PAGE, page_id="page_unknown", avg_position=0)]
        status, result, _ = self.request("POST", payload={"pages": pages})
        self.assertEqual(status, 200)
        rows = result["recommendations"]
        self.assertEqual([row["page_id"] for row in rows[:2]], ["page_a", "page_z"])
        self.assertTrue(all(row["eligible_for_review"] for row in rows[:2]))
        self.assertTrue(all(row["action"] == "monitor" for row in rows[2:]))
        unknown = next(row for row in rows if row["page_id"] == "page_unknown")
        self.assertIn("position_unavailable", unknown["reason_codes"])

    def test_numeric_limits_and_optional_missing_words(self):
        pages = [dict(PAGE, impressions_90d=0, ctr_pct=0, avg_position=0,
                      days_since_last_update=0, word_count=None),
                 dict(PAGE, page_id="page_max", impressions_90d=1_000_000_000,
                      ctr_pct=100, avg_position=100, days_since_last_update=36_500, word_count=1_000_000)]
        status, result, _ = self.request("POST", payload={"pages": pages})
        self.assertEqual(status, 200)
        self.assertTrue(all(0 <= row["review_score"] <= 100 for row in result["recommendations"]))
        self.assertEqual(next(row for row in result["recommendations"] if row["page_id"] == PAGE["page_id"])["review_score"], 0)

    def test_unsafe_duplicate_and_extra_fields_rejected(self):
        cases = [({"pages": [dict(PAGE, page_id="https://example.test")]}, "unsafe_id"),
                 ({"pages": [PAGE, PAGE]}, "duplicate_id"),
                 ({"pages": [dict(PAGE, title="private text")]}, "invalid_schema"),
                 ({"pages": [PAGE], "client_name": "not allowed"}, "invalid_schema")]
        for payload, code in cases:
            with self.subTest(code=code):
                status, result, _ = self.request("POST", payload=payload)
                self.assertEqual(status, 422)
                self.assertEqual(result["error"]["code"], code)
                self.assertNotIn("private text", json.dumps(result))

    def test_bad_numbers_and_types_rejected(self):
        changes = [{"impressions_90d": True}, {"impressions_90d": 2.5}, {"ctr_pct": -1},
                   {"ctr_pct": 100.001}, {"avg_position": 101}, {"word_count": "850"},
                   {"days_since_last_update": 36_501}, {"impressions_90d": 1_000_000_001},
                   {"impressions_90d": 10 ** 400}, {"ctr_pct": float("inf")}]
        for change in changes:
            with self.subTest(change=change):
                expected = 400 if change.get("ctr_pct") == float("inf") else 422
                self.assertEqual(self.request("POST", payload={"pages": [dict(PAGE, **change)]})[0], expected)

    def test_page_count_limits(self):
        self.assertEqual(self.request("POST", payload={"pages": []})[0], 422)
        self.assertEqual(self.request("POST", payload={"pages": "bad"})[0], 422)
        fifty = [dict(PAGE, page_id=f"page_{index}") for index in range(50)]
        self.assertEqual(self.request("POST", payload={"pages": fifty})[0], 200)
        self.assertEqual(self.request("POST", payload={"pages": fifty + [dict(PAGE, page_id="page_51")]})[0], 422)

    def test_malformed_duplicate_and_nonfinite_json_rejected(self):
        for raw in [b"not JSON", b'{"pages":[],"pages":[]}', b'{"pages":[NaN]}',
                    b'{"pages":[Infinity]}', b'\xff', b'{"pages":']:
            with self.subTest(raw=raw):
                status, body, _ = self.request("POST", raw=raw)
                self.assertEqual(status, 400)
                self.assertEqual(body["error"]["code"], "invalid_json")

    def test_body_limit_and_content_type(self):
        self.assertEqual(self.request("POST", raw=b" " * (MAX_BODY_BYTES + 1))[0], 413)
        self.assertEqual(self.request("POST", payload={"pages": [PAGE]},
                                      headers={"Content-Type": "text/plain"})[0], 415)

    def test_missing_duplicate_length_and_chunked_rejected(self):
        for headers, expected in [([], 411), ([("Content-Length", "-1")], 400),
                                  ([("Content-Length", "0"), ("Content-Length", "0")], 400),
                                  ([("Transfer-Encoding", "chunked")], 400)]:
            with self.subTest(headers=headers):
                connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
                connection.putrequest("POST", "/api/v1/review-priorities")
                connection.putheader("Content-Type", "application/json")
                for key, value in headers:
                    connection.putheader(key, value)
                connection.endheaders()
                response = connection.getresponse()
                self.assertEqual(response.status, expected)
                response.read()
                connection.close()

    def test_wrong_route_method_and_cors(self):
        self.assertEqual(self.request("GET", "/unknown")[0], 404)
        self.assertEqual(self.request("GET")[0], 405)
        self.assertEqual(self.request("OPTIONS", headers={"Origin": "https://untrusted.example"})[0], 403)
        status, _, headers = self.request("OPTIONS", headers={"Origin": "http://127.0.0.1:8000"})
        self.assertEqual(status, 204)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://127.0.0.1:8000")

    def test_metrics_unavailable_corrupt_and_safe_allowlist(self):
        self.assertEqual(self.request("GET", "/api/v1/metrics")[0], 503)
        self.metrics_path.write_text("broken", encoding="utf-8")
        self.assertEqual(self.request("GET", "/api/v1/metrics")[0], 503)
        self.metrics_path.write_text(json.dumps({"selected_model": "random_forest",
            "private_rows": ["should not appear"], "test_metrics": {
                "rule_baseline": {"rows": 100, "base_rate": .3, "average_precision": .35},
                "random_forest": {"rows": 100, "average_precision": .6, "private_id": "should not appear"},
                "unsafe_name": {"rows": 100}}}), encoding="utf-8")
        status, body, _ = self.request("GET", "/api/v1/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(body["test_metrics"]["random_forest"], {"rows": 100, "average_precision": .6})
        self.assertNotIn("should not appear", json.dumps(body))
        self.assertNotIn("unsafe_name", body["test_metrics"])


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2, stream=sys.stdout))
