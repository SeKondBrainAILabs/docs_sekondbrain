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
https://kemory.sekondbrain.ai/mcp/v1
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

## Connect a local client

For Claude Code, Claude Desktop, Cursor, Cline, Windsurf, Warp, Codex, Gemini CLI and any
other client that reads MCP servers from a config file.

These clients authenticate with an API key sent as an `X-API-Key` header. Create one from
**Dashboard → Keys**. It is shown once.

The entry below is exactly what a local client needs. Read it before you connect anything —
this is the whole surface.

```json
{
  "mcpServers": {
    "kemory": {
      "type": "http",
      "url": "https://kemory.sekondbrain.ai/mcp/v1",
      "headers": {
        "X-API-Key": "kemory_REPLACE_WITH_YOUR_KEY"
      }
    }
  }
}
```

| Client | Config location |
|---|---|
| Claude Code | `~/.claude.json` |
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

Never write credentials, keys or passwords into memory.
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
Kemory exposes **17 tools**, all prefixed `kemory_`. Every one carries a `title` and MCP
behaviour annotations, so your client can tell reading from writing from deleting before it
runs anything.

### Read-only — `readOnlyHint: true`

| Tool | What it does |
|---|---|
| `kemory_check_access` | Asks whether an action on a namespace would be permitted, without performing it. |
| `kemory_find_similar` | Nearest-neighbour lookup by embedding. Finds memories that mean the same thing, not ones that share words. |
| `kemory_get_compressed` | The same material at three levels of compression: raw, key-fact, and concept synthesis. |
| `kemory_get_context` | Memories relevant to a topic, returned as a synthesis rather than a list. |
| `kemory_get_history` | Version history and provenance for one memory — what changed, when, and which agent changed it. |
| `kemory_get_raw` | Unsynthesised contents of one namespace. Use when you want the source text, not a summary. |
| `kemory_get_session_context` | What was read and written inside one session. |
| `kemory_get_user_context` | A cross-namespace picture of you. Used to prewarm a session before the first question. |
| `kemory_list_namespaces` | Every namespace you can reach. |
| `kemory_list_skills` | Registered agent skills available to you. |
| `kemory_recall_memory` | Hybrid search across your namespaces — vector similarity and full-text, fused and re-ranked. The default way to find something. |
| `kemory_rehydrate_session_sources` | Re-reads the source material behind a session's memories, within a token budget. Reads only, despite the name. |

### Write — `destructiveHint: false`

| Tool | What it does |
|---|---|
| `kemory_consolidate_session` | Turns a session into durable memories. Idempotent — running it twice changes nothing. |
| `kemory_promote_memory` | Raises a memory from a narrow namespace into a wider one. The original stays where it was. |
| `kemory_store_memory` | Writes one memory into a namespace, with metadata. Nothing existing is overwritten. |
| `kemory_store_skill` | Registers a reusable skill. |

### Destructive — `destructiveHint: true`

| Tool | What it does |
|---|---|
| `kemory_delete_memory` | Deletes a memory by id. It stops being returned by recall. The audit trail retains that a deletion happened, and by whom. |

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

## Capture with Kora for Chrome

Kemory is the memory; **Kora** is one way to fill it. Kora is a Chrome extension that
captures your conversations with ChatGPT, Claude, Gemini, Perplexity and Manus as you have
them, keeps them in your browser, and syncs them into Kemory — so a chat you had in one AI
becomes a memory any connected AI can recall.

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

**What Kora reads.** The extension reads page content only on the AI sites you switch it on
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

**Do not put credentials in memory.** Passwords, API keys and tokens have no business in a
memory layer, and every tool description says so to the model as well as to you.

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

Tools returning `s9nmem_*` migration errors mean a client is running an outdated
configuration. Reconnect it.

---

## Support

- **Support:** support@sekondbrain.ai
- **Privacy policy:** https://docs.sekondbrain.ai/legal/privacy/

Kemory is built by SeKondBrain AI Labs. We own and operate the API, the domain and the
infrastructure this connector reaches.
