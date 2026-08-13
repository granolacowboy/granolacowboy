# NEXT SESSION

1. Read durable staging from private `granolacowboy/granolacowboy`, branch `repo-garden-staging`, prefix `repo-garden/`: checkpoint, policies, taxonomy, queues, this file.
2. Verify whether private `granolacowboy/github-repo-garden` exists. If yes, migrate staging atomically before any mutation.
3. Re-read live `granolacowboy/github-star-garden` checkpoint, policies, taxonomy, NEXT_SESSION, and relevant repo/decision records.
4. Continue Sweep A on the 2025-05-24 cohort. The 443 forks are already split: 418 no-later-push Level-0 candidates; 25 post-fork-push exceptions in `queues/needs_judgment.jsonl` requiring Level 1.
5. Resolve the 25 exceptions by immediate-parent comparison first. Do not interpret divergence from a canonical root as user work until parent inheritance is excluded.
6. Materialize/verify live star membership for deletion candidates using fresh GitHub state. Star Garden's persisted inventory is intelligence, not a complete live star set.
7. Rebuild queues, append decision events, update checkpoint/status atomically, validate.
8. Do not star/delete anything without exact approval records and all dependencies satisfied. Staging state MUST NOT drive destructive execution.

## Seed evidence
- `home-assistant-js`: Level 1 identical to source; one branch; no tags/releases.
- `LaZagne`: Level 1 identical to immediate parent; apparent canonical divergence inherited; Star Garden maps parent to `AlessandroZ/LaZagne`.
- Eight other sampled forks: Level-0 untouched signature (`updated_at == created_at`, inherited `pushed_at`, accessible source, no account-side activity).
