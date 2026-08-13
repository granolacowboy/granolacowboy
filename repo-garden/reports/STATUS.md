# Repository Garden Status

Updated: 2026-08-13T04:31:00Z

## Account
- Owned repositories: 1,250
- Forks: 1,205
- Non-forks: 45
- Forks created in 2025: 1,200
- Forks created in 2026: 5
- May 2025 forks: 600
- May 24, 2025 forks: 443

## Sweep A structural segmentation
The 2025-05-24 bulk-fork cohort is now split deterministically:
- 418 forks: no repository push on any later date than 2025-05-24; eligible for Level-0 metadata/star-overlap analysis, not deletion yet.
- 25 forks: later push activity detected; quarantined in `queues/needs_judgment.jsonl` for Level-1 parent/ref comparison before any deletion recommendation.

## Seed safety-tested cohort
- Persisted records: 10
- Recommend `DELETE_REDUNDANT_FORK`: 9
- Recommend `STAR_UPSTREAM_THEN_DELETE`: 1 (`granolacowboy/LaZagne`)
- Approved deletions: 0
- Executed deletions: 0
- Approved stars: 0

The nine deletion recommendations are analysis recommendations only. Seven have no star dependency because Star Garden independently recommends removing the canonical star; two (`BoilingFrogs`, `nsa-rules`) require live-star membership verification before execution because Star Garden classifies the canonical source as KEEP_REFERENCE.

## Durable staging
A private, isolated `repo-garden-staging` branch exists in `granolacowboy/granolacowboy`. Repository Garden state is staged under `repo-garden/`; default `main` is untouched. This is durable but non-authoritative until migrated to `granolacowboy/github-repo-garden`. Mutation queues remain unapproved and MUST NOT execute from staging.
