# Recurring portfolio maintenance note

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
