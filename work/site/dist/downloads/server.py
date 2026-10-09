"""Local, non-persistent rule review API. Python standard library only."""

from __future__ import annotations

import argparse
import json
import math
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS = ROOT / "work" / "outputs" / "capstone_metrics.json"
MAX_BODY_BYTES = 32_768
MAX_PAGES = 50
PAGE_ID = re.compile(r"page_[A-Za-z0-9_-]{1,40}\Z")
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000", "http://localhost:8000",
    "http://127.0.0.1:8080", "http://localhost:8080",
    "http://127.0.0.1:5500", "http://localhost:5500",
}
METRIC_KEYS = {
    "rows", "base_rate", "majority_class_accuracy", "roc_auc", "average_precision",
    "precision_at_50", "precision_at_100", "precision_at_250",
    "lift_at_50_vs_base_rate", "lift_at_100_vs_base_rate", "lift_at_250_vs_base_rate",
}


class RequestError(ValueError):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code = status, code


def _json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Non-finite JSON number")


def decode_json(raw: bytes):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_json_pairs,
                      parse_constant=_reject_constant)


def _number(page: dict, field: str, upper: float, integer: bool = False):
    value = page.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RequestError(422, "invalid_signal", f"{field} must be a number.")
    if value < 0 or value > upper or not math.isfinite(value):
        raise RequestError(422, "invalid_signal", f"{field} is outside its allowed range.")
    if integer and (not isinstance(value, int)):
        raise RequestError(422, "invalid_signal", f"{field} must be a JSON integer.")
    return value


def review_priorities(payload):
    if not isinstance(payload, dict) or set(payload) != {"pages"}:
        raise RequestError(422, "invalid_schema", "Body must contain only a pages array.")
    pages = payload["pages"]
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        raise RequestError(422, "invalid_schema", "Supply between 1 and 50 pages.")
    required = {"page_id", "impressions_90d", "ctr_pct", "avg_position", "days_since_last_update"}
    allowed = required | {"word_count"}
    seen, ranked = set(), []
    for page in pages:
        if not isinstance(page, dict) or not required <= set(page) or not set(page) <= allowed:
            raise RequestError(422, "invalid_schema", "A page has missing or unsupported fields.")
        page_id = page["page_id"]
        if not isinstance(page_id, str) or not PAGE_ID.fullmatch(page_id):
            raise RequestError(422, "unsafe_id", "Use synthetic page_ IDs; names and URLs are not accepted.")
        if page_id in seen:
            raise RequestError(422, "duplicate_id", "Page IDs must be unique in a request.")
        seen.add(page_id)
        impressions = _number(page, "impressions_90d", 1_000_000_000, integer=True)
        ctr = _number(page, "ctr_pct", 100)
        position = _number(page, "avg_position", 100)
        age = _number(page, "days_since_last_update", 36_500, integer=True)
        words = page.get("word_count")
        if words is not None:
            words = _number(page, "word_count", 1_000_000, integer=True)

        exposure = min(impressions / 10_000, 1)
        freshness = min(age / 365, 1)
        ctr_gap = max(0, (2 - ctr) / 2) if 1 <= position <= 20 else 0
        depth_gap = max(0, (1200 - words) / 1200) if words is not None and words > 0 else 0
        score = round(100 * exposure * (.4 + .3 * freshness + .2 * ctr_gap + .1 * depth_gap), 3)
        eligible = impressions >= 500 and position > 0
        reasons = []
        if impressions >= 500:
            reasons.append("sufficient_search_volume")
        else:
            reasons.append("low_volume_monitor")
        if position == 0:
            reasons.append("position_unavailable")
        if impressions >= 500 and age >= 180:
            reasons.append("stale_visible_page")
        if eligible and 1 <= position <= 20 and ctr < 2:
            reasons.append("low_ctr_with_strong_position")
        if eligible and words is not None and 0 < words < 1200:
            reasons.append("thin_visible_page")
        if words is None:
            reasons.append("word_count_unavailable")
        ranked.append({"page_id": page_id, "review_score": score,
                       "action": "review" if eligible else "monitor",
                       "eligible_for_review": eligible, "reason_codes": reasons})
    # Eligible review pages precede monitor-only pages, then score, then ID for stable ties.
    ranked.sort(key=lambda row: (not row["eligible_for_review"], -row["review_score"], row["page_id"]))
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank
    return {
        "method": "transparent_fixed_rule_v1",
        "scope": "Local demonstration; unvalidated editorial decision support, not a trained model or forecast.",
        "rate_unit": "percentage points: ctr_pct=0.4 means 0.4%",
        "count": len(ranked), "recommendations": ranked,
    }


