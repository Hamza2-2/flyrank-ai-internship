# Hamza Afzal — backend portfolio build context

Saved 2026-10-09, Asia/Karachi. This is the actual local context document used by the Codex assistant to build and pressure-test the deliverables. It is not a screenshot or export from a Claude Project.

## Identity and proof

I am Hamza Afzal, focusing on backend development and engineering. I can build a tested backend API that converts anonymized search signals into explainable content-review priorities. I am building this proof for a backend engineering lead evaluating my backend project, so they can invite me to an interview about this backend project. The API contract, input validation, automated checks, and runnable example provide the evidence; any results from the starter dataset demonstrate a prototype rather than production readiness.

Hamza explicitly confirmed the exact narrow portfolio claim above, his name, backend field, audience (a backend engineering lead), action (invite me to an interview), all 12 recurring weekly tasks, GitHub username Hamza2-2, and the next real piece 'Deploy and harden the backend review API' in this conversation. Claim confirmation does not establish that he has reviewed or understood all the AI-assisted code. Account setup, Academy completion, and external Claude Project UI remain unconfirmed.

## Tutor instructions

Act as my backend engineering tutor and reviewer. Explain each design choice in simple language, then give a runnable example. Ask one sharp question when a personal fact or requirement is missing. Ask me to explain what a route, validation rule, or automated check does before I claim it as my skill. Keep writing concise and direct; this is a working preference for this project, not a claim about my established voice.

Treat backend engineering as the primary skill. Keep the claim narrow: a tested API with clear contracts and reason codes. Give the backend lead direct evidence of input validation, predictable errors, reproducible runs, and limits. Keep one main action: an interview invitation, confirmed by Hamza.

Do not invent employment, previous clients, production deployments, measured business gains, screenshots, account setup, Academy attendance, interview answers, or certificates. Show local prototype results as local prototype results. Require my review before describing AI-authored code as independently demonstrated ability. Keep client identities, domains, raw search queries, private exports, credentials, and personal contact details out of public pages.

## Build boundaries

The portfolio is generated at `work/site/dist/portfolio.html` from the source-of-truth portfolio block in `work/scripts/build_site.py`. Edit that source, then run `python work/scripts/build_site.py`; do not make lasting changes only in the generated HTML. The backend proof lives in `work/backend_api/`. A future standalone deployment case can be generated at `work/site/dist/cases/backend-api-deployment.html` after actual production work and evidence exist; add its output/template to the builder at that time.

Use one landing page with claim, featured API case section, short about, and one contact action. Link the case to real backend source/contract/checks and the supporting research page at `index.html`. Do not add a blog, services page, or invented testimonials. A built site is a local artifact until a public deployed URL is verified.

Each case uses three beats: problem, what I did, what came of it. Link to real source code and recorded checks. Warehouse-backed claims wait for gated dataset access and an honest grouped/time-aware evaluation. Results from a starter CSV do not fulfill warehouse evidence requirements.

## Current stack and identity kit

The actual proof is a dependency-free Python standard-library REST API at `work/backend_api/server.py`, paired with a static HTML/CSS/JavaScript portfolio. It runs locally at `http://127.0.0.1:8787` using `python work/backend_api/server.py`. `GET /health` reports the service state; `POST /api/v1/review-priorities` returns a deterministic fixed-rule queue and reason codes; `GET /api/v1/metrics` exposes only allowlisted aggregate metrics from the separate capstone analysis when available. The POST endpoint does not train or call a learned model.

`work/backend_api/openapi.json` is the actual contract. `python work/backend_api/test_api.py` runs real-HTTP integration checks; recorded passing output lives at `work/backend_api/TEST_RESULTS.txt`. Read that output for the current check count rather than hard-coding a number in future prose. Demo inputs are synthetic and use safe `page_` IDs. Requests are not stored. The local stdlib server is not a publicly hosted or production-hardened service.

The actual site's visual direction is navy with green accents, generous white space, readable headings, and visible evidence links; it is a design for this build rather than a pre-existing personal brand. Display name: Hamza Afzal. Field: Backend Development and Engineering. Confirmed GitHub: [Hamza2-2](https://github.com/Hamza2-2). Owned project repo: [flyrank-ai-internship](https://github.com/Hamza2-2/flyrank-ai-internship). Hamza chose a [GitHub interview-request link](https://github.com/Hamza2-2/flyrank-ai-internship/issues/new?title=Interview%20invitation%20for%20Hamza%20Afzal) as his one contact action. It opens a prefilled issue form; the visitor must choose to submit it, and opening the link sends nothing automatically. Do not invent an email or scheduling account.

## Next piece and maintenance habit

Confirmed next intention: **Deploy and harden the backend review API**. Hamza selected this real next piece in this conversation. Its future scope is production hosting, HTTPS, authentication and rate limits, meaningful tests, rollback, and actual deployment evidence. The current backend remains a local prototype; none of that production work is claimed as done. A local recurring note exists at `work/context/portfolio_maintenance_reminder.md`, first due Friday 2026-10-16 at 18:00 Asia/Karachi, then every Friday at 18:00. The matching ICS is importable but has not been imported into a calendar and creates no push notification by itself.

## Reuse this context

Keep this file with the project. Paste it at the start of a new AI chat or add it to a Claude/ChatGPT Project or Gemini Gem. If using Claude, proposed Project name: Hamza Afzal — Backend Proof Portfolio. Set the instructions to this tutor/identity content and attach the backend README and next-case evidence. Capture genuine account/UI evidence only after configuring it yourself. Preserve the actual transcript at `work/assignments/Draw_the_Path_Portfolio_Sitemap_and_Toolkit/pressure_test.md`.

## Sources and interpretation

The supplied assignment cards are the controlling scope. The [current FlyRank Week 1 guide](https://aifluency.flyrank.ai/week-01.html), checked 2026-10-09, permits a saved context document when a tool has no workspace feature. This local context document uses that route; it does not establish account setup or a configured Claude Project. The [current Week 10 guide](https://aifluency.flyrank.ai/week-10.html) describes a broader launch package than the pasted cards. Publication, a recorded demo, a graduate badge, and showcase submission remain separate actions with no completion claim here.
