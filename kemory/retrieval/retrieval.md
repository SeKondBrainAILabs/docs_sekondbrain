# How Kemory retrieval works

> Copy source of truth for `kemory/retrieval/index.html`. Edit prose here first, then
> mirror it into the HTML — the same convention as `kemory/docs.md`.

Kemory exposes several ways to read memory, and they are not interchangeable. This page
explains what happens when you search, which tool to reach for, and how to read a result
honestly — including the cases where a tool's name suggests more than it does.

## One engine underneath

Every read path funnels into the same search. It runs up to three legs in parallel and
fuses them by rank:

**Semantic.** Your query is embedded and compared by cosine similarity against every
memory's vector. This is what finds a memory when you describe it loosely.

**Lexical.** Your query's terms are matched as full-text search and ordered by term
frequency and rarity. This is what finds a memory by an exact identifier — a ticket
number, an error code, a config key. Conservative spelling variants are expanded on the
query side, so transliteration pairs that stemming never folds — *vaastu*/*vastu*,
*Raajesh*/*Rajesh* — find each other in both directions. Originals always rank ahead of
variants.

**Blind index (encrypted accounts).** When memory content is encrypted at rest, ordinary
text matching cannot read it. Identifier-shaped tokens are therefore indexed as keyed
hashes when the memory is written, and matched by equality at query time. Prose is never
indexed this way — only identifiers.

The legs are combined with reciprocal rank fusion, then re-ranked on five signals:
semantic similarity (the largest weight), recency, how often the memory has been accessed,
its proximity in the memory graph, and its measured usefulness.

## How you phrase a query changes what you get

Retrieval compares your query against each memory's own wording. A query phrased the way
the note was **written** beats one phrased the way you would describe it to a colleague.

Prefer domain vocabulary, service and tool names, config keys, identifiers and error
strings:

> `CORS_ALLOWED_ORIGINS admin frontend 403`

rather than:

> `why did the admin site stop working`

Both will return something. The first is far more likely to return the right thing.

## Reading a result honestly

Kemory tells you how a search actually ran, and it is worth reading those fields.

**`search_mode_effective`** — what really executed. `hybrid_dense_only` means the lexical
half was skipped because your content is encrypted. Recall is genuinely weaker for rare
tokens in that mode, so **an empty result is not evidence the memory does not exist.**

**`total` and `total_mode`** — for a hybrid search, `total_mode` is `page` and `total`
counts the results on this page, not the memories in your account. Only `exact` mode
totals are corpus counts.

**Page shape** — `top_relevance`, `relevance_spread` and `flat_page` describe the shape of
the result set. `flat_page: true` means the results are a saturated band of near-identical
scores: the signature of nearest-neighbour background noise for a topic your memory does
not actually cover. A page with a genuine match spreads much wider. Read shape rather than
an absolute similarity number — similarity scores drift upward as a store grows, so no
fixed threshold stays meaningful.

## Which tool to use

**`kemory_ask`** — the one federated tool: searches memories, chat turns and files
together (the cross-surface engine below) and, when the question calls for it, synthesises
an answer with citations instead of returning a bare list. Reach for it when you don't
know which surface holds the answer.

**`kemory_recall_memory`** — the main *memory* search. Text query, optional namespace and content
type filters, pagination. `kemory_recall` is a friendlier alias with identical ranking that
can also return your profile in the same call.

