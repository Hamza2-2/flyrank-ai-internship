# Change after the user-provided sitemap pressure test

Implemented by Codex on 10 October 2026 from the recommendation pasted by Hamza. Hamza's personal review and adoption of the change remain to be recorded.

## Weakness identified

The digital sitemap named evidence categories without explicitly identifying direct links. The portfolio had a contract link and a backend-folder link lower in the case, but no three-link evidence strip, recorded test-output link or early visible bad-input response beside the interview action.

## Before

- The map said “Contract + request/response” and “Checks + bad-input example”.
- The portfolio's backend case opened with descriptive paragraphs.
- A contract and repository-folder link appeared later; the recorded test output was not a site download.
- A visitor needed the local interactive demo or README to inspect validation behavior.
- Interview links were in the hero and About/contact section.

## After

- The API case opens with direct links to the OpenAPI contract, exact server source and recorded passing HTTP integration tests.
- Immediately below, a synthetic negative-CTR request and its actually observed HTTP 422 JSON response are inspectable without starting the server.
- The same interview-request action is repeated immediately after the error evidence.
- The sitemap explicitly names the direct contract/source/test-output links and the adjacent interview action.
- Public pages retain the local-prototype limitation. The error response is a recorded example, not a live public API.

## Why this change was implemented

It makes the claim “tested backend API” inspectable and gives a convinced reviewer the interview action beside that evidence. It implements the supplied recommendation without adding competing actions or implying production deployment.

## Source and verification

- Durable site source: `../../scripts/build_site.py`.
- Recorded synthetic HTTP request/response: `../../backend_api/bad_input_example.json`.
- Test output: `../../backend_api/TEST_RESULTS.txt`.
- Browser verification: `../../site/qa/verification.json`.
- The original Codex pressure-test transcript is preserved separately.

The final verification results are recorded in the files above. Complete the review below in Hamza's own words; Codex has not supplied a personal reflection on his behalf.

## Hamza's review — pending

Do I adopt this change? ______

Why does it strengthen my proof? ______

Why does invalid CTR return 422? ______

Real project-chat screenshot saved at: ______
