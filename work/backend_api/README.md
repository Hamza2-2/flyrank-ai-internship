# Hamza Afzal — local backend proof

This dependency-free Python REST API is a runnable Backend Development and Engineering portfolio feature. It turns small **synthetic** content-signal requests into a deterministic review queue, returns documented validation errors, and exposes a safe subset of the separately computed capstone metrics. It does not train a model, apply edits, persist requests, or predict future outcomes.

From the repository root:

```powershell
python work/backend_api/server.py
```

The default address is `http://127.0.0.1:8787`. Stop with Ctrl+C. In another terminal:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8787/health'
$demoBody = '{"pages":[{"page_id":"page_demo_001","impressions_90d":1200,"ctr_pct":0.4,"avg_position":8,"days_since_last_update":220,"word_count":850}]}'
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8787/api/v1/review-priorities' -ContentType 'application/json' -Body $demoBody
```

Run the integration tests from the repository root:

```powershell
python work/backend_api/test_api.py
```

Tests create an ephemeral loopback server and use real HTTP requests, not mocked handler calls. Synthetic fixtures cover deterministic ranking, score calculation, ties, eligibility thresholds, valid upper/lower bounds, optional missing word count, all request schema limits, unsafe/duplicate IDs, oversized/malformed/non-finite/duplicate-key JSON, missing/duplicate length, unsupported transfer/media type, CORS, routes/methods, and missing/corrupt/allowlisted aggregate metrics.

## Endpoints

| Method | Route | Behavior |
|---|---|---|
| GET | `/health` | `200` with service status and `persistence: none` |
| GET | `/api/v1/metrics` | `200` with whitelisted aggregate held-out capstone metrics; `503` until valid metrics exist |
| POST | `/api/v1/review-priorities` | `200` with ranked fixed-rule recommendations; request limits/schema are enforced |
| OPTIONS | `/api/v1/review-priorities` | Local browser-demo preflight for documented allowed origins |

The API contract is [openapi.json](openapi.json). Request fields are strict; unknown fields are rejected. All IDs must begin `page_` followed by 1–40 ASCII letters, digits, underscores or hyphens. Use synthetic IDs, not names, URLs or encoded private identifiers. Only 1–50 unique pages and at most 32,768 request-body bytes are accepted. JSON integer fields reject booleans and fractional values. Rates use percentage points: `ctr_pct = 0.4` means **0.4%**. Position 0 means unavailable; it receives no CTR opportunity bonus and the action is monitor.

Validation responses use a stable `{"error":{"code":"…","message":"…"}}` shape. Error messages do not echo submitted values. `400` means invalid JSON/framing, `408` body timeout, `411` missing Content-Length, `413` oversized body, `415` unsupported media type, and `422` invalid schema/signal/ID. Unknown routes return `404`, and GET on the ranking route returns `405`.

The [recorded bad-input example](bad_input_example.json) contains an actual loopback HTTP request with synthetic data and `ctr_pct: -1`. Its observed response is HTTP 422 with `invalid_signal` and `ctr_pct is outside its allowed range.` Reproduce it through the local portfolio demo using the recorded request. The static portfolio shows this response beside direct contract/source/test-output links and the interview action; it is a recorded example, not a publicly hosted API.

## Transparent rule

For each page:

```text
exposure  = min(impressions_90d / 10000, 1)
freshness = min(days_since_last_update / 365, 1)
ctr_gap   = max(0, (2 - ctr_pct) / 2) when position is 1–20, otherwise 0
depth_gap = max(0, (1200 - word_count) / 1200) when positive word count is known, otherwise 0
score     = round(100 * exposure * (0.4 + 0.3*freshness + 0.2*ctr_gap + 0.1*depth_gap), 3)
```

Review eligibility requires at least 500 impressions and known position. Eligible pages sort before monitor pages, then higher score, then ID alphabetically. Reason codes explain volume, freshness, CTR, thin depth and missingness. The example above scores **9.240**. The constants are explicit demonstration heuristics; they are not estimated from data or validated as causal editorial advice. Human review should inspect actual context before any action.

## Metrics and safety

By default `/api/v1/metrics` reads `work/outputs/capstone_metrics.json`, created by the local capstone analysis. It exposes only supported model names and numeric aggregate metric keys. It omits page rows, IDs, feature exports, arbitrary source fields and private file paths. Missing or malformed metrics return `503`; the ranking endpoint still works. Override the metrics path for local testing with `--metrics PATH`.

There is no request-body logging or disk persistence. Responses use `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`. Default binding is loopback. Browser-demo CORS allows only `http://127.0.0.1` or `http://localhost` on ports 8000, 8080 and 5500; this is not authentication. The stdlib server is a local proof artifact. Public deployment would need a production server, HTTPS, authentication, rate limits and explicit hosting approval; no public hosting is claimed.

## Demo sequence

1. Start the API and show `/health`.
2. Submit the synthetic example; show score, action, rank and reason codes.
3. Submit a negative CTR or repeated ID; show the precise validation error.
4. Run the tests; show the passing integration count.
5. If capstone metrics are ready, show `/api/v1/metrics` and explain that these trained-model results come from the separate notebook, while this POST endpoint uses the visible fixed rule.

This code was AI-assisted; Hamza should run and understand the scoring and validation before representing it as personal engineering proof.
