# Kemory

**Persistent, permissioned memory for AI agents.**

> This file is the copy source of truth for `kemory/index.html`. Edit prose here first,
> then mirror it into the HTML. The tool table between the `TOOLS` markers is machine-
> generated in both files — do not hand-edit it. See `tools/gen_tools_table.py`.

Kemory gives an AI something it does not have on its own: recall. An assistant that reads
from Kemory at the start of a session knows what you told it last week, in a different
client, on a different machine. What it learns, it can write back. Every memory is scoped
to a user and an organisation, and that scoping is enforced in the database rather than in
a prompt.

Kemory is a remote MCP server. You connect to it once, from any MCP-capable AI, and it is
available to every session after that.

---

## Before you connect

You need a SeKondBrain account. Sign-in is handled by SeKondBrain's identity service — Kemory
never sees or holds a password.

There is nothing to install for a web AI. Local clients need a config-file entry, shown below.

**The server address:**

```
https://api.kemory.s9n.ai/mcp/v1
```

Every user connects to the same address. There is no per-tenant URL and nothing to
provision before you begin.

**Transport:** Streamable HTTP, JSON-RPC 2.0, single endpoint. Protocol revisions
`2024-11-05` through `2025-11-25` are negotiated on `initialize`. Server-sent events,
server-initiated messages and persistent sessions are deliberately not implemented — every
request is stateless and self-authenticating.

---

## Connect a web AI

For Claude, ChatGPT, Perplexity, Manus and any other AI that supports remote MCP connectors.

1. Open your AI's connector settings and choose **Add custom connector**.
2. Paste the server address above.
3. Your browser opens a SeKondBrain sign-in page. Sign in and approve.
4. The connector reports the tools it found. You are connected.

There is no key to copy, paste or keep safe. The connector holds a short-lived token that
refreshes itself and that you can revoke at any time from your Kemory dashboard.

Connected is not the same as remembering: a model decides for itself when to call a tool,
and an AI given one with no instruction about it will usually not reach for it.
[Optimise your AIs for Kemory](optimise/) is the standing instruction that fixes that, and
where to paste it.

**What you are approving.** The sign-in screen asks you to let this AI act as you inside
Kemory — read your memories, write new ones, and delete memories you point it at. It does
not grant the AI access to anything else in your SeKondBrain account, and it does not grant
access to another user's memories, including colleagues in the same organisation.

---

## Connect Claude Code

Claude Code has a plugin, and it is the better path: browser sign-in instead of a key in a
file, and hooks that make memory get used rather than merely be available.

Install the CLI and sign in:

```bash
brew install sekondbrainailabs/s9n/kemory
kemory login
```

OAuth browser sign-in — nothing to copy or paste. No key is written into any config file:
the credentials land in `~/.kemory/credentials`, and the plugin reads them at runtime.

Then, inside Claude Code:

```
/plugin marketplace add SeKondBrainAILabs/claude-kemory
/plugin install kemory@kemory
/kemory:status
```

`/kemory:status` reports whether credentials resolve, whether the API accepts them, and
whether the CLI is on PATH. All green means done. Context injection begins with your next
session, because the hook that performs it fires at session start.

### What the plugin adds

Connected is not the same as remembering. The plugin closes that gap with four hooks that
fire without anyone having to ask:

| Hook | When | What it does |
|---|---|---|
| `session-start.sh` | Session start | Injects your namespace summaries, so the session begins informed rather than blind |
| `rate-reminder.sh` | After any recall tool | Reminds the agent to rate what it actually used, so retrieval keeps improving |
| inline | Before compaction | Prompts consolidation before a long session is summarised away |
| `capture.sh` | Session end | **Opt-in.** Stores a bounded, redacted digest of the session |

It also ships the `/kemory:status` command and a skill covering how to recall, rate, store
and phrase memories so semantic search can find them again — the standing instruction from
[Optimise your AIs](optimise/), already written and kept current.

