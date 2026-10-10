# Hamza Afzal — remaining work and submission instructions

Prepared 10 October 2026, Asia/Karachi. These are instructions, not claims that the actions below have happened. Existing artifacts, public repository and starter paper are ready; personal evidence, gated warehouse execution, review and portal submission remain outstanding.

Repository: https://github.com/Hamza2-2/flyrank-ai-internship

Portfolio: https://hamza2-2.github.io/flyrank-ai-internship/portfolio.html

Paper: https://hamza2-2.github.io/flyrank-ai-internship/

Start with [SUBMISSION_INDEX.md](SUBMISSION_INDEX.md). Use the task titles in your signed-in portal as the final upload destinations. ML-02 appears twice in the pasted text; it is one unique deliverable. If the portal actually has separate cards, follow their individual instructions rather than assuming one save populates both.

## A. Accounts and first Academy module

Applies to FL-01 and Draw the Path. Reuse existing accounts.

1. Sign in to Claude, ChatGPT, Gemini and Perplexity as required by the pasted toolkit cards. A paid subscription is not required for the described account setup. Use your existing ChatGPT account if you already have one.
2. Save genuine screenshots showing the tool and your signed-in account/profile. Crop unrelated personal information. Never include passwords, API tokens or recovery codes.
3. For FL-01, save `claude_account.png` and `chatgpt_account.png` in `work/assignments/FL-01_AI_Workflow_Audit_and_Tool_Setup/`.
4. For Draw the Path, save `gemini_account.png` and `perplexity_account.png` in `work/assignments/Draw_the_Path_Portfolio_Sitemap_and_Toolkit/`. Reuse the other two real screenshots where needed.
5. Open [AI Fluency: Framework and foundations](https://academy.claude.com/courses/ai-fluency-framework-foundations). Sign in so progress is recorded, start/enroll in the course, and complete its first instructional section, currently **Introduction to AI Fluency**, including any items the course presents as required for that section.
6. Save `academy_enrollment.png` and `academy_first_module.png` in the FL-01 folder. The screenshots should show the course title and actual saved progress/completion. Finishing only the first section does not earn the full-course badge; do not claim the complete course unless you finish it.
7. Add a dated note to the FL-01 README identifying the evidence files and exactly what you completed. Update the corresponding personal-evidence checkboxes in `work/REQUIREMENTS_MATRIX.md` only after the files exist.

Done when: accounts are usable, first-section progress is genuinely recorded, and the screenshots can be opened by the reviewer.

## B. Configure the Claude Project and run a genuine pressure test

Applies to FL-01, Draw the Path, and preserved context for both AI Fluency capstones.

1. Open [Claude Projects](https://claude.ai/projects), choose **+ New Project**, and name it **Hamza Afzal — Backend Portfolio**.
2. Choose **Set project instructions**, paste the prepared text from `work/context/claude_project_instructions.txt`, and save the instructions.
3. Add `work/context/project_context.md` and the digital sitemap as project knowledge if useful. The custom instructions must include your actual proof statement, audience, interview action and tutor request.
4. Save `claude_project_configured.png` in the FL-01 folder. Include the real project title and saved custom instructions; use two screenshots if one cannot show both clearly.
5. Inside the project, attach the map from `work/assignments/Draw_the_Path_Portfolio_Sitemap_and_Toolkit/sitemap.png` and submit this prompt:

   > My claim is: I can build a tested backend API that converts anonymized search signals into explainable content-review priorities. My audience is a backend engineering lead; my one action is an interview invitation. Pressure-test this sitemap. Does it move the reviewer from landing, to evidence, to the action? Identify a specific weakness and one change that would strengthen the proof. Explain your reasoning as my tutor.

6. Save the actual prompt and answer as `claude_pressure_test.md` in the Draw the Path folder. Capture the conversation as `claude_pressure_test.png`; multiple images are acceptable if the answer is long.
7. Evaluate the suggestion yourself. Implement one justified change, or document a specific existing change that the actual response supports. Record the exact before/after and why in `change_after_pressure_test.md`. Do not invent a change or silently replace the earlier real Codex pressure test.
8. If you alter the sitemap/site, change the editable source or generator and regenerate the relevant artifact; changing only a generated HTML file will be lost on the next build.
9. Add the configured-project screenshot and pressure-test evidence to Draw the Path as well. Reference the genuine preserved project from both AI Fluency capstone READMEs.

The live Week 1 guide accepts a Claude/ChatGPT Project, Gemini Gem or persistent context document. Our existing saved context and real Codex screenshots are therefore a documented alternative. The Claude route above directly matches the more specific pasted FL-01 wording. Use the alternative if your portal card permits it; do not buy a subscription merely to replace an accepted context-document route.

Sources: [Claude project instructions](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects), [FlyRank Week 1 workspace alternatives](https://aifluency.flyrank.ai/week-01).

## C. Photograph a real sitemap sketch

Applies to Draw the Path.

1. Open the prepared `sitemap.png` as your reference.
2. On paper, draw the small flow: **Landing/claim → API case and evidence → interview-request action**. Add the short About section and supporting research link. Show the actual page/section relationships, not extra pages that do not exist.
3. Label each box with its purpose for the backend lead. The API evidence box should mention contract, valid/invalid requests, tests and reason codes.
4. Photograph the page in good light, with all labels readable.
5. Save it as `sitemap_sketch_photo.jpg` in `work/assignments/Draw_the_Path_Portfolio_Sitemap_and_Toolkit/`. Upload this photo together with the digital map, rather than describing the digital rendering as a photograph.

Done when: the genuine photo shows your compact navigation/proof flow clearly.

## D. Understand and demonstrate the backend and research

Applies to What Are You Proving?, ML-01, ML-02 and both research/portfolio capstones.

1. Read `work/backend_api/README.md`, `server.py` and `openapi.json`; read the four already executed assignment/capstone notebooks and the paper.
2. In PowerShell terminal 1, run:

   ```powershell
   Set-Location -LiteralPath 'D:\flyrank'
   .\.venv\Scripts\python.exe -X utf8 work/backend_api/server.py
   ```

3. In PowerShell terminal 2, run:

   ```powershell
   Set-Location -LiteralPath 'D:\flyrank'
   .\.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory work/site/dist
   ```

4. Open `http://127.0.0.1:8000/portfolio.html`, then use **Send local API request**. The real Python backend must be running for this local demonstration.
5. Show `/health`, one valid synthetic request, the score/reason codes, and one invalid request such as a negative CTR. Verify the expected 200 and 422 responses. The documented valid example scores 9.24.
6. In another terminal, run:

   ```powershell
   Set-Location -LiteralPath 'D:\flyrank'
   .\.venv\Scripts\python.exe -X utf8 work/backend_api/test_api.py
   ```

7. Save your explanation in `work/context/my_understanding.md`. In your own words answer: What does the API accept? Why are requests bounded? How are ties resolved? What does position zero mean? Why does the POST endpoint use a fixed rule rather than the trained model? Why does the starter study not establish future prediction or causal refresh benefit? Why are clients separated in validation?
8. Re-run the ML assignment notebooks top to bottom when validating them personally. Use the local `.venv`/`flyrank` kernel and save the genuine outputs; do not discard cells or paste synthetic results into their outputs.
9. Stop the servers with Ctrl+C after the demonstration. The public static portfolio does not run the Python backend; describe the demo as local unless a real production deployment is completed.

Done when: you can reproduce the example, explain the errors and limitations, and answer the questions without reading an AI-written script.

## E. Sign in privately and execute the full warehouse study

Applies to Hugging Face evidence in ML-01 and the strict ML capstone.

### E1. Accept access and save local authentication

1. Sign in to your own Hugging Face account and open [FlyRank/internship-warehouse](https://huggingface.co/datasets/FlyRank/internship-warehouse).
2. Read/accept its access conditions. Accepting access shares the requested contact details with the dataset owner. Save `huggingface_access.png` in the ML-01 task folder showing access granted or an accessible file list, without token details.
3. In your own PowerShell terminal, run:

   ```powershell
   Set-Location -LiteralPath 'D:\flyrank'
   .\.venv\Scripts\hf.exe auth login
   .\.venv\Scripts\hf.exe auth whoami
   ```

4. Follow the browser flow, or enter a read token privately when the CLI requests it. Never paste a token into chat, a notebook, a screenshot or a command argument. Accepting the browser gate and storing the local login are separate steps. The script reads the saved login automatically.

Sources: [warehouse access terms](https://huggingface.co/datasets/FlyRank/internship-warehouse), [official HF CLI authentication](https://huggingface.co/docs/huggingface_hub/en/guides/cli).

### E2. Run the guarded notebook

The prepared notebook has only run offline plan/synthetic checks so far. Those outputs do not count as warehouse analysis.

1. Register the local kernel if necessary:

   ```powershell
   .\.venv\Scripts\python.exe -m ipykernel install --user --name flyrank --display-name 'FlyRank (.venv)'
   ```

2. Check the runner without starting a warehouse query:

   ```powershell
   .\.venv\Scripts\python.exe -X utf8 work/scripts/execute_warehouse_notebook.py
   ```

3. After login/gate access is ready, execute every notebook cell:

   ```powershell
   .\.venv\Scripts\python.exe -X utf8 work/scripts/execute_warehouse_notebook.py --run
   ```

4. The runner enables the gated switch in memory. The underlying stages are **inspect → develop March → aggregate non-June facts → freeze development model/contract → evaluate June**. Keep the window/model choices fixed and let each stage finish.
5. On verified success, the runner saves `work/notebooks/warehouse_extension.ipynb` with genuine outputs. It stops without saving a new canonical deliverable if authentication, schema, a stage or the result checks fail.
6. Inspect `work/outputs/warehouse_metrics.json`, `warehouse_frozen_contract.json`, `warehouse_ranked_actions.json` and the generated capstone-folder `warehouse_report.md`. Confirm the completed status, cohort/coverage counts, selected model, baseline comparison and limitations.
7. If a stage fails, stop and read [warehouse_execution.md](capstones/ML_Google_Search_Ranking_and_Discoverability/warehouse_execution.md). Resolve the actual access/schema/quality issue. Do not delete June markers, change the frozen model after outcomes, or keep rescanning on HTTP 429. Exact validated receipts/caches can be reused; later fresh reproductions use the documented isolated replay mode.

Private aggregates, hash IDs, fitted models and case lookups remain in ignored `work/outputs/warehouse_cache/` or `warehouse_replays/`. Publish only the approved aggregate evidence and notebook. The source dataset forbids raw redistribution and re-identification.

### E3. Review the recommendations and finish the paper

1. Review the 20 actual recommendations after genuine execution. Use [editor_review_template.md](capstones/ML_Google_Search_Ranking_and_Discoverability/editor_review_template.md) for synthetic case label, reviewed material, decision and rationale.
2. Request approved anonymized content/query context from your mentor when needed. The numeric dataset does not contain page text or readable query intent. Structural checks of reason codes are possible from the authorized local aggregates; they do not replace content review. If the necessary content is unavailable, record that limitation and ask the reviewer whether it is acceptable for your chosen lane. Do not invent accept/reject judgments.
3. Update `work/capstone_report.md` with actual warehouse methods and results, preserving the starter comparison as a clearly labeled separate study. Cover all required sections: title/five-sentence abstract, problem, data, baseline/methods, evaluation/charts, interpretation, ranked actions, limitations/reproduction, and FlyRank credit.
4. Generate plots from the actual warehouse metrics: at minimum baseline-versus-model results/review budgets and cohort/coverage/attrition. Report effective K, base rate, held-out clients/time windows and uncertainty. Do not transfer starter precision numbers into warehouse sections.
5. Update `work/scripts/build_site.py` explicitly: it currently reads starter metrics/actions. Its headline metrics, interactive comparison and recommendations must use the intended study's actual JSON schema and labels. Warehouse baseline is `prior_rule`; starter baseline is `rule_baseline`. Keep them distinct. Add the genuine warehouse notebook/results to safe downloads.
6. Update `model_card.md`, capstone README, submission index and matrix to match executed evidence. Do not claim causal editorial gains or prospective live data collection from a finalized historical snapshot.
7. Rebuild, check and publish using section G. Verify the public page displays the actual warehouse results. Check root `submission/paper_url.txt` still contains exactly the direct paper URL on one line.

Done when: actual gated stages pass, the canonical notebook has outputs, editorial review/limits are documented, and the public paper/source agree.

### E4. Handoff if you want help integrating the actual results

After your private login works, use this prompt in a new conversation opened in `D:\flyrank`:

> Complete the Google Search Ranking & Discoverability capstone using the genuine gated warehouse. Read AGENTS.md and the skill router first. Use the prepared guarded runner, respect the frozen June holdout and private-cache rules, and execute the notebook top to bottom. Integrate verified warehouse results into the paper, model card and static site without mixing starter and warehouse metrics. Verify the backend/site and publish the reviewed public artifacts to the existing repository. Record unavailable editorial context honestly and tell me what human review and portal actions remain. Do not print tokens or redistribute private data.

The assistant can implement the paper/site changes from actual outputs. Account login, your own explanation, real content review and portal reviewer approval remain separate actions.

## F. Finish the AI Fluency maintenance and launch evidence

### F1. Maintenance — required by both pasted capstone briefs

1. Open each capstone's existing `deliverable.pdf`; check the next-case steps and intended work are accurate.
2. Preserve the actual configured project/context from section B. Reference or attach the screenshot in each capstone submission.
3. The existing recurring note already supplies the pasted brief's permitted reminder format. It starts **Friday 16 October 2026, 18:00 Asia/Karachi**, repeats weekly and names **Deploy and harden the backend review API**.
4. If you want phone/calendar notifications, create that weekly event in your calendar or import `work/context/portfolio_maintenance_reminder.ics`. Verify the actual time, recurrence and notification, then save `calendar_reminder_configured.png` in both capstone folders. Only then change the documentation from unimported to imported/configured.
5. Production backend deployment is the named next case, not a requirement to pretend future work is already complete.

### F2. Broader live Week 10 package — match to your portal card

The [current Week 10 guide](https://aifluency.flyrank.ai/week-10.html) adds custom-domain launch, a 3–5 minute demo, build write-up, public story, badge/showcase and passed design/hardening checkpoints. Your pasted capstone text is narrower. Check the signed-in card and applicable review requirements before treating the broader package as satisfied or unnecessary.

1. **Domain, if required:** use a domain you own. In the repository, open Settings → Pages → Custom domain and save it before changing DNS. For a `www`/other subdomain, set its CNAME to `hamza2-2.github.io` without the repository name; use the official GitHub instructions for an apex domain. Enable HTTPS when available. Pull GitHub's CNAME commit and preserve it in the publishing directory. The current portfolio is `/portfolio.html`; verify that actual path on the domain. Update direct paper/publication URLs after a domain change. Follow [GitHub's domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
2. **Demo:** record 3–5 minutes showing the live portfolio, your claim/audience/action, actual code/contract, a working valid API request and invalid-request error, one concrete AI contribution, and one real limitation. Show the local URL when using the local API; do not present it as a public deployed backend. Save `demo.mp4` in the Send the Link folder and/or upload it to a reviewer-accessible video URL.
3. **Build write-up:** create `build_writeup.md` in that folder. Explain the actual Python/static-site stack, why you chose it, one real problem/fix, the tests and next deployment case. Use your own understanding, not invented experiences.
4. **Public story:** draft 200–300 words in your own voice about what you built, where AI helped, one real win and one limitation. Publish it yourself to a channel you use, then save `public_story_url.txt` with its actual URL. A draft is not a published post.
5. **Working feature/checkpoints:** verify the live feature on a fresh try and obtain the required design/hardening reviews if the current portal demands them. GitHub Pages serves static files and cannot run this Python server. If a public API is required, implement the planned production case: a production adapter/server, HTTPS, authentication, rate limits, public-origin CORS, configurable API URL, health monitoring, endpoint tests and rollback. Record the real deployment before changing the portfolio's local-only claim.
6. **Badge/showcase:** use only the badge and verification URL actually issued by FlyRank. Install it in the footer after eligibility is confirmed and submit the real site/package to the official showcase. Record the real URL/receipt. Do not fabricate a badge or verification page. Optional featured-case-study participation is your choice.

Done when: the applicable portal package has real, accessible evidence for every required component; the existing PDFs alone do not establish the broader launch criteria.

## G. Update GitHub and verify publication after new work

The Git/gh executables are installed locally under `.tools`; ordinary `git` may not be on your PATH.

1. Before sharing, keep account/course screenshots private in portal Files if they contain personal information. Add only intended public, sanitized evidence to GitHub.
2. After changing the paper/site source, run:

   ```powershell
   Set-Location -LiteralPath 'D:\flyrank'
   .\.venv\Scripts\python.exe -X utf8 work/scripts/build_site.py
   .\.venv\Scripts\python.exe -X utf8 work/scripts/check_site.py
   ```

3. Inspect and stage only the public files you changed. Use exact filenames for screenshots/review logs, rather than uploading an entire private folder:

   ```powershell
   .\.tools\git\cmd\git.exe status --short
   .\.tools\git\cmd\git.exe add work/notebooks/warehouse_extension.ipynb work/capstone_report.md work/scripts/build_site.py work/capstones/ML_Google_Search_Ranking_and_Discoverability/README.md work/capstones/ML_Google_Search_Ranking_and_Discoverability/warehouse_report.md work/capstones/ML_Google_Search_Ranking_and_Discoverability/model_card.md docs work/site/dist
   .\.tools\git\cmd\git.exe diff --cached --stat
   .\.tools\git\cmd\git.exe diff --cached
   .\.tools\git\cmd\git.exe commit -m 'Complete verified warehouse study and update paper'
   $env:Path='D:\flyrank\.tools\git\cmd;D:\flyrank\.tools\gh\bin;' + $env:Path
   .\.tools\git\cmd\git.exe push origin main
   ```

   Use that stage list only after those files actually exist and are ready; add the particular reviewed aggregate JSON/figures and index changes separately. Never force-add caches, raw datasets, tokens or a private editorial log.

4. Wait for the relevant commit's GitHub Actions/Pages deployment to pass. Open the paper, portfolio and download links while logged out. Verify actual latest content, mobile layout, working links and FlyRank credit.
5. If also maintaining the native Sites mirror, deploy the updated exact source through the existing Sites project workflow; a GitHub push updates GitHub Pages only. The direct submission URL currently uses GitHub Pages.

## H. Submit each task in the portal

The [official submission walkthrough](https://aifluency.flyrank.ai/assignments) describes this flow:

1. Sign in to https://internship.flyrank.ai and open **Assignments**.
2. Open the exact task card, find **Submission**, and check its current requirements.
3. Under **Deliverable links**, put one public URL per line. Do not put a Windows file path or explanatory paragraph in that field.
4. Under **Files**, attach the task's PDF and real screenshots/photos/video that are not supplied by URL. Portal file attachments are the appropriate private route for personal screenshots.
5. Use **Notes** for context, AI assistance, chosen scope and actual remaining limits. Notes alone are not the deliverable.
6. Click **Save submission**, reopen the card and confirm the links/attachments/save are present. Save a private confirmation screenshot if useful. A save is a submission, not a pass/certificate award.
7. If the reviewer requests revisions, make the change, update the public version/evidence, and save the submission again.

| Card | Links/files to hand in after completion |
|---|---|
| FL-01 | Task-folder `deliverable.pdf`; real configured-project screenshot; account and Academy evidence; audit already includes three measurable targets |
| ML-01 | Repository root URL; both genuinely executed starter notebooks in the repo; actual HF account/gate evidence if requested |
| Draw the Path | Task-folder PDF; real sketch photo; configured workspace screenshot; actual pressure-test prompt/output and change log |
| What Are You Proving? | Task-folder PDF or public proof-statement link, including the paragraph and one-line why |
| ML-02 | Repository root URL with executed `work/notebooks/w01_research_question.ipynb` |
| General AI Fluency Impact Project | Its own PDF, next-work/maintenance note, preserved project/context and actual reminder evidence |
| Send the Link | Its separate PDF/maintenance/context/reminder evidence; add live domain, demo, write-up, public story, badge/showcase/checkpoint evidence if required by the current card |
| Google Search Ranking & Discoverability | Repository root URL, direct public paper URL, genuinely executed capstone/warehouse notebook, actual analysis evidence and required editorial review/limits |

For the ML cards, use the repository root URL: **https://github.com/Hamza2-2/flyrank-ai-internship**. The direct paper URL is **https://hamza2-2.github.io/flyrank-ai-internship/** until an actual verified domain change occurs.

Certificate check: the pasted FAQ asks for at least five assignments plus a capstone from the main track. This supplied set has three AI Fluency and two ML assignments. Review the main-track portal checklist, including applicable checkpoint reviews, before claiming certificate eligibility; this document does not complete additional unrequested cards.
