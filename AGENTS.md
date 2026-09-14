# X-AI-Radar

Collects recent AI/developer and education sources and produces Korean reports in `reports/`. Project behavior is implemented by Python collectors and adapters, not by a required model or agent roster.

## Boundaries
- Source collection is read-only: never like, repost, reply, follow, bookmark, quote or submit forms on X or other source sites.
- Research, ranking or report-generation requests do not authorize Telegram, Slack/Discord webhooks, Git publication or other external writes. Delivery needs approval covering destination and content, or matching recurring-delivery authorization. Verify final Korean text and destination; preserve existing approval reuse rules.
- Current `scripts/collector.py` calls `send_notifications`; `scripts/edu_collector.py` calls Telegram delivery. The CLI and run wrappers are not guaranteed collection-only entrypoints. Inspect the chosen path's side effects before running it; do not invoke a delivery-capable workflow under research-only authorization.
- Keep `.env`, tokens, `data/*.json`, browser profiles and temporary logs out of Git and reports. Do not print secret values.
- Preserve 24-hour source-time checks, state/history-based velocity scoring and the education planner's three-topic output. Do not claim a fixed runtime without measuring it.

## Read by task
- Topics, channels and presets: `docs/CUSTOMIZATION_GUIDE.md` or its Korean counterpart.
- Collection/scoring: `scripts/collector.py`, `scripts/edu_collector.py`, `scripts/adapters/`; preserve `cdp_send_sync` response handling and resource blocking where applicable.
- Delivery: `scripts/notifier.py` and the selected collector's actual send path.
- Routine report workflow: `.agents/skills/x-ai-radar/SKILL.md`.

## Verification
Use offline/static checks for changed Python or shell code and synthetic fixtures if available. Do not execute collection, notification or publication merely to validate documentation. Report external/browser checks separately when they were not run.