def aggregate_metrics(path: Path):
    try:
        if path.stat().st_size > 1_000_000:
            raise ValueError("Metrics file too large")
        data = decode_json(path.read_bytes())
        if not isinstance(data, dict) or not isinstance(data.get("test_metrics"), dict):
            raise ValueError("Unrecognized metrics format")
        safe_metrics = {}
        allowed_models = {"rule_baseline", "logistic_regression", "random_forest"}
        for name, metrics in data["test_metrics"].items():
            if name not in allowed_models or not isinstance(metrics, dict):
                continue
            safe = {}
            for key, value in metrics.items():
                if key not in METRIC_KEYS:
                    continue
                if value is None:
                    safe[key] = None
                elif isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                    safe[key] = value
                else:
                    raise ValueError("Invalid aggregate metric")
            safe_metrics[name] = safe
        if not safe_metrics:
            raise ValueError("No aggregate metrics")
        selected = data.get("selected_model")
        if selected not in allowed_models:
            raise ValueError("Unknown selected model")
        return {"scope": "starter snapshot; current proxy label, not future decline or causal benefit",
                "selected_model": selected, "test_metrics": safe_metrics}
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        raise RequestError(503, "metrics_unavailable", "Run the capstone analysis to create valid aggregate metrics.") from None


class ReviewHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "FlyRankLocalReview/1"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(3)

    def log_message(self, *_):
        # Never log request paths, payloads, IDs or client-origin details.
        pass

    def _respond(self, status, payload):
        body = json.dumps(payload, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def _error(self, error):
        self._respond(error.status, {"error": {"code": error.code, "message": str(error)}})

    def do_GET(self):
        path = urlsplit(self.path).path
        try:
            if path == "/health":
                self._respond(200, {"status": "ok", "service": "local-review-api", "persistence": "none"})
            elif path == "/api/v1/metrics":
                self._respond(200, aggregate_metrics(self.server.metrics_path))
            elif path == "/api/v1/review-priorities":
                raise RequestError(405, "method_not_allowed", "Use POST for review priorities.")
            else:
                raise RequestError(404, "not_found", "Endpoint not found.")
        except RequestError as error:
            self._error(error)

    def do_POST(self):
        try:
            if urlsplit(self.path).path != "/api/v1/review-priorities":
                raise RequestError(404, "not_found", "Endpoint not found.")
            if self.headers.get("Transfer-Encoding"):
                raise RequestError(400, "unsupported_transfer", "Chunked request bodies are not supported.")
            lengths = self.headers.get_all("Content-Length", [])
            if not lengths:
                raise RequestError(411, "length_required", "Content-Length is required.")
            if len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,10}", lengths[0]):
                raise RequestError(400, "invalid_length", "Supply one valid Content-Length.")
            length = int(lengths[0])
            if length > MAX_BODY_BYTES:
                raise RequestError(413, "body_too_large", "Body exceeds 32768 bytes.")
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise RequestError(415, "unsupported_media_type", "Use application/json.")
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("Truncated body")
                payload = decode_json(raw)
            except (UnicodeError, ValueError, OverflowError, RecursionError):
                raise RequestError(400, "invalid_json", "Body must be valid finite JSON without duplicate keys.") from None
            except TimeoutError:
                raise RequestError(408, "request_timeout", "Request body did not arrive in time.") from None
            self._respond(200, review_priorities(payload))
        except RequestError as error:
            self._error(error)

    def do_OPTIONS(self):
        if urlsplit(self.path).path != "/api/v1/review-priorities":
            return self._error(RequestError(404, "not_found", "Endpoint not found."))
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            return self._error(RequestError(403, "origin_not_allowed", "This demo allows documented local web origins only."))
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True


class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, metrics_path=DEFAULT_METRICS):
        self.metrics_path = Path(metrics_path)
        super().__init__(address, ReviewHandler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    with ReviewServer((args.host, args.port), args.metrics) as server:
        print(f"Local review API listening on http://{args.host}:{args.port}; Ctrl+C stops it.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
