# Sources and interpretation notes

Checked on 9 October 2026 (Asia/Karachi), including final public-deployment verification. These notes record the authority and discrepancies used when preparing the requested deliverables.

## Pasted assignment cards

Primary requested scope: the user's attachment `Pasted text.txt`. Relevant line locations in the attachment:

| Lines | Card |
|---|---|
| 1–31 | AI Workflow Audit and Tool Setup (FL-01) |
| 34–59 | Run the Starter Notebooks (ML-01) |
| 64–85 | Draw the Path: Portfolio Sitemap + Toolkit |
| 209–230 | What Are You Proving? |
| 419–439 and 446–466 | Research Question and Provisional Lane (ML-02), duplicated |
| 635–656 | General AI Fluency · Impact Project (FL) |
| 789–810 | Send the Link: Launch, Demo & Story |
| 843–872 | Google Search Ranking & Discoverability Capstone (ML) |

Portal Q&A text is contextual; it does not prove Hamza completed an activity. It says minimum certification scope is five assignments plus one capstone from the main track, but the user requested all pasted named tasks. It also indicates tool flexibility and optional AI Fluency work for other main tracks. This does not authorize manufacturing screenshots, course certificates, reminders, identity facts or external submissions.

The two AI Fluency capstone cards have different titles, codes, weeks and workload estimates, but repeat the same next-case/reminder/context brief. They are kept separately. The second ML-02 occurrence requires no duplicate implementation.

## Official starter repository

