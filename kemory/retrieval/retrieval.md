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
number, an error code, a config key.

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

**`kemory_recall_memory`** — the main search. Text query, optional namespace and content
type filters, pagination. `kemory_recall` is a friendlier alias with identical ranking that
can also return your profile in the same call.

**`kemory_find_similar`** — searches by relevance to a reference string. It currently
shares `recall_memory`'s ranking exactly and applies **no** separate similarity threshold,
so for the same query string it returns the same results in the same order. Choose it for
readability, not for a different algorithm.

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

## Cross-surface search

`POST /api/v1/search/unified` searches memories, chat turns and files together. Each
surface is searched by its own leg and the results are merged **by rank**, because the
surfaces' raw scores are on different scales. Each result reports its own leg-native score,
so compare scores within a type and never across types.

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
