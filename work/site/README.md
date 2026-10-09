# Research paper and backend portfolio

The published paper is `dist/index.html`; the portfolio is `dist/portfolio.html`. Source content and figures come from the executed capstone. No private warehouse rows, raw exports, tokens, or client identities are copied into this site.

Build from the repository root after notebook execution: `python work/scripts/build_site.py` (install `work/requirements-execution.txt` first).

Local demonstration:

1. Run `python work/backend_api/server.py`.
2. In another terminal run `python -m http.server 8000 --directory work/site/dist`.
3. Open `http://127.0.0.1:8000/portfolio.html` and press Send local API request.

The public static website hosts the paper, downloadable evidence, and source. The backend service runs locally. The button reports that limitation accurately when viewed online.

To add the next case, extend the portfolio's problem/work/outcome section in `work/scripts/build_site.py`, rerun the build, review locally, and republish. Hamza confirmed the next case: Deploy and harden the backend review API. An optional standalone case page belongs at `dist/cases/backend-api-deployment.html` after real production work exists. Record the actual hosting, HTTPS, authentication/rate limits, tests, rollback, and deployment evidence.
