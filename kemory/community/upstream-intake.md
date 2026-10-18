# Hosted Upstream Intake

Kemory Community is an independent public repository. Hosted Kemory is a
private upstream design and implementation source, so a normal Git merge or
subtree mirror would also import hosted identity, billing, telemetry, storage,
and private dependency assumptions.

Discovery is automated while integration remains reviewed:

1. The Community `upstream intake` GitHub workflow runs daily and on demand.
2. It reads hosted `main` with the repository's read-only
   `KEMORY_UPSTREAM_READ_TOKEN` secret.
3. The intake script compares hosted `main` with the accepted baseline and
   classifies each first-parent change as `port`, `adapt`, `exclude`, `mixed`,
   or `review`.
4. The public Actions summary contains only hashes and aggregate counts. Hosted
   commit subjects and paths are redacted by default.
5. The job fails while review candidates exist, making upstream drift visible.
6. A maintainer reviews details locally, implements compatible behavior on a
   Community branch, runs Docker acceptance tests, records the cohort in the
   delta ledger, and only then advances the accepted baseline.

Classification is triage, not an automatic merge. A `port` result still needs
code-level review because hosted auth, tenancy, encryption, provider routing,
and migrations can be adjacent to otherwise compatible memory behavior.

As of 18 October 2026, the latest automated observation is hosted commit
`b366a39121`. The accepted implementation baseline remains `2aa9da45db`; the
1,003 first-parent commits between them are the review queue, not completed
Community parity.
