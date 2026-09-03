# docs.sekondbrain.ai

Public technical documentation for SeKondBrain products. Static HTML, served by GitHub Pages.

This repo gives the Kemory MCP connector a public documentation URL — a page a reviewer or a
prospective user can read and vet *before* connecting anything, without an account and without
claiming a credential.

| | |
|---|---|
| Live | https://docs.sekondbrain.ai |
| Documentation URL for the listing | https://docs.sekondbrain.ai/kemory/ |
| Repo | `SeKondBrainAILabs/docs_sekondbrain` (public) |
| Owner | Product / Kemory |

---

## Layout

```
.
├── index.html              docs root — product index
├── 404.html
├── CNAME                   docs.sekondbrain.ai
├── .nojekyll               serve the tree as-is; no Jekyll
├── assets/
│   ├── style.css           the whole design system, one file
│   └── mark.svg            logomark
├── kemory/
│   ├── index.html          THE published page
│   ├── docs.md             copy source of truth (prose)
│   ├── optimise/           the standing instruction, and where it goes in each AI
│   ├── retrieval/          how search works, which read tool to use
│   └── community/          Community Edition guide and versioned sources
├── legal/                  the four legal documents — see below
│   ├── index.html
│   ├── privacy/            master Privacy Policy v2.7
│   ├── terms/              Terms of Service — Individuals v2.6
│   ├── business-terms/     Business Terms v1.4 + DPA (Schedules 1 and 2)
│   └── extension-privacy/  Kora for Chrome & Kemory privacy companion
├── subprocessors/          sub-processor disclosure — cited by the DPA, keep it live
│   └── index.html
├── tools/
│   ├── gen_tools_table.py  regenerates the tool table from live tools/list
│   └── preflight.py        tag balance, link resolution, no leaked internal notes
└── .github/workflows/
    ├── pages.yml           deploy
    └── tools-drift.yml     fails if the published tool table has drifted
```

**Two files, one page.** `kemory/docs.md` holds the prose; `kemory/index.html` is what ships.
Edit prose in the Markdown first, then mirror it. The tool table between the
`<!-- TOOLS:BEGIN -->` / `<!-- TOOLS:END -->` markers is generated in **both** files — never
hand-edit it.

---

## First-time setup

1. **Push this repo to `main`.**
2. **Settings → Pages → Source → GitHub Actions.** The `pages.yml` workflow does the rest.
   (A branch source also works, but the workflow's pre-flight guard on `CNAME`, `.nojekyll`
   and the two `index.html` files is worth keeping.)
3. **DNS.** Add a `CNAME` record for `docs` pointing at **`sekondbrainailabs.github.io`** —
   the *organisation* Pages host, not a personal one, and not the repo name. Then
   Settings → Pages → Custom domain → `docs.sekondbrain.ai`, and tick **Enforce HTTPS**
   once the certificate is issued.
   **Start this first.** Propagation plus certificate issuance can take up to 24 hours, and
   the Definition of Done requires the URL to return `200`.
4. **Verify the domain at organisation level.** Organisation → Settings → Pages →
   *Verified domains* → add `sekondbrain.ai` and publish the `TXT` record it gives you.
   Without verification, anyone who later points a repo at `docs.sekondbrain.ai` can take the
   subdomain over if our DNS record ever outlives this repo. Cheap, and it applies to every
   future subdomain we publish.
5. **Confirm** `curl -I https://docs.sekondbrain.ai/kemory/` returns `200`.

---

## The legal documents

Four documents, one page each, at `/legal/`. **The source of truth is the legal document, not
this repo** — each page names its source document in an HTML comment at the top, along with
what changed in the current version. Edit the source first, then mirror it here; never let the
two diverge silently.

| Page | Document | Version |
|---|---|---|
| `/legal/privacy/` | Privacy Policy | 2.7 |
| `/legal/terms/` | Terms of Service — Individuals | 2.6 |
| `/legal/business-terms/` | Business Terms + DPA (Schedules 1–2) | 1.4 |
| `/legal/extension-privacy/` | Kora for Chrome & Kemory | 1.1 (companion to 2.7) |

Privacy 2.7, Terms 2.6 and Business Terms 1.4 are **effective 1 October 2026** — 30 days
after publication, per Terms 12.1. Until that date the previously published versions
govern; do not date the source documents earlier than the site says.

Two rules, both enforced by `tools/preflight.py`:

- **Internal drafting apparatus never ships.** The source documents carry drafting notes and
  risk flags addressed to us. The build fails if `Internal drafting note`, `RISK FLAG`,
  `remove before signature` or `ship gate` appears in any published HTML — including inside
  an HTML comment, which is served to the public just like the body.
- **Unfilled brackets are marked, never guessed.** Where a source document still has a `[●]`
  placeholder, it renders as `<span class="gap">` — a visible amber marker. Do not invent a
  value to make a page look finished; an ICO number or an effective date that we made up is
  worse than an obvious gap.

`/legal/extension-privacy/` is the URL to give the Chrome Web Store listing as the extension's
privacy policy.

### Outstanding

- **`/subprocessors` names every provider but is not complete.** Processing regions for Groq,
  Concentrate.ai, OpenRunner, PostHog, Stripe and Notion are marked pending, Notion's
  purpose is unconfirmed, and the speech and email-delivery providers are unnamed. This is
  contractual, not cosmetic: Schedule 1 §3 grounds the general sub-processor authorisation in
  that list, and §4 says transfers occur only as disclosed there — so an undisclosed provider
  is one the DPA does not permit us to transfer to. Tracked as **S9N-6672** (Karol).
