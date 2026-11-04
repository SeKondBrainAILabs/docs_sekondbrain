# Hosted Upstream Intake

Kemory Community is an independent public repository. Hosted Kemory is a
private upstream design and implementation source, so a normal Git merge or
subtree mirror would also import hosted identity, billing, telemetry, storage,
and private dependency assumptions.

Discovery and queue maintenance are automated while integration remains
reviewed:

1. The Community `upstream intake` GitHub workflow runs daily and on demand.
2. It reads hosted `main` with the repository's read-only
   `KEMORY_UPSTREAM_READ_TOKEN` secret.
3. The intake script compares hosted `main` with the accepted baseline and
   classifies each first-parent change as `port`, `adapt`, `exclude`, `mixed`,
   or `review`.
4. The public Actions summary contains only hashes and aggregate counts. Hosted
   commit subjects and paths are redacted by default.
5. The workflow commits the redacted observation to the fixed
   `automation/upstream-intake` branch and opens or refreshes one review pull
   request. It closes that pull request when no candidates remain.
6. The job fails while review candidates exist, making upstream drift visible.
7. A maintainer reviews details locally, implements compatible behavior on a
   Community branch, runs Docker acceptance tests, records the cohort in the
   delta ledger, and only then advances the accepted baseline.

The workflow never imports hosted source, advances the accepted baseline, or
merges its own pull request. Classification is triage, not an automatic merge.
A `port` result still needs code-level review because hosted auth, tenancy,
encryption, provider routing, and migrations can be adjacent to otherwise
compatible memory behavior.

As of 24 October 2026, the latest automated observation is hosted commit
`1b0bddd450` (`v4.266.1`). The accepted implementation baseline remains
`2aa9da45db`. The intake inspected 1,159 first-parent changes: 1,075 adapt,
36 mixed-boundary, 46 manual-review, and two excluded-only. The 1,157
non-excluded candidates are a review queue, not a completed parity claim.

## Repository secrets

The repository requires two Actions secrets:

- `KEMORY_UPSTREAM_READ_TOKEN` can clone only
  `SeKondBrainAILabs/Kemory`. Use a fine-grained, read-only token.
- `KEMORY_COMMUNITY_SYNC_TOKEN` can write branches and pull requests only in
  `SeKondBrainAILabs/kemory-community`. It is required because the organisation
  disables pull-request creation by the workflow `GITHUB_TOKEN`.

Replace broader bootstrap credentials with these least-privilege grants as
soon as fine-grained tokens are available. Branch protection and required
human review still gate `main`.

## Notion feature decisions

The canonical Product x Features database uses `Community Edition` as the hard
inclusion gate for Kemory and Chrome Extension features. Only a checked feature
may enter a Community porting cohort. An unchecked feature remains outside the
cohort even when automated intake detects related hosted changes.

`Community status` records the lifecycle behind the gate:

- `Shipped` - verified in a tagged Community release.
- `Adapted` - implemented with Community-specific runtime or security changes.
- `Planned` - approved for a future Community cohort.
- `Excluded` - intentionally outside the Community product boundary.
- `Review` - not yet classified.

`Community evidence` records the implementation or exclusion rationale. Do not
mark a hosted feature `Shipped` from intake evidence alone. Link its Community
pull request, tests, and release tag first.

The `Community Edition intake` view is the allowed feature set. The
`Community Edition review` view is the decision queue. Chrome Extension
features start unchecked and in `Review`; each requires explicit approval.