Source: [SeKondBrainAILabs/claude-kemory](https://github.com/SeKondBrainAILabs/claude-kemory).

**Already using the connector?** Adding *Kemory by SeKondBrain* in your claude.ai connector
settings gives you the tools in Claude Code too. Do not run that alongside the plugin's
bundled MCP server — two servers means two copies of every tool in every request. The hooks
are separate from MCP and work either way, provided `kemory login` has run.

**Prefer no plugin?** The manual entry under [Connect a local client](#connect-a-local-client)
works for Claude Code as well.

---

## Connect a local client

For Claude Desktop, Cursor, Cline, Windsurf, Warp, Codex, Gemini CLI and any other client
that reads MCP servers from a config file. Claude Code has a plugin instead — see
[Connect Claude Code](#connect-claude-code).

These clients authenticate with an API key sent as an `X-API-Key` header. Create one from
**Dashboard → Keys**. It is shown once.

The entry below is exactly what a local client needs. Read it before you connect anything —
this is the whole surface.

```json
{
  "mcpServers": {
    "kemory": {
      "type": "http",
      "url": "https://api.kemory.s9n.ai/mcp/v1",
      "headers": {
        "X-API-Key": "kemory_REPLACE_WITH_YOUR_KEY"
      }
    }
  }
}
```

| Client | Config location |
|---|---|
| Claude Code | `~/.claude.json` — but prefer the [plugin](#connect-claude-code) |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| Cursor | `~/.cursor/mcp.json` |
| Cline | VS Code settings → Cline → MCP servers |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Warp | Settings → AI → MCP servers |
| Codex | `~/.codex/config.toml` |
| Gemini CLI | `~/.gemini/settings.json` |

Restart the client fully after editing — quitting the window is not enough. Ask it to list
your Kemory namespaces; a response means all three gates (authentication, agent
registration, permissions) are green.

A key inherits the organisation of the person who created it, so an agent holding one stays
inside your tenant. Keys can be listed and revoked from the dashboard, and revocation takes
effect on the next call. Never commit one.

There is also a command-line tool that writes this entry for you, using a browser login
instead of a key in a file — useful if you are wiring several clients on one machine. See
the [Kemory CLI](cli/).

### Making an AI actually use memory

Most clients treat a tool as something to reach for when asked. Put this in your project
instructions or `CLAUDE.md` and it becomes the first thing checked instead:

```markdown
You have Kemory memory tools available.

At the start of each session: call kemory_list_namespaces, then
kemory_recall_memory on the current topic.

Write a memory immediately when: I state a preference or a way of working,
we make a decision, or we learn something non-obvious about this codebase
or domain. Tell me what you wrote and to which namespace.

Do not write credentials, keys or passwords into memory unless I ask you to.
```

[Optimise your AIs for Kemory](optimise/) has the same instruction sized for every field it
has to fit in, and names where that field lives in each AI.

---

## Quickstart

Write one memory, then read it back in a session that has never seen it.

**1. Write it.** Ask your AI:

> Remember that I prefer imperative-mood commit messages, no emoji.
> Put it in `user:preferences`.

It calls `kemory_store_memory` and tells you the namespace it used.

**2. Read it back.** Quit the client entirely and reopen it — a new chat is not enough,
the point is to cross a process boundary. Then ask:

> What is my commit-message preference?

It calls `kemory_recall_memory` and answers correctly.

That is the whole product. Everything below is detail.

---

## The tools

<!-- TOOLS:BEGIN -->
Kemory exposes **28 tools**, all prefixed `kemory_`. Every one carries a `title` and MCP
behaviour annotations, so your client can tell reading from writing from deleting before it
runs anything.

### Read-only — `readOnlyHint: true`

| Tool | What it does |
|---|---|
| `kemory_ask` | SURFACES: memories, chat turns AND files — the ONLY search tool that reads all three; every kemory_recall* tool reads memories alone. If a conversation might hold the answer, this is the tool (S9N-7495). |
| `kemory_check_access` | Check if the current agent has permission to perform an action. Returns the Gatekeeper evaluation result without performing the action. |
| `kemory_find_similar` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three (S9N-7495). |
| `kemory_get_compressed` | Tiered namespace compression. mode='aaak' returns the L2 lossless dialect encoding for byte-oriented storage/export diagnostics; do not inject AAAK into prompts as a token-saving context format. mode='concept' returns L3.1 LLM-synthesized concepts via core-ai-backend. merge_mode='current' picks the latest position in directional sequences; 'aggregate' synthesises all positions. mode='raw' is deprecated — use kemory_get_raw, which pages and reports has_more; raw calls here may serve one bounded page (check has_more/note in the result). Requires memory:read permission. |
| `kemory_get_context` | Get contextual memories relevant to a conversation or topic. Searches across all accessible namespaces (or a specific namespace) and returns the most relevant memories, optionally synthesised by the AI backend. Requires memory:read permission. |
| `kemory_get_history` | Return the full provenance history of a memory — every state change with actor, reason, and before/after snapshots. Requires memory:read permission. |
| `kemory_get_namespace_summary` | Get one namespace's consolidated cross-session summary: its human-readable description, the rolling L3.1 summary (falling back to the latest L3.0 concept memory when L3.1 has not been synthesised yet), the summary tier and when it was last updated, plus any related namespaces the matcher flagged as near-duplicates. Use this to orient on a single namespace before recalling from it. Requires memory:read permission on the namespace. |
| `kemory_get_profile` | Return the user's PERSISTED profile — 'static' (stable preferences) and 'dynamic' (recent activity) halves, served from a stored row in one lookup with no LLM call; the row rebuilds lazily when stale. Use section to fetch one half, refresh=true to force a rebuild. Requires memory:read permission. |
| `kemory_get_raw` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three (S9N-7495). |
| `kemory_get_session_context` | Get an optimized, prompt-ready context block for one namespace session. This keeps the latest raw user/assistant exchanges readable and folds older exchanges into a rolling token-budgeted digest. Namespace and session summaries are included as long-term background orientation; the digest itself is grounded only in prior digest + source exchanges. AAAK is never returned here because AAAK is byte-oriented storage/export compression, not the default LLM-context representation. Append the current user message after this tool output. |
| `kemory_get_user_context` | Get a cross-namespace memory overview for the user. Ideal for session-start context injection — gives the agent a single block covering all of the user's memory namespaces. |
| `kemory_list_namespaces` | List all namespaces in the user's S9N Memory Vault with memory counts and existing second-tier tags. Use this before store_memory so a new write reuses an established tag instead of fragmenting the namespace. |
| `kemory_list_projects` | List the user's projects with their namespace mapping and memory counts. Explicit projects (created aliases spanning 1+ namespaces) merge with implicit ones (bare project:* namespaces). Pass a returned project name to kemory_memory / kemory_recall via their 'project' argument for project-scoped writes and reads. |
| `kemory_list_skills` | List all stored agent skills — learned procedures with name, trigger, and steps. Requires memory:read permission. |
| `kemory_recall` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three (S9N-7495). |
| `kemory_recall_memory` | Search and retrieve memories from the user's S9N Memory Vault. Supports text search, namespace filtering, content type filtering, and pagination. Requires memory:read permission. |
| `kemory_rehydrate_session_sources` | Expand selected rolling-digest source IDs back to exact raw L1 memories or chat turns. This is read-only and token-budgeted: whole source items are included or omitted with a reason, never sliced, stop-word stripped, entity-coded, or returned as AAAK. Use this after kemory_get_session_context returns expansion hooks or when a query needs full-fidelity detail. |
| `kemory_whoami` | Return the calling identity as Kemory sees it: user id, agent registry entry (when agent-authenticated), and organisation scope. Use to verify which tenant and agent a session is bound to before writing. |

### Write — `destructiveHint: false`

| Tool | What it does |
|---|---|
| `kemory_capture_session` | Extract durable memories from a conversation window in one call — the server pulls out stable facts, preferences and decisions, dedupes them, and stores each through the normal write path (enrichment, provenance, &lt;private&gt; redaction). Call at the end of a significant turn with the recent window; re-sending overlapping windows is safe (dedup absorbs it). Transient state, secret-shaped content, and unknown namespace destinations are skipped and counted; shared is used as a bootstrap only for an empty vault. For a single narrative summary of the session, use kemory_consolidate_session instead. Requires memory:write permission. |
| `kemory_consolidate_session` | Trigger consolidation on a session — runs the Reflector agent over its episodic memories and produces ONE semantic summary stored as a new memory. Idempotent. For extracting many discrete durable facts from a conversation window, use kemory_capture_session instead; the two compose. |
| `kemory_memory` | Save one memory. Friendly alias of kemory_store_memory: same storage path and dedup/enrichment. Pass namespace/project explicitly. If omitted in a non-empty vault, this call returns existing destinations and an advisory suggestion without writing; retry with your choice. Only a brand-new vault falls back to 'shared'. Reserve shared for durable cross-project profile/preferences; use project namespaces for project facts, plans, decisions, and releases. Requires memory:write permission. |
| `kemory_promote_memory` | Promote a transient chunk (E09 multi-modal pipeline) so the CogOS retire pass leaves it alive. Use BEFORE referencing a transient memory from a skill or memory that won't carry a cited_memory_id, or as an explicit pin when you know an artifact is load-bearing. Idempotent — promoting an already-promoted memory is a no-op. |
| `kemory_rate_memory` | Report whether a memory returned by kemory_recall_memory (or another read tool) was actually useful, so kemory's own recall metrics reflect usage rather than just fetch counts (S9N-7207 Phase B). Not idempotent — each call inserts a new append-only rating row, so re-rating the same memory records a separate event rather than overwriting the last one. |
| `kemory_store_memory` | Store a new memory in the user's S9N Memory Vault. The memory needs an explicit destination — a namespace, or a project (from kemory_list_projects) routed to that project's primary namespace — and can include metadata, content type, and an optional TTL. Use 'shared' only for durable cross-project profile/preferences; file project facts, plans, decisions, and releases in their project namespace. Call kemory_list_namespaces or kemory_list_projects when the destination is unknown. Requires memory:write permission. |
| `kemory_store_skill` | Store a learned skill (procedural memory) with name, trigger, and ordered steps. Requires memory:write permission. |

### Destructive — `destructiveHint: true`

| Tool | What it does |
|---|---|
| `kemory_delete_memory` | Soft-delete a memory from the user's S9N Memory Vault by its ID. Requires memory:delete permission. |
| `kemory_forget` | Forget (soft-delete) one memory by its ID. Friendly alias of kemory_delete_memory — same soft-delete path, recoverable by an administrator. Requires memory:delete permission. |
| `kemory_resolve_conflict` | Resolve a contradiction between two memories: the loser is soft-superseded (bi-temporal invalid_at + superseded_by marker, same mechanics as the automatic contradiction judge), a conflict_resolved provenance event is recorded, and a 'supersedes' relation edge is written. Idempotent — resolving an already-resolved pair changes nothing. Requires memory:delete permission. |

<!-- TOOLS:END -->

**On annotations.** MCP clients read these hints when deciding what to auto-approve and what
to confirm with you. They are hints: the MCP specification says a client must treat
annotations from an untrusted server as untrusted. They are not Kemory's access control.
Permissions are enforced server-side on every call, whatever a client decides to do with the
hint.

---

## Authentication

Two paths, one authorisation model.

**OAuth 2.1 with PKCE — web AIs.** Authorisation is handled by SeKondBrain's identity
service. Clients register dynamically, so there is nothing to configure. You are redirected
to sign in, you approve, and the client receives a short-lived access token and a refresh
token. Kemory never sees your password. No long-lived credential exists anywhere on this
path.

**API keys — local clients.** A key is minted from an authenticated dashboard session,
displayed once, and stored hashed. It carries your organisation and identity. Present it as
`X-API-Key`. Revoke it from the dashboard when the machine or agent is retired.

Whichever path issued it, a credential resolves to the same authorisation context — a user,
an organisation, and an agent identity — and every tool call is checked against it before it
runs.

**Revoking access.** Dashboard → Connectors lists every agent connected to your account,
with the client it came from and when it last called. Revoke one and its next request
returns `401`.

---

## Scoping, namespaces and sharing

This is the part worth reading twice, because it determines what other people can see.

**Organisation isolation is structural.** Every query against tenant-scoped data carries an
organisation filter applied beneath the API layer, not by the calling code. A request cannot
read across organisations, and no tool, transport or client setting changes that.

**Within an organisation, you are the default boundary.** Memories you write are yours.
Colleagues in the same organisation do not see them by default, and neither do their agents.

**Namespaces are how you organise memory, and they are free-form.** A namespace is a label
you choose. Conventions that work well:

| Namespace | For |
|---|---|
| `user:preferences` | How you like to work — style, tools, formats |
| `project:<name>` | Facts and decisions about one project |
| `decisions:<period>` | A decision log with reasoning, in dated buckets |
| `tribal:<area>` | Operational knowledge that is nobody's and everybody's |

**Sharing is explicit.** A memory becomes visible beyond you when it is written to, or
promoted into, a namespace that your team can read. Nothing is promoted automatically.
`kemory_promote_memory` is the tool that does it, and it is a write, so a client that asks
before writing will ask before sharing.

If you are unsure whether something would be visible to a colleague, `kemory_check_access`
answers the question without changing anything.

**What agents can see.** An agent sees exactly what the person who connected it can see —
no more. Two agents connected by the same person share that person's memory. Two agents
connected by different people do not.

---

## Benchmarks

Kemory scores **89.6%** — 448 of 500 — on the LongMemEval-S oracle benchmark, run against the live production deployment. That is
*end-to-end answer accuracy*: retrieve, generate, then judge the answer against the reference.
It is not a retrieval-recall figure, which is the number most memory systems publish and is
not the same thing.

The method, the per-category breakdown, the run-to-run variance and the four caveats that matter
when comparing it are all set out in full — along with how to reproduce it.

**Full method and results:** https://docs.sekondbrain.ai/kemory/benchmarks/

---

## Capture with Kora's Chrome extension

Kemory is the memory; **Kora** is one way to fill it. Kora is SeKondBrain's Chief of Staff
AI, and her Chrome extension captures your conversations with ChatGPT, Claude, Gemini,
Perplexity and Manus as you have them, keeps them in your browser, and syncs them into
Kemory — so a chat you had in one AI becomes a memory any connected AI can recall.

It keeps what the host platforms eventually drop: full message text and structured blocks —
code, tables, reasoning, citations, artifacts — uploaded and generated files, inline images,
and conversation metadata. It groups related chats across tools by topic, so your *React
hooks* thread in ChatGPT and your *React state* thread in Claude land in the same place.

**Local first.** Conversations are captured into browser storage first, and sync only to the
Kemory you connect — your SeKondBrain account's, or a self-hosted instance you point it at.
They go nowhere else.

**Connecting is the sign-in.** Choose your environment and **Sign in with SeKondBrain**. That
single sign-in also connects Kemory: a per-install key is issued for you in the background and
the connection indicator turns green on its own — there is no separate key to paste. An
Advanced mode still accepts a pair code, a pasted key, or a custom URL for manual and
self-hosted setups.

**What reaches Kemory.** Captured chats become memories in your account, routed into
namespaces automatically — a chat with no routing signal lands in an inbox namespace and is
sorted from there. Once in Kemory they behave like any other memory: `kemory_recall_memory`
and the rest return them, scoped to you, from any AI you have connected.

**What the extension reads.** The extension reads page content only on the AI sites you switch it on
for, and only to capture your own conversations. What it stores and syncs is covered by the
same privacy policy as the rest of Kemory.

---

## Your data

Kemory stores memory content, the namespaces and metadata you attach to it, and the vector
embeddings computed from it. Where you connect a capture surface, it stores the conversation
content that surface sends. Account identity comes from SeKondBrain sign-in.

Memory content is processed by third-party language models for enrichment, compression and
embedding. Which providers, what is retained, how long, and how to have material erased are
set out in full in the privacy policy.

**Privacy policy:** https://docs.sekondbrain.ai/legal/privacy/

`kemory_delete_memory` is a soft delete: the memory stops being returned by any read tool.
The privacy policy describes what the audit trail retains afterwards and how to request
complete erasure.

**Credentials are your call.** Kemory does not stop you storing a password or an API key. An
explicit write is stored as you sent it, and no tool refuses one. Two facts should inform that
choice rather than a rule: content is encrypted at rest only if you have turned encryption on,
which is opt-in and permanent per account; and memory content is processed by third-party
language models for enrichment, compression and embedding, so a stored secret reaches those
providers like any other memory.

What Kemory will not do is make the decision for you. Automatic capture —
`kemory_capture_session` and the Kora sync behind it — drops credential-shaped text instead of
persisting it, even though that text was already in the conversation you had. The asymmetry is
deliberate: you can store a secret on purpose, but nothing will store one on your behalf.

---

## Errors and limits

Tool failures come back inside a successful JSON-RPC response with `isError: true` and a
typed message, rather than as an HTTP error — an AI can read the message and adjust.

| You see | It means |
|---|---|
| `Permission denied` | The credential is valid; that action on that namespace is not allowed. |
| `Validation error` | Arguments did not match the tool's schema. |
| `401` with a `WWW-Authenticate` header | No credential, or it expired or was revoked. Web clients re-authenticate automatically; local clients need a new key. |
| `-32601 Method not found` | An MCP method Kemory does not implement. `resources/*` returns an empty list by design. |
| `429` | Rate limited. Back off and retry. |

Calls using the old `s9nmem_*` tool names return `Unknown tool` — the prefix was
retired in August 2026 and no longer resolves. Something is still naming the old
tools, and it is usually a standing instruction or rules file written before the
rename rather than the connection itself. Change those names to `kemory_*`;
reconnecting on its own will not fix it.

---

## Support

- **Support:** support@sekondbrain.ai
- **Privacy policy:** https://docs.sekondbrain.ai/legal/privacy/

Kemory is built by SeKondBrain AI Labs. We own and operate the API, the domain and the
infrastructure this connector reaches.