**`kemory_find_similar`** — searches by relevance to a reference string. Without
arguments it shares `recall_memory`'s ranking exactly, so the same query returns the same
results in the same order. It additionally accepts **`min_similarity`** — a caller-supplied
floor applied to semantic matches (the same mechanism as recall's `min_relevance`). The
floor is a floor, not a verdict: results stay relevance-ranked, and exact-token (lexical)
hits are never floored, so an identifier match survives any threshold. Absent
`min_similarity`, no threshold applies — see "A fixed similarity floor — inert at scale"
below for why one is not applied by default.

**`kemory_get_context`** — topical context for a conversation, optionally synthesised. Use
it when you want relevant background rather than a list of hits. When the results are flat
background noise it deliberately returns nothing rather than filling your prompt with
near-misses.

**`kemory_get_user_context`** — a cross-namespace overview of everything you have stored.
The right call at the start of a session.

**`kemory_get_session_context`** — a prompt-ready block for one namespace session: recent
exchanges verbatim, older ones folded into a rolling digest.

**`kemory_list_namespaces` / `kemory_list_projects`** — discovery. Worth calling before a
scoped search so you filter on a namespace that exists.

**`kemory_get_raw` / `kemory_get_compressed`** — read a whole namespace, uncompressed or at
a chosen compression tier.

**`kemory_get_history`** — the full provenance of one memory: every state change, who made
it, and why.

## Tuning retrieval (self-hosted)

These are **server-side** settings. On hosted Kemory they are managed for you and cannot be
set per account; they matter if you run Community Edition or your own deployment.

| Variable | Default | What it changes |
|---|---|---|
| `KMV_RRF_K` | `60` | The rank-fusion constant. Lower values let a leg's top hits dominate the merge; higher values flatten the contribution across ranks. |
| `KMV_DENSE_CANDIDATES` | `50` | How many candidates the semantic leg retrieves before fusion. |
| `KMV_SPARSE_CANDIDATES` | `50` | How many candidates the lexical leg retrieves before fusion. |
| `KMV_RANK_W_VECTOR_SIM` | `0.35` | Weight of semantic similarity in the final ranking. |
| `KMV_RANK_W_RECENCY` | `0.20` | Weight of recency. |
| `KMV_RANK_W_ACCESS_FREQ` | `0.15` | Weight of how often a memory has been read. |
| `KMV_RANK_W_GRAPH_PROXIMITY` | `0.15` | Weight of proximity in the memory graph. |
| `KMV_RANK_W_UTILITY_SALIENCE` | `0.15` | Weight of measured usefulness. |
| `MCP_MIN_RELEVANCE` | `0.0` (off) | An absolute similarity floor applied to results. See the note below on why this is off. |
| `GET_CONTEXT_FLAT_GATE` | `true` | Whether `kemory_get_context` suppresses a flat, background-noise page instead of returning it. |
| `KMV_UNIFIED_RRF_RELEVANCE_WEIGHTING` | `true` | Cross-surface search only: weight each result's rank contribution by its within-leg relevance. `false` reverts to pure rank interleaving. |
| `KMV_UNIFIED_V2_PLAN_FOR_CHAT_FILE` | `true` | Cross-surface search only: drive the chat and file lexical legs from the same parsed query plan as the memory leg (phrases, negations, spelling variants). `false` reverts each leg to its own raw-token parse. |

Raising a weight does not raise quality on its own — the five are normalised against each
other, so increasing one necessarily reduces the influence of the rest. Change one at a
time and measure against a labelled set you control.

## What we tried that did not work

Retrieval quality attracts plausible fixes. These were each implemented, measured against a
labelled evaluation set, and rejected. They are documented here so the same ground is not
covered twice — including by us.

**Splitting memories into chunks before embedding — actively harmful.** The intuition is
sound: one vector averaging a long, multi-topic note matches none of its topics sharply.
Measured, the median rank improved while recall@1, recall@5 and MRR all degraded. Chunking
helps some mid-ranked results and hurts the ones that matter most. Splitting notes on their
own structure rather than arbitrary boundaries scored *worse*, not better.

**Cross-encoder re-rankers — no measurable effect.** Two were tried. Neither moved the
numbers enough to justify roughly doubling search latency on CPU inference.

**An asymmetric query prefix for the embedding model — measured negative.** The model
family documents a prefix for query-side encoding. Applying it made results slightly worse
on our corpus, so it ships off.

**Truncation as the explanation — ruled out.** Long notes exceeding the embedding model's
input window were an obvious suspect for poor paraphrase recall. Removing truncation from
the equation did not close the gap; the cause is vocabulary mismatch, not lost text.

**A fixed similarity floor — inert at scale.** The most-requested fix for "irrelevant
results" is a minimum similarity score. It does not work: across a store of ~18,500
memories, a topic provably absent from the store still returned raw similarities of
0.55–0.8, because the nearest-of-N score rises as N grows. Genuine matches score in the
same band. Any threshold high enough to exclude the noise also excludes real answers. This
is why the floor ships off, and why the page-shape signals above exist instead — shape is
scale-invariant, absolute scores are not.

**What did work:** phrasing a query in the vocabulary the memory was written in. That is
the single intervention that has consistently moved retrieval quality, and it is why the
phrasing guidance near the top of this page is the most useful thing on it.

## Cross-surface search

`POST /api/v1/search/unified` searches memories, chat turns and files together — it is
the engine behind `kemory_ask` and the extension's Enhance. Each surface is searched by
its own leg, and two rules govern the merge:

**Scores never compare across surfaces.** The surfaces' raw scores are on different
scales, so each result reports its own leg-native score — compare within a type, never
across types.

**The merge is rank-based, weighted by within-leg relevance.** Pure rank interleaving
treated a leg's weak second hit and another leg's near-top second as equals, producing a
strict round-robin of types. Each contribution is now weighted by how close the hit is to
*its own leg's* best score — a ratio taken inside one leg, so it is invariant to that
leg's scale and the cross-surface rule above still holds. A surface with genuinely weak
results contributes fewer of them.

**All three surfaces share one query plan.** The query is parsed once — quoted phrases as
adjacency groups, negated terms dropped, spelling variants expanded — and the same plan
drives the memory, chat and file lexical legs. A `vaastu` query lexically matches a chat
titled *Vastu Mirror Placement*, not just memories.

## Capture versus consolidate

Two write tools are easy to confuse:

- **`kemory_capture_session`** extracts *many* discrete durable facts from a conversation
  and stores each one.
- **`kemory_consolidate_session`** produces *one* semantic summary of a session.

Use capture when the conversation contained several things worth remembering separately;
use consolidate when you want a single durable record of what a session was about.

## Scoping and isolation

Every read is filtered by user and organisation in the database, not in a prompt. That
applies identically across REST, MCP and every tool listed above. Agents additionally pass
a permission check before any read or write.
