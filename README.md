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
│   └── docs.md             copy source of truth (prose)
├── tools/
│   └── gen_tools_table.py  regenerates the tool table from live tools/list
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

## Keeping the tool table honest

The submission portal syncs tools from the live server and flags any tool missing a `title`
or a behaviour annotation. A hand-maintained table on a public page will drift from the
server within one release, so it is generated:

```bash
# rewrite both files from the live server
python tools/gen_tools_table.py \
  --url  https://kemory.sekondbrain.ai/mcp/v1 \
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
