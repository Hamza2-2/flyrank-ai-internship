# FL-01 — AI Workflow Audit and Tool Setup

Hamza Afzal · Backend Development and Engineering · 2026-10-09

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