- **Cookie inventory.** The Cookie Policy publishes accurate categories, but the per-cookie
  table in §4 is still placeholder pending a runtime audit. Tracked as **S9N-6677** (Karol).
- Backup retention `[90]` days in Privacy §9.2.
- **Source documents are behind the site** for Privacy §7.1 and §8, and Business Terms
  Schedules 1–2. Bring them level or the next mirror will revert what is published.
- **The FZCO trade licence number is still an open bracket** (Terms 4.0). FZCO holds a DMCC
  licence and holds the Stripe account — this is now data entry, not a blocker — but it
  renders as a `gap` until someone supplies the number, and the same number blocks the
  pricing-page footer changes in Core_Kora #188 and Kemory #561. Tracked as **S9N-7313**.
- **Nobody owns refunds or disputes.** Paddle used to issue refunds and absorb chargebacks;
  both now land on us, via a manual Stripe action, and every dispute carries a fee whether
  we win it or lose it. The published wording commits us to acknowledging a request within
  two working days, on three separate pages. **This needs a named owner.**
- **The statement descriptor is unset**, and renders as a `gap` in Terms 4.5A and on the
  Refund Policy. An unrecognised descriptor is the largest single cause of chargebacks —
  which we now pay for. Set it to something a customer will recognise, then fill both.
- **Stripe's processing region is still pending** on `/subprocessors`. This row is now
  load-bearing in a way it was not under a merchant of record: every payment record flows
  through Stripe, and Schedule 1 §4 says transfers occur only as disclosed there. Needs the
  Stripe contracting entity and the region from the account's own Stripe Services
  Agreement. A UAE-domiciled account does **not** imply UAE processing. Part of S9N-6672.
- **Tax registrations are unbuilt and Terms 4.1 already promises the outcome.** Paddle held
  the VAT/GST/sales-tax registrations and remitted on its own numbers; they are FZCO's now.
  The UK has *no* registration threshold for a non-established taxable person, so UK VAT is
  due from the first B2C sale; EU B2C digital services need a non-Union OSS registration.
  Terms 4.1 tells consumers prices already include applicable tax. Either register and
  configure a tax engine before checkout opens, or reword 4.1. Needs the accountants.
- **Renewal reminders do not exist.** Terms 4.1 promises them "where required by law" and
  4.3D now grants a fresh 14-day cancellation right on *every* renewal, everywhere. Paddle
  sent renewal notices; Stripe sends none unless we build them. The DMCC Act subscription
  regime (reminder notices plus a renewal cooling-off period) is expected Spring 2027.
- **Stripe's cookies are in scope for the cookie audit** (S9N-6677). The checkout now runs
  on our own domain, so Stripe.js sets its fraud-prevention cookies first-party.

---

## Keeping the tool table honest

The submission portal syncs tools from the live server and flags any tool missing a `title`
or a behaviour annotation. A hand-maintained table on a public page will drift from the
server within one release, so it is generated:

```bash
# rewrite both files from the live server
python tools/gen_tools_table.py \
  --url  https://api.kemory.s9n.ai/mcp/v1 \
  --api-key "$KEMORY_DOCS_KEY" \
  --write kemory/docs.md --write kemory/index.html

# CI mode — non-zero exit if either committed table is stale
python tools/gen_tools_table.py --url ... --api-key ... \
  --check kemory/docs.md --check kemory/index.html
```

The script fails the build, rather than publishing something misleading, when:

- a tool declares neither `readOnlyHint` nor `destructiveHint` — an unannotated tool must not
  be quietly published as a harmless write;
- a tool has no `title` — the portal rejects that anyway, so catch it here.

To enable the weekly gate, set the `KEMORY_MCP_URL` repository variable and the
`KEMORY_DOCS_KEY` secret (read-only key; `tools/list` performs no writes), then uncomment the
schedule in `tools-drift.yml`.

---

## Design

Everything derives from **SeKondBrain Brand Book v6**. Tokens live in the `:root` block of
`assets/style.css` — colour, spacing, radius, type. Do not introduce a value that is not in
that block.

Per-page mood is one aurora veil, set by overriding `--veil-a` / `--veil-b` in the page's own
`<style>`: blue for Kemory, violet for the index, peach for 404.

`TT Interphases Pro` is licensed and not served here; Inter is the sanctioned web proxy, as
the brand book itself specifies. Swap the `@font-face` source if the licence is extended to
web.

The one deliberate flourish is the tool table: read / write / destructive carry the brand
status-dot colours (mint / amber / danger) with the raw annotation string set in the margin.
That is not decoration — it renders the `readOnlyHint` / `destructiveHint` contract the
directory requires.

---

## Deliberately not documented

- **The `kemory` CLI.** Installing it needs a private repo and GitHub auth, so it cannot be
  documented publicly without describing a path a reader cannot take.
- **The pair-code flow.** It is the internal fast path. A public reader connecting a web AI
  should meet OAuth, and the page must be readable without claiming a code — that was the
  external security feedback that prompted this work.
- **Legacy `/mcp/v1/tools/*` REST sub-routes.** Deprecated; no new client should use them.
- **Per-connector deep dives** (tracked separately).

---

© SeKondBrain AI Labs. Content in this repository is published for users of SeKondBrain
products; it is not open-source software and carries no licence to reuse.
