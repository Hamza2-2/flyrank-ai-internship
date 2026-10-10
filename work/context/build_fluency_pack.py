"""Build honest, separately scoped General AI Fluency deliverables.

Documents use only confirmed identity plus clearly marked provisional choices.
No account, training completion, calendar import, or publication is implied.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work"
CONTEXT = WORK / "context"
DATE = "2026-10-09"
NAME = "Hamza Afzal"
REPO = "https://github.com/Hamza2-2/flyrank-ai-internship"
INTERVIEW = REPO + "/issues/new?title=Interview%20invitation%20for%20Hamza%20Afzal"
CLAIM = "I can build a tested backend API that converts anonymized search signals into explainable content-review priorities."
AUDIENCE = "a backend engineering lead evaluating my backend project"
ACTION = "invite me to an interview about this backend project"
PROOF = f"I am {NAME}, focusing on backend development and engineering. {CLAIM} I am building this proof for {AUDIENCE}, so they can {ACTION}. The API contract, input validation, automated checks, and runnable example provide the evidence; any results from the starter dataset demonstrate a prototype rather than production readiness."
FACTS = "Hamza explicitly confirmed the exact narrow portfolio claim above, his name, backend field, audience (a backend engineering lead), action (invite me to an interview), all 12 recurring weekly tasks, GitHub username Hamza2-2, and the next real piece 'Deploy and harden the backend review API' in this conversation. Claim confirmation does not establish that he has reviewed or understood all the AI-assisted code. Account setup, Academy completion, and external Claude Project UI remain unconfirmed."


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def inline(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(text, title):
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            out.append("<pre>" + html.escape("\n".join(body)) + "</pre>")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+", c) for c in raw):
                    rows.append(raw)
                i += 1
            out.append("<table>" + "".join("<tr>" + "".join(("<th>" if j == 0 else "<td>") + inline(c) + ("</th>" if j == 0 else "</td>") for c in row) + "</tr>" for j, row in enumerate(rows)) + "</table>")
            continue
        elif re.match(r"^#{1,6} ", line):
            size = len(line.split(" ")[0])
            out.append(f"<h{size}>" + inline(line[size + 1:]) + f"</h{size}>")
        elif line.startswith("- ") or re.match(r"^\d+\. ", line):
            ordered = not line.startswith("- ")
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and (re.match(r"^\d+\. ", lines[i]) if ordered else lines[i].startswith("- ")):
                item = re.sub(r"^(?:\d+\.|-) ", "", lines[i])
                items.append("<li>" + inline(item) + "</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        else:
            body = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(?:#|\||-|\d+\.|```)", lines[i + 1]):
                i += 1
                body.append(lines[i])
            out.append("<p>" + inline(" ".join(body)) + "</p>")
        i += 1
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>
    @page {{ size: A4; margin: 14mm; }} * {{ box-sizing:border-box; }} body {{ max-width:1000px; margin:36px auto; padding:0 32px; font:15px/1.45 Arial,sans-serif; color:#182735; background:white; }} h1 {{ font-size:30px; color:#123c4e; margin:0 0 20px; }} h2 {{ font-size:20px; margin:24px 0 10px; color:#15596b; }} h3 {{ font-size:17px; }} p,li {{ margin:8px 0; }} table {{ border-collapse:collapse; width:100%; font-size:12px; margin:16px 0; }} th,td {{ border:1px solid #c6d3da; padding:7px; text-align:left; vertical-align:top; }} th {{ background:#e8f3f5; }} a {{ color:#15596b; overflow-wrap:anywhere; }} code {{ background:#edf1f3; font-size:0.9em; overflow-wrap:anywhere; }} pre {{ padding:14px; white-space:pre-wrap; background:#edf1f3; font-size:12px; }} h1,h2,h3 {{ break-after:avoid; }} tr {{ break-inside:avoid; }} @media print {{ body {{ margin:0; padding:0; max-width:none; font-size:11px; }} h1 {{ font-size:23px; }} h2 {{ font-size:16px; margin-top:18px; }} table {{ font-size:9px; }} a {{ text-decoration:none; }} }}
    </style></head><body>{''.join(out)}</body></html>'''


def doc(folder, name, body):
    path = folder / (name + ".md")
    write(path, body)
    write(folder / (name + ".html"), markdown_to_html(body, body.splitlines()[0].lstrip("# ")))


def requirement_block(folder, title, body, status):
    write(folder / "source_requirements.md", f"# {title}: source requirements\n\nSource: user-provided pasted assignment text, received {DATE}. This excerpt controls the deliverable scope; portal Q&A is not copied.\n\n{body}")
    write(folder / "README.md", f"# {title}\n\nPrepared for {NAME} on {DATE}, Asia/Karachi.\n\n{status}\n\nOpen `deliverable.pdf` or `deliverable.html`; the Markdown is editable. `source_requirements.md` records the supplied card. Evidence and missing items are explicit in the deliverable. This task is kept separate from every other assignment/capstone.\n\nOwned project repository: {REPO}. See the repository's submission index for publication status. Do not submit a task as fully complete until its required personal evidence is confirmed. The document-generation scripts do not submit to the internship portal or send interview requests.\n")


def main():
    CONTEXT.mkdir(parents=True, exist_ok=True)
    context = f'''# Hamza Afzal — backend portfolio build context

Saved {DATE}, Asia/Karachi. This is the actual local context document used by the Codex assistant to build and pressure-test the deliverables. It is not a screenshot or export from a Claude Project.

## Identity and proof

{PROOF}

{FACTS}

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

The actual site's visual direction is navy with green accents, generous white space, readable headings, and visible evidence links; it is a design for this build rather than a pre-existing personal brand. Display name: Hamza Afzal. Field: Backend Development and Engineering. Confirmed GitHub: [Hamza2-2](https://github.com/Hamza2-2). Owned project repo: [flyrank-ai-internship]({REPO}). Hamza chose a [GitHub interview-request link]({INTERVIEW}) as his one contact action. It opens a prefilled issue form; the visitor must choose to submit it, and opening the link sends nothing automatically. Do not invent an email or scheduling account.

## Next piece and maintenance habit

Confirmed next intention: **Deploy and harden the backend review API**. Hamza selected this real next piece in this conversation. Its future scope is production hosting, HTTPS, authentication and rate limits, meaningful tests, rollback, and actual deployment evidence. The current backend remains a local prototype; none of that production work is claimed as done. A local recurring note exists at `work/context/portfolio_maintenance_reminder.md`, first due Friday 2026-10-16 at 18:00 Asia/Karachi, then every Friday at 18:00. The matching ICS is importable but has not been imported into a calendar and creates no push notification by itself.

## Reuse this context

Keep this file with the project. Paste it at the start of a new AI chat or add it to a Claude/ChatGPT Project or Gemini Gem. If using Claude, proposed Project name: Hamza Afzal — Backend Proof Portfolio. Set the instructions to this tutor/identity content and attach the backend README and next-case evidence. Capture genuine account/UI evidence only after configuring it yourself. Preserve the actual transcript at `work/assignments/Draw_the_Path_Portfolio_Sitemap_and_Toolkit/pressure_test.md`.

## Sources and interpretation

The supplied assignment cards are the controlling scope. The [current FlyRank Week 1 guide](https://aifluency.flyrank.ai/week-01.html), checked {DATE}, permits a saved context document when a tool has no workspace feature. This local context document uses that route; it does not establish account setup or a configured Claude Project. The [current Week 10 guide](https://aifluency.flyrank.ai/week-10.html) describes a broader launch package than the pasted cards. Publication, a recorded demo, a graduate badge, and showcase submission remain separate actions with no completion claim here.
'''
    doc(CONTEXT, "project_context", context)
    write(CONTEXT / "claude_project_instructions.txt", context)
    receipt = f'''# User confirmation receipt

Date: 2026-10-09 · Asia/Karachi
Source: Hamza Afzal's confirmations in this conversation.

| Portfolio decision | User-confirmed value |
| --- | --- |
| Exact primary claim | “{CLAIM.rstrip('.')}” |
| Audience | A backend engineering lead |
| One action | Invite me to an interview |
| Next real piece | Deploy and harden the backend review API |

Hamza also chose the GitHub interview-request link in his owned repository as the contact path. The next piece is a confirmed intention; production deployment/hardening is future work. This receipt does not establish review/understanding of all AI-assisted code, account setup, or course completion.
'''
    doc(CONTEXT, "user_confirmation_receipt", receipt)
    write(CONTEXT / "user_confirmations.json", json.dumps({
        "date": DATE,
        "timezone": "Asia/Karachi",
        "confirmed_by": NAME,
        "source": "explicit confirmations in this conversation",
        "exact_primary_claim": CLAIM.rstrip('.'),
        "audience": "A backend engineering lead",
        "one_action": "invite me to an interview",
        "next_real_piece": "Deploy and harden the backend review API",
        "contact_method": "GitHub interview-request form",
        "contact_link": INTERVIEW,
        "next_piece_intention_status": "confirmed",
        "next_piece_work_status": "planned; production deployment/hardening is not done",
        "code_review_understanding_status": "not established by claim confirmation",
        "account_course_completion_status": "unconfirmed; genuine evidence pending",
    }, indent=2))
    reminder = '''# Recurring portfolio maintenance note

Created: 2026-10-09 (Asia/Karachi)
Owner: Hamza Afzal
State: active local recurring note; no calendar import or notification service configured
First due: Friday 2026-10-16 at 18:00 Asia/Karachi (13:00 UTC)
Repeat: every Friday at 18:00 Asia/Karachi until the next case is added
Next piece: Deploy and harden the backend review API
Intention status: explicitly confirmed by Hamza
Work status: planned next project; production deployment/hardening is not done
Scope: production hosting, HTTPS, authentication/rate limits, tests, rollback, and actual deployment evidence

- At the next due time, review production hosting, HTTPS, authentication/rate limits, tests, rollback, and deployment evidence against the planned scope.
- When the actual work/evidence is ready, edit the portfolio case block in `work/scripts/build_site.py` using the three beats, then run `python work/scripts/build_site.py` to rebuild `work/site/dist/portfolio.html`. A standalone case can also be generated at `work/site/dist/cases/backend-api-deployment.html` by adding its output to the builder.
- If work/evidence is pending, record the blocker and review it at the next Friday checkpoint. Do not turn a local prototype into a claimed production deployment.
- After publication, replace this note with the following real case and date.

Checkpoint log: no due checkpoint has occurred yet.
Calendar aid: `portfolio_maintenance_reminder.ics` is ready to import; it has NOT been imported and is not evidence of an external calendar reminder.
'''
    doc(CONTEXT, "portfolio_maintenance_reminder", reminder)
    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Hamza Afzal//Portfolio Maintenance//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VTIMEZONE", "TZID:Asia/Karachi", "BEGIN:STANDARD", "DTSTART:19700101T000000", "TZOFFSETFROM:+0500", "TZOFFSETTO:+0500", "TZNAME:PKT", "END:STANDARD", "END:VTIMEZONE",
        "BEGIN:VEVENT", "UID:portfolio-next-case-20261016-hamza-afzal@local", "DTSTAMP:20261009T000000Z", "DTSTART;TZID=Asia/Karachi:20261016T180000", "DTEND;TZID=Asia/Karachi:20261016T183000", "RRULE:FREQ=WEEKLY;BYDAY=FR",
        "SUMMARY:Add case: Deploy and harden the backend review API", "DESCRIPTION:Review hosting HTTPS auth rate limits tests rollback and deployment evidence.", "STATUS:CONFIRMED", "BEGIN:VALARM", "TRIGGER:-PT15M", "ACTION:DISPLAY", "DESCRIPTION:Portfolio case checkpoint", "END:VALARM", "END:VEVENT", "END:VCALENDAR", "",
    ])
    # The event is ASCII; fold long RFC 5545 content lines at 75 octets.
    folded = []
    for line in ics.split("\r\n"):
        while len(line.encode("utf-8")) > 75:
            folded.append(line[:75])
            line = " " + line[75:]
        folded.append(line)
    (CONTEXT / "portfolio_maintenance_reminder.ics").write_bytes("\r\n".join(folded).encode("utf-8"))

    audit_folder = WORK / "assignments" / "FL-01_AI_Workflow_Audit_and_Tool_Setup"
    requirement_block(audit_folder, "FL-01 — AI Workflow Audit and Tool Setup", "10–15 genuine recurring weekly tasks, each classified as just me / delegate to AI with review / collaborate with AI / fully automate, with one-line rationales. At least two honestly just me. Three reusable target tasks with measurable success definitions. Claude, ChatGPT, Anthropic Academy setup and first course module evidence. Configured Claude Project screenshot. Deliverable: a 1–2 page workflow audit plus evidence and three target tasks.", "Status: all 12 recurring tasks confirmed by Hamza; personal audit and measurable target definitions prepared. Account/course evidence and genuine Claude UI screenshot still required.")
    audit = f'''# FL-01 — AI Workflow Audit and Tool Setup

{NAME} · Backend Development and Engineering · {DATE}

**Personal workflow audit.** Hamza explicitly confirmed all 12 recurring tasks below in this conversation. Classifications and success definitions are the assistant's proposed workflow, ready for Hamza to use and review. Tool/account/course evidence remains pending.

| Confirmed recurring task | Classification | One-line rationale |
| --- | --- | --- |
| Writing API endpoints | Delegate to AI with review | AI can draft a handler quickly; I review every branch and execute the contract before accepting it. |
| Defining request/response schemas | Collaborate with AI | I specify the consumer's need; AI challenges required fields, ranges, and edge cases. |
| Designing database tables | Collaborate with AI | AI proposes keys and relationships; I check that they match the real entities and access patterns. |
| Planning features | Collaborate with AI | I define the user need and priority while AI surfaces dependencies and alternatives. |
| Breaking features into coding tasks | Delegate to AI with review | AI drafts small steps; I check their order, scope, and acceptance conditions. |
| Reproducing bugs | Collaborate with AI | I confirm the failure in the actual environment; AI suggests minimal reproductions to test. |
| Reading error logs | Collaborate with AI | AI helps explain a sanitized trace; I compare the explanation against the source and reproduce it. |
| Fixing bugs | Delegate to AI with review | AI proposes a patch; I inspect it and require the reproduction plus regression checks to pass. |
| Writing tests | Collaborate with AI | I define expected behavior; AI proposes meaningful edge cases and executable checks. |
| Refactoring code | Delegate to AI with review | AI can reduce repetition; I review the change and check that public behavior stays correct. |
| Choosing architecture | Just me | AI may outline tradeoffs, but I own the final architecture decision and its consequences. |
| Checking finished work myself | Just me | Automated checks assist me; final acceptance requires my understanding and direct verification. |

## Three reusable targets and done-well definitions

1. **API contract:** specify one request/response schema for ranking anonymized signals; every required field, allowed range, output reason code, and error response is documented and demonstrated by an executed example.
2. **Input validation:** cover missing fields, negative metrics, impressions equal to zero, malformed JSON, and unexpected fields; valid inputs succeed and invalid inputs return a documented 4xx response without a server crash.
3. **Regression check plus explanation:** run the backend project's full check command from a clean local setup; every check passes, examples reproduce, and Hamza can explain the ranking and one limitation in his own words.

## Toolkit and evidence status

| Required evidence | Actual status | Next evidence to attach |
| --- | --- | --- |
| Claude account | Unconfirmed | Genuine signed-in account evidence with email/private details hidden |
| ChatGPT account | Unconfirmed | Genuine signed-in account evidence with private details hidden |
| Anthropic Academy enrollment | Unconfirmed | Enrollment page for AI Fluency: Framework & Foundations |
| First module completed | Unconfirmed | Actual progress/completion screen after learning the module |
| Claude Project with custom instructions | Instructions prepared, UI setup unconfirmed | Configure using `../../context/claude_project_instructions.txt`; attach actual Project screenshot |

The current AI assistant is Codex in this conversation; using it does not prove a Claude/ChatGPT account or Academy completion. Course entry: [Anthropic Academy](https://anthropic.skilljar.com/ai-fluency-framework-and-foundations). Project reference: [Claude Projects documentation](https://support.claude.com/en/articles/9517075-what-are-projects).

## To make this audit final

The 12 tasks are already confirmed against Hamza's real week, and architecture/final acceptance stay just me. Hamza must review the suggested classifications and targets, configure his accounts/Project, and attach genuine Academy/setup evidence. No account, enrollment, or module completion was fabricated.
'''
    doc(audit_folder, "deliverable", audit)

    proof_folder = WORK / "assignments" / "What_Are_You_Proving"
    requirement_block(proof_folder, "What Are You Proving?", "One paragraph naming one primary skill, one specific hiring/engagement person, and one action, plus one honest line explaining why owning a portfolio adds proof beyond a CV/LinkedIn. Use AI as an interviewer and thinking partner; the final claim must be the intern's own.", "Status: Hamza explicitly confirmed the exact narrow portfolio claim, identity, backend field, backend lead audience, and interview invitation action. Statement and one-line why prepared. Confirmation does not establish that Hamza has reviewed or understood all AI-assisted code.")
    proof = f'''# What Are You Proving?

{NAME} · {DATE}

**User-confirmed proof statement.** Hamza explicitly confirmed the exact primary claim: “{CLAIM}” Name, field, audience, and action are also confirmed. The assistant helped narrow the wording. Confirmation does not establish that Hamza has reviewed or understood all AI-assisted code.

## One-paragraph proof statement

{PROOF}

## One-line why

A CV can name backend engineering; an owned portfolio can let someone inspect the API contract, run an example, and examine the checks that support that claim.

## Narrowing choices and actual interview status

| Element | Choice | Evidence/status |
| --- | --- | --- |
| Primary skill | Backend development and engineering, demonstrated through one tested API | Hamza supplied the field in this conversation |
| Specific proof | {CLAIM} | Exact narrow claim explicitly confirmed by Hamza; local backend, synthetic examples, and passing HTTP checks are recorded |
| One person | A backend engineering lead | Confirmed by Hamza |
| One action | Invite Hamza to an interview about this backend project | Confirmed by Hamza |

The assistant asked for identity, skill, audience/action, recurring weekly tasks, and GitHub/contact. Hamza supplied his name/field, backend lead audience, interview action, 12 audit tasks, and GitHub Hamza2-2. He also explicitly confirmed the exact narrow API claim quoted above. This records actual inputs without inventing a longer interview transcript or code-understanding evidence.

Reflection still needed: What can Hamza explain and modify himself after the AI-assisted build? Which detail would he remove because it overstates his current ability? The audience and action have already been answered.

## Claim boundary

The actual local API has a schema at `work/backend_api/openapi.json`, executable examples in its README, and passing real-HTTP check output at `work/backend_api/TEST_RESULTS.txt`. Its demo requests are synthetic, its queue uses a documented fixed rule, and learned-model metrics come from a separate notebook. The portfolio must not say the API is deployed in production, improves client search traffic, or proves warehouse results. AI assistance is disclosed; Hamza's review and explanation are part of the proof.
'''
    doc(proof_folder, "deliverable", proof)

    map_folder = WORK / "assignments" / "Draw_the_Path_Portfolio_Sitemap_and_Toolkit"
    requirement_block(map_folder, "Draw the Path — Portfolio Sitemap + Toolkit", "Small sitemap where every page supports the one claim/person/action. Accounts for Claude, ChatGPT, Gemini, Perplexity. Claude Project named for the build with proof statement and tutor instructions. Real sitemap pressure-test prompt/output and at least one change. Supplied-card deliverable: sketch photo plus configured Project screenshot and prompt/output.", "Status: actual digital sitemap, saved context doc, actual assistant pressure test, and concrete changes prepared. Physical sketch photo, external accounts, and genuine Claude UI evidence remain unconfirmed. Live Week 1 guide allows context-document route; supplied-card differences are recorded.")
    pressure = f'''# Actual sitemap pressure test

Date: {DATE}, Asia/Karachi. Tool: Codex assistant in this live conversation. This answer was authored while doing the assignment. It is not a fabricated Claude/ChatGPT export. Context: `work/context/project_context.md`.

## Prompt evaluated

My name is {NAME}. My primary skill is backend development and engineering. I explicitly confirmed this exact narrow primary claim in this conversation: “{CLAIM}” My proof statement is: {PROOF}

Sitemap: a landing page at `portfolio.html` with hero/claim, detailed API case section at `#work`, short about, and one contact action. The case links to runnable API documentation/checks and a supporting research page at `index.html`. The confirmed contact action is a GitHub interview-request form in my owned repository: {INTERVIEW}. My confirmed next piece is Deploy and harden the backend review API; its case is added only after actual production work/evidence exists. Does this walk my one person from landing, to believing me, to taking my one action? Which parts earn their place, which waste attention, and what evidence is missing? Pressure-test the plan against backend engineering; be specific and identify at least one change.

## Assistant output — actual evaluation

The map is small enough, but its proof depends on the case section and direct evidence links. A backend lead needs to inspect behavior, not only read a statement about engineering. Keep the landing hero because it tells that lead exactly what to assess. Keep the featured API case because it connects the claim to running code. Keep a brief about section because it gives identity and internship context. Keep the one confirmed interview invitation action.

The API case earns its place only if it includes an example request and response, the schema/validation rules, a way to rerun the checks, and one explicit failure example. Link directly to the backend README and check evidence so the visitor does not have to search a repository. Distinguish the tested local prototype from a hosted service. Reason codes must be visible, otherwise the word “explainable” is unsupported. Keep the research page as supporting evidence for the separate aggregate-metrics endpoint, with a clear distinction between learned-model metrics and fixed-rule POST ranking.

A separate About page, blog, services page, and testimonials would add navigation without strengthening this proof. Keep about/contact inside the landing page. Do not show the future deployment case as completed work. A planned-next-case label is enough until hosting, HTTPS, authentication/rate limits, tests, rollback, and actual deployment evidence exist.

Hamza confirmed both the backend lead audience and the interview invitation action, and chose a prefilled GitHub issue link in the owned internship repository. Repeating that same link beside the case and at the footer is acceptable; offering several competing actions would dilute it. The page should disclose that opening it only opens a form; a visitor deliberately submits the request. This is now a concrete contact path rather than an invented email address or a vague profile link.

Concrete change: add a compact evidence strip immediately under the API case summary with “Contract”, “Example request”, and “Checks”, plus a visible “Local prototype” limitation. Show a bad-input example in the case or directly linked documentation. This changes the visitor's path from a claim-only page into inspectable backend proof.

Acceptance check: within 30 seconds a visitor can identify Hamza's field, the specific API, and the chosen action. Within five minutes the visitor can find and run one example and locate the checks. This is a design check to perform after building the site; no user test has been conducted here.

## Changes taken into the build specification

1. Keep about and contact as landing-page sections rather than separate pages.
2. Add direct contract/example/check evidence beside the featured API case.
3. Show the API's actual limitation and a documented invalid-input example.
4. Label the confirmed backend deployment/hardening intention as planned; add the actual case page only after production work/evidence is ready.

The sitemap SVG/PNG reflects this revised plan and the user-confirmed exact claim/field/person/action. Claim confirmation is distinct from reviewing and understanding every AI-assisted code path; no such review completion is asserted.
'''
    doc(map_folder, "pressure_test", pressure)
    sitemap = f'''# Draw the Path — Portfolio Sitemap + Toolkit

{NAME} · Backend Development and Engineering · {DATE}

## Claim, one person, one action

{PROOF}

The exact narrow primary claim, audience, and action are explicitly user-confirmed. Owned repo: [flyrank-ai-internship]({REPO}). The [GitHub interview-request link]({INTERVIEW}) opens a prefilled issue form; the visitor chooses whether to submit it. Opening the link does not send a request automatically. Code review/understanding is not established by claim confirmation.

## Small sitemap and page purpose

| Destination | Purpose | Why it earns its place |
| --- | --- | --- |
| `work/site/dist/portfolio.html` — hero | State the narrow backend claim | A backend lead can immediately decide what the site proves |
| Same page — featured API case | Show contract, example, checks, and reason codes | Evidence makes the claim inspectable |
| Same page — short about | Name and honest internship context | Gives identity without adding a separate page |
| Same page — contact/CTA | One invitation to interview | Turns belief into Hamza's confirmed action |
| `portfolio.html#work` — API case section | Problem → what I did → what came of it; evidence and limits | Gives technical depth with direct links to runnable proof |
| `index.html` — supporting research | Data/method/results behind the separate aggregate metrics | Supports the backend metrics endpoint without confusing it with the POST rule |
| Future backend deployment/hardening case | Only add after actual production work and deployment evidence | Extends the same backend proof with evidence of deployment and reliability |

Actual map files: `sitemap.svg` and `sitemap.png`. The PNG is a browser rendering of the SVG. These are a real digital sitemap, not a photograph of a hand-drawn sketch; a physical sketch photo remains outstanding if the reviewer enforces the pasted card literally.

## AI workspace and toolkit

The saved customized context is `../../context/project_context.md`, with copy-ready Claude instructions at `../../context/claude_project_instructions.txt`. It contains identity, the proof paragraph, tutor directions, stack/paths, limits, and maintenance context. `context_doc_screenshot.png` is an actual browser screenshot of that local context document, explicitly not a Claude interface screenshot.

Claude, ChatGPT, Gemini, and Perplexity accounts are unconfirmed. No signup, paid plan, course enrollment, or external Project has been claimed. A genuine Claude Project screenshot can be added after configuring “Hamza Afzal — Backend Proof Portfolio” using the prepared context. The [current FlyRank Week 1 guide](https://aifluency.flyrank.ai/week-01.html), checked {DATE}, also accepts a context document when workspace features are unavailable; this artifact follows that alternative.

## Real pressure test and change

Open `pressure_test.md`/`pressure_test.html` for the actual prompt and answer produced by the Codex assistant here. `pressure_test_screenshot.png` records the rendered transcript. The evaluation found a gap: the map needed direct contract, example, and check evidence to prove backend engineering. The revised map adds that evidence, keeps about/contact on the landing, and labels the confirmed next backend deployment/hardening piece as planned.

## Submission status

Prepared: map, context doc, actual pressure-test output, documented changes, exact user-confirmed claim/field/person/action, and a user-chosen GitHub interview-request link. Pending: toolkit account evidence and genuine Claude/physical sketch evidence if required by the supplied card. The screenshot artifacts show local files and must never be described as external account UI.
'''
    doc(map_folder, "deliverable", sitemap)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850" viewBox="0 0 1280 850" role="img" aria-labelledby="title desc">
    <title id="title">Hamza Afzal backend proof portfolio sitemap</title><desc id="desc">Landing claim flows to inspectable API evidence, brief about, and one interview action; deploying and hardening the backend API is the confirmed planned next case.</desc>
    <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 Z" fill="#236577"/></marker></defs>
    <rect width="1280" height="850" fill="#f4f8f9"/><g font-family="Arial,sans-serif" fill="#132d3c">
    <text x="60" y="60" font-size="30" font-weight="700">Hamza Afzal · Backend proof portfolio</text><text x="60" y="96" font-size="18">Revised digital sitemap · 2026-10-09 · Claim/audience/action confirmed</text>
    <rect x="60" y="137" width="1160" height="130" rx="14" fill="#123d51"/><text x="90" y="177" font-size="23" font-weight="700" fill="white">ONE USER-CONFIRMED CLAIM</text><text x="90" y="213" font-size="22" fill="white">I can build a tested backend API that converts anonymized search signals</text><text x="90" y="244" font-size="22" fill="white">into explainable content-review priorities.</text>
    <rect x="60" y="320" width="260" height="270" rx="14" fill="white" stroke="#236577" stroke-width="2"/><text x="84" y="359" font-size="22" font-weight="700">1 · LAND</text><text x="84" y="398" font-size="18">portfolio.html</text><text x="84" y="438" font-size="17">Hero + narrow claim</text><text x="84" y="469" font-size="17">Featured API proof</text><text x="84" y="500" font-size="17">Short about section</text><text x="84" y="548" font-size="15" fill="#236577">One landing; no extra blog</text>
    <rect x="390" y="320" width="410" height="270" rx="14" fill="white" stroke="#236577" stroke-width="2"/><text x="418" y="359" font-size="22" font-weight="700">2 · BELIEVE</text><text x="418" y="398" font-size="18">portfolio.html#work · API case</text><text x="418" y="438" font-size="17">Problem → build → outcome</text><text x="418" y="469" font-size="17">Contract + request/response</text><text x="418" y="500" font-size="17">Checks + bad-input example</text><text x="418" y="531" font-size="17">Reason codes + research link</text><text x="418" y="565" font-size="15" fill="#236577">API runs locally; explicit limitations</text>
    <rect x="870" y="320" width="350" height="270" rx="14" fill="white" stroke="#236577" stroke-width="2"/><text x="897" y="359" font-size="22" font-weight="700">3 · ACT</text><text x="897" y="398" font-size="18">Same landing · contact</text><text x="897" y="438" font-size="17">One confirmed action:</text><text x="897" y="469" font-size="17">Invite Hamza to interview</text><text x="897" y="512" font-size="17">GitHub interview-request form</text><text x="897" y="550" font-size="15" fill="#236577">Opens a form; visitor chooses to submit</text>
    <path d="M320 451 H379" stroke="#236577" stroke-width="3" marker-end="url(#arrow)"/><path d="M800 451 H859" stroke="#236577" stroke-width="3" marker-end="url(#arrow)"/>
    <rect x="390" y="660" width="830" height="130" rx="14" fill="#e7f2f4" stroke="#236577" stroke-dasharray="7 5"/><text x="418" y="699" font-size="20" font-weight="700">NEXT CASE · Deploy and harden the backend review API</text><text x="418" y="734" font-size="17">cases/backend-api-deployment.html · intention confirmed, work planned</text><text x="418" y="767" font-size="16">Hosting · HTTPS · auth/rate limits · tests · rollback · actual deployment evidence</text>
    <path d="M596 590 V648" stroke="#236577" stroke-width="3" marker-end="url(#arrow)"/>
    <text x="60" y="826" font-size="14">Actual digital artifact, not a photograph of a physical sketch. Current API is local; production deployment is a future piece.</text>
    </g></svg>'''
    write(map_folder / "sitemap.svg", svg)
    write(map_folder / "sitemap_render.html", '<!doctype html><meta charset="utf-8"><title>Digital sitemap</title><style>html,body{margin:0;width:1280px;height:850px;overflow:hidden}svg{display:block}</style>' + svg)
    write(map_folder / "context_evidence.html", markdown_to_html("# Actual saved AI context document\n\n**Local context-document screenshot. This is not a Claude/ChatGPT interface.**\n\n" + context.replace("# Hamza Afzal — backend portfolio build context", "## Customized identity and tutor context"), "Saved AI context evidence"))

    how = '''## Exactly how to add the next case

1. Edit the `portfolio` case block in **`work/scripts/build_site.py`**, the source of truth. Use three beats: **problem** (local API → reliable production service), **what I did** (actual deployment/hardening), **what came of it** (verified behavior and limits).
2. Link source/configuration, deployment date/version, working HTTPS endpoint, authentication/rate-limit checks, tests, and rollback evidence. Keep secrets out; retain a planned label until the work exists.
3. If a separate page is useful, extend the builder to write `work/site/dist/cases/backend-api-deployment.html`; add that relative link to its featured-work section. Keep the GitHub interview-request action.
4. Run **`python work/scripts/build_site.py`** to regenerate `work/site/dist/portfolio.html`; review via `python -m http.server 8000 --directory work/site/dist`. Check links/mobile layout and the documented site checks, then verify the exact URL after authorized publication.
5. Update the saved context/reminder for the following case. Reuse the tutor instructions and review unsupported claims yourself.

## Named next piece

**Deploy and harden the backend review API** — explicitly confirmed by Hamza. Planned scope: production hosting, HTTPS, authentication/rate limits, meaningful tests, rollback, and actual deployment evidence. The intention is confirmed; this production work is not done.

## Concrete reminder evidence

The actual note is `work/context/portfolio_maintenance_reminder.md`, created 2026-10-09. First checkpoint: **Friday 2026-10-16 at 18:00 Asia/Karachi**, then every Friday until the case is added. It records the action/blocker steps; this local recurring note is permitted by the supplied brief. No notification service is configured.

The matching ICS is **not calendar-imported**. `reminder_screenshot.png` shows the actual local note, not calendar UI; `reminder_evidence.json` records its hash/due time. Copies of the note/ICS are included here.

## Preserved tutor/build context

`work/context/project_context.md` preserves identity, proof, tutor instructions, stack, style, boundaries, and the confirmed next piece; `preserved_build_context.md` is the copy in this folder. External Claude Project UI is unconfirmed. The actual Codex pressure test is saved in the Draw the Path assignment folder.
'''
    caps = [
        ("FL_General_AI_Fluency_Impact_Project", "General AI Fluency · Impact Project", "FL"),
        ("Send_the_Link_Launch_Demo_and_Story", "Send the Link: Launch, Demo & Story", "no code supplied"),
    ]
    for dirname, title, code in caps:
        folder = WORK / "capstones" / dirname
        requirement_block(folder, title, f"Code: {code}. Supplied brief: a concrete note explaining where/how to add the next case using problem → what you did → what came of it; name the next real piece; set a real reminder (calendar nudge or recurring note); preserve the Claude Project/build context. Deliverable: short update note + named piece + reminder evidence.", "Status: concrete maintenance note, user-confirmed next piece 'Deploy and harden the backend review API', actual local recurring note/ICS, and preserved context prepared. Future production work is not claimed as completed. External Claude Project UI remains unconfirmed; see submission index for publication status.")
        body = f'''# {title}

{NAME} · Backend Development and Engineering · {DATE}

**Separate capstone deliverable.** The two supplied General AI Fluency cards have identical maintenance briefs. Each folder includes its own note/evidence and copies of the shared context/reminder.

{how}

## Honest completion boundaries and source discrepancy

The local reminder/context exist; Hamza confirmed the next intention and GitHub interview action. Toolkit/Claude UI evidence remains unconfirmed. Repo: `https://github.com/Hamza2-2/flyrank-ai-internship`; see its submission index for publication status. Document scripts do not send messages or submit to the portal.

The [live Week 10 guide](https://aifluency.flyrank.ai/week-10.html), checked 2026-10-09, adds a broader launch/demo/story package. This note follows the supplied maintenance card; check the current portal card before submission. A demo, badge, or showcase submission is not established by this note.
'''
        doc(folder, "deliverable", body)
    write(CONTEXT / "fluency_manifest.json", json.dumps({"created_date": DATE, "timezone": "Asia/Karachi", "name": NAME, "confirmed_field": "Backend Development and Engineering", "exact_primary_claim": CLAIM.rstrip('.'), "primary_claim_status": "explicitly confirmed by user", "code_review_understanding_status": "not established by claim confirmation", "account_course_status": "unconfirmed; genuine evidence pending", "confirmation_receipt": "work/context/user_confirmations.json", "audience_status": "confirmed", "action_status": "confirmed", "weekly_tasks_status": "all 12 confirmed by user", "github_username": "Hamza2-2", "next_case": "Deploy and harden the backend review API", "next_case_intention_status": "confirmed by user", "next_case_work_status": "planned; no production deployment or hardening claimed", "next_case_page": "work/site/dist/cases/backend-api-deployment.html", "folders": [str(p.relative_to(ROOT)).replace("\\", "/") for p in [audit_folder, map_folder, proof_folder] + [WORK / "capstones" / x[0] for x in caps]], "external_actions": "none by these document-generation scripts", "verification_notebooks": "not applicable to prose deliverables"}, indent=2))


if __name__ == "__main__":
    main()