Source: [FlyRank ML internship starter](https://github.com/flyrank-bih/flyrank-ml-internship-starter).

- [Skills router](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/skills/README.md): read the router and load one task skill plus the data skill for data work.
- [Data-use policy](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/DATA_USE.md): private client data stays out of the public repo, data processing must respect approved release terms, IDs are not model features, and public claims must remain observational or decision-support.
- [Smoke-test workflow](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/.github/workflows/smoke-test.yml): runs the bundled pipeline, blocks committed dataset archives and unexpected CSVs, checks executed deliverable outputs after paper publication, and checks deployed-paper data credit.
- [Work-area instructions](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/work/README.md): keep reference pipeline intact; write work under `work/`; retain compact metrics JSON receipts; exclude datasets; use fixed seeds and reproducibility instructions.
- [Dataset and lane guide](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/docs/ml-intern-dataset-and-lane-guide.md): starter dataset is permitted by individual predefined lane descriptions; warehouse is needed for own joins/time windows and stronger temporal labels. Final capstone requires deployed paper, executed notebooks, and root `submission/paper_url.txt`.
- [Data dictionary](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/docs/data-dictionary.md) and [data skill](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/skills/flyrank/flyrank-data/SKILL.md): percent scale, missingness and zero-position semantics, pseudonymous IDs, proxy-label leakage, warehouse panel/availability/window cautions.

Local guidance is the downloaded starter snapshot. These links identify the upstream sources. Hamza's separate owned repository and verified publication are recorded below.

### Starter versus warehouse distinction

The pasted capstone describes full-warehouse feature building, and freestyle specifically says full warehouse. The lane table in the downloaded guide lists “warehouse release or starter dataset” for Ranking Signal Analysis, Structured Content Archetype Clustering, and CTR / Engagement Opportunity Scoring. It lists Refresh as “starter playground plus warehouse support,” while that lane's detailed section permits either dataset and recommends daily warehouse facts for stronger time-window labels. Consequently a transparent predefined starter analysis is supported by official lane guidance, but must never be labeled a full-warehouse or future-outcome study. Strict temporal prediction/freestyle cannot be completed from a single starter snapshot.

Warehouse source: [FlyRank/internship-warehouse](https://huggingface.co/datasets/FlyRank/internship-warehouse). It requires user-approved gated access. The official lane guide reports build `flyrank_pseudonymized_warehouse_release_v20260703`, daily-fact range 2025-01-27 through 2026-06-30 and 78,835,655 daily rows. Those are source metadata, not counts independently computed by this local project.

## Live AI Fluency guide differences

### Week 1

Checked [official Week 1](https://aifluency.flyrank.ai/week-01.html). The current course runs ten weeks. Its workspace can be a Claude/ChatGPT Project, Gemini Gem, or persistent context document; it requests a tutor, proof statement, pressure-test and change. The user's pasted card is more Claude-specific and says eight weeks. Preserve requested Claude evidence where possible; a saved context document is a current-guide alternative but does not claim an account or screenshot exists. The proof statement still requires an authentic claim, audience and action chosen by the learner.

### Week 10

Checked [official Week 10](https://aifluency.flyrank.ai/week-10.html#send-the-link). It expands the launch capstone to a custom-domain portfolio, working feature, 3–5 minute demo, build write-up and public story, plus graduate badge/verification and showcase steps. It references design/hardening checkpoints and includes a next-work plan and real reminder. The attachment instead repeats only next-case instructions, next-work naming, reminder evidence and preserved context under both capstone titles. Record both versions; do not treat a local draft as proof of launch, publication, badge eligibility or showcase submission.

## Honest evidence rules for this package

- Direct user facts confirmed through the root agent: **Hamza Afzal**; **Backend Development and Engineering**; audience **a backend engineering lead**; action **invite me to an interview**; GitHub **Hamza2-2**; explicit confirmation of all 12 recurring workflow tasks. Chosen contact route is a GitHub interview-request issue. Confirmed intended next piece: **Deploy and harden the backend review API**. Its production work remains planned. Other toolkit/Academy/Claude account and course evidence remain unconfirmed.
- Notebook execution logs and saved cell outputs can prove local computation. Static prose that describes a run cannot.
- API tests can prove local feature behavior. They do not prove a publicly reachable deployment.
- A calendar import file can prepare a reminder and does not prove calendar installation. The pasted brief explicitly accepts a recurring note, so an actual saved note with a concrete recurring schedule can satisfy that reminder form; state clearly that it produces no automatic notification.
- Written workspace instructions can preserve reusable context. They do not prove a Claude Project was configured.
- Public-facing templates and demo scripts can be prepared. An actual demo recording, public post, domain and portal submission require their own evidence.
- Completion language must distinguish locally verified artifacts from outstanding personal evidence and publication requirements.

## Final publication and verification evidence

- Owned public repository: [Hamza2-2/flyrank-ai-internship](https://github.com/Hamza2-2/flyrank-ai-internship), pushed and anonymously reachable with HTTP 200.
- Primary published [research paper](https://hamza2-2.github.io/flyrank-ai-internship/) and [backend portfolio](https://hamza2-2.github.io/flyrank-ai-internship/portfolio.html) use owned GitHub Pages. Independent unauthenticated fetches returned HTTP 200, and the paper contains required `flyrank.ai` credit. A native [paper mirror](https://hamza-afzal-flyrank-research.chirpy-vine-4912.chatgpt.site) was also verified with a standard browser User-Agent; that mirror's platform can reject a default automated client.
- [Publication receipt](site/publication.json) records primary GitHub Pages publication at commit `d64dc02859e4828dd58f4ba441f5f131e9c015cb` and the verified native Sites mirror. `submission/paper_url.txt` contains exactly the primary direct deployed paper URL. This publishes the paper/portfolio; it does not claim production hosting of the Python API.
- Saved notebook evidence: starter notebooks eight/seven code cells, ML-02 five, capstone nine; all cells executed and all notebooks have zero error outputs. Public GitHub and site-download copies of ML-02/capstone were independently fetched and carry the same executed-cell counts.
- [GitHub Actions](https://github.com/Hamza2-2/flyrank-ai-internship/actions) contains passing runs of all three inherited workflows. Independent final inspection verified the [latest smoke run](https://github.com/Hamza2-2/flyrank-ai-internship/actions/runs/37967384678) and [Pages deployment](https://github.com/Hamza2-2/flyrank-ai-internship/actions/runs/37967386837) were both completed successfully. Later pushes can trigger additional runs.
- Root verified no modifications to upstream reference scripts or bundled data. Eight unassigned notebook templates were relocated and preserved with hashes, then their Colab badge URLs were personalized by the inherited workflow; current hashes are recorded separately. Their code/content was not filled as a completed assignment.
- Actual recurring reminder note, matching local-note screenshot, saved-context copies and current hashes were checked after Hamza confirmed the next case. There is no external calendar import or automatic notification claim.
- No portal submission, reviewer acceptance, certificate award, external Claude Project UI, Academy enrollment/module completion, user-owned custom domain, recorded final demo, graduate badge or showcase submission is established by these artifacts.
