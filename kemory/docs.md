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

You need a SeKondBrain account. Create one, and reach every setting named on this page, at
**[kemory.sekondbrain.ai](https://kemory.sekondbrain.ai)** — that is the dashboard. Sign-in is handled by SeKondBrain's
identity service; Kemory never sees or holds a password.

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

Claude Code can connect two ways. The **plugin** is the recommended path: it carries hooks
that make memory get used rather than merely be available. Connecting the server on its own
works too, and gives you the same tools, prompts and resources with none of the hooks — see
[Server only](#server-only) below.

**1. Install it**, in a Claude Code terminal:

```
/plugin marketplace add SeKondBrainAILabs/kemory-plugin
/plugin install kemory@kemory
/reload-plugins
```

`/reload-plugins` is not optional — until it runs, the plugin's commands do not exist yet.
Nothing is downloaded beyond the plugin itself: its bundled MCP entry launches a script
inside the plugin, so there is no binary to install and nothing to put on `PATH`.

**2. Sign in.**

```
/kemory:login
```

It prints one link. Open it, approve in the browser, and the credential is written for you —
nothing to install, nothing to paste. It writes the same file the [CLI](cli/) does, so a CLI
installed later finds you already signed in. On a headless machine,
`export KEMORY_API_KEY="kemory_..."` instead.

**3. Restart Claude Code fully** — quitting the window is not enough — then confirm:

```
/kemory:status
```

Two checks have to pass: credentials resolve, and the API accepts them. The same output
prints which server will serve the tools and how capture and context injection are
configured. `/mcp` then shows which Kemory server Claude Code is actually talking to.
Context injection begins with your *next* session, because the hook that performs it runs
at session start.

### What the plugin adds

Connected is not the same as remembering. Tools sit unused unless something prompts the model
to reach for them; that prompting is the whole of what the plugin contributes. It loads your
context at session start, recalls under every prompt, and captures the session as it goes.
Six hooks, none of which need remembering — five on by default, and the store nudge ships
off:

| Hook | When | What it does |
|---|---|---|
| context injection | Session start | Injects your namespace summaries, so the session begins informed rather than blind |
| prompt recall | Every prompt you send | Searches your vault with what you just typed and injects what matches. `KEMORY_PROMPT_RECALL=0` turns it off |
| rate reminder | After a recall returns something rateable | Reminds the agent to rate what it used, so retrieval keeps improving. Local only, no network call |
| consolidate reminder | After compaction | Prompts the agent to store facts that would otherwise survive only as a summary |
| store nudge | End of a turn | **Opt-in, off by default.** When the turn settled something durable and nothing was written, asks for it before the turn ends |
| session capture | End of each turn, before `/compact`, session end | **On by default.** Stores a bounded, redacted digest of your own turns — never file contents or tool output. `KEMORY_AUTO_CAPTURE=0` turns it off |

It also ships `/kemory:login`, `/kemory:status`, and a skill covering how to recall, rate,
store and phrase memories so semantic search can find them again. That skill is the standing
instruction from [Optimise your AIs](optimise/), already written and kept current — with the
plugin installed you do not need to paste it into `CLAUDE.md` yourself. The server's
[prompts](#prompts-resources-and-cards) arrive with the plugin too, under plugin-namespaced
names: `/mcp__plugin_kemory_kemory__enhance` and `/mcp__plugin_kemory_kemory__save-session`.

Auto-approval of read-only Kemory tools, a status line and an in-app panel live in a separate,
optional add-on, `kemory-panel` (`/plugin install kemory-panel@kemory`). Without it, read-only
Kemory tools ask for permission like any other tool.

Every environment variable, what each hook sends, the surfaces that do and do not have
plugins, and what to do when nothing seems to happen: **[the plugin documentation](plugin/)**.
Source: [SeKondBrainAILabs/kemory-plugin](https://github.com/SeKondBrainAILabs/kemory-plugin).

### Run one server, not two

There are three ways to give Claude Code the Kemory tools, and they stack silently. Two
servers means two copies of every tool in every request — wasted context, and no way to
tell which lane a result came from. Pick one:

| Route | What connects | Use when |
|---|---|---|
| The plugin's bundled entry | A launcher that resolves the same credential the hooks use | Default. Installed with the plugin, nothing to configure beyond signing in |
| `claude mcp add`, `kemory connect` or `kemory mcp install --host claude-code` | An entry in `~/.claude.json` | You want the server without the plugin |
| *Kemory by SeKondBrain* in claude.ai connector settings | OAuth, account-wide | You want the same tools in the web and desktop apps too |

You do not have to police this yourself: the bundled entry stands down when this machine
already has a server for the same Kemory, and says so rather than starting and exposing
nothing. The hooks are unaffected either way — they call the API directly. The one case it
cannot detect is a claude.ai connector, which lives inside Claude and is invisible from a
shell; disable the bundled entry under `/mcp` if you use it.

### What leaves your machine

Two hooks transmit anything, and both are on by default. **Prompt recall** sends the
redacted text of each prompt to your Kemory instance as a search query — it skips prompts
under 12 characters and anything starting with `/`, `!` or `#`, so slash commands are never
sent. **Session capture** sends a bounded, redacted digest of your own turns, never file
contents or tool output, and stores it as a private memory; `KEMORY_AUTO_CAPTURE=0` turns it
off. Context injection sends only your credential, and the rating and store-nudge hooks make
no network calls at all. The full per-hook policy, with the redaction rules and the local
files the plugin keeps, is in [the plugin documentation](plugin/#privacy).

### If nothing seems to happen

The hooks fail open by design: with no credentials or no Kemory server they print one short
warning and carry on rather than erroring or blocking the session, so a broken setup can look
like an idle one. The setup notice then stays silent for 24 hours rather than nagging.

Run `/kemory:status` — it names which check failed. `Unknown command: /kemory:login` means
the plugin is installed but not loaded yet; run `/reload-plugins`. No credential means
nothing was exported into the environment Claude Code started from and no browser login is
stored. A rejected one means it expired or was revoked. Tools present but no context at
session start is the config-file case — a key inside an MCP config file authenticates the
tools, and the hooks never read MCP config.
[The full troubleshooting table](plugin/#trouble) covers the rest.

### Server only

To connect the server without the plugin:

```
claude mcp add --transport http kemory https://api.kemory.s9n.ai/mcp/v1
```

Then run `/mcp`, choose **kemory → Authenticate**, and sign in in the browser. You get the
tools, the prompts as `/mcp__kemory__enhance` and `/mcp__kemory__save-session`, and the
resources under `@kemory:` — but none of the hooks, so nothing is recalled or captured unless
the model decides to call a tool. Do not add this alongside the plugin; see
[Run one server, not two](#run-one-server-not-two).

---

## Connect a local client

For Claude Desktop, Cursor, Cline, Windsurf, Warp, Codex, Gemini CLI and any other client
that reads MCP servers from a config file. Claude Code has a plugin instead — see
[Connect Claude Code](#connect-claude-code).

These clients authenticate with an API key sent as an `X-API-Key` header. Create one from
**[Dashboard](https://kemory.sekondbrain.ai) → Keys**. It is shown once.

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
instructions or `CLAUDE.md` and it becomes the first thing checked instead. The
[Kemory plugin](plugin/) ships this as a skill, so plugin users can skip it:

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

## Use Kemory from the Claude API

The Claude API's MCP connector can call Kemory's tools from a Messages API request, with no
MCP client of your own. Pass a Kemory API key as the server's `authorization_token`:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: mcp-client-2026-09-15" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "What did we decide about the release process?"}],
    "mcp_servers": [{
      "type": "url",
      "url": "https://api.kemory.s9n.ai/mcp/v1",
      "name": "kemory",
      "authorization_token": "<KEMORY_API_KEY>"
    }],
    "tools": [{"type": "mcp_toolset", "mcp_server_name": "kemory"}]
  }'
```

The connector uses tools only, so the prompts, resources and cards described below do not
apply on this path. With this beta header a response can begin with an `mcp_tool_listing`
block; send the assistant message back unchanged on the next request. Keep the key on your
server, never in client-side code.

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
Kemory exposes **31 tools**, all prefixed `kemory_`. Every one carries a `title` and MCP
behaviour annotations, so your client can tell reading from writing from deleting before it
runs anything.

### Read-only — `readOnlyHint: true`

| Tool | What it does |
|---|---|
| `kemory_ask` | SURFACES: memories, chats, supported text files and namespace summaries where enabled. Check unsupported_types and retrieval_status for incomplete coverage. If a conversation might hold the answer, this is the tool. |
| `kemory_check_access` | Check if the current agent has permission to perform an action. Returns the Gatekeeper evaluation result without performing the action. |
| `kemory_find_similar` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three. |
| `kemory_get_compressed` | Tiered namespace compression. mode='aaak' returns the L2 lossless dialect encoding for byte-oriented storage/export diagnostics; do not inject AAAK into prompts as a token-saving context format. mode='concept' returns L3.1 LLM-synthesized concepts via core-ai-backend. merge_mode='current' picks the latest position in directional sequences; 'aggregate' synthesises all positions. mode='raw' is deprecated — use kemory_get_raw, which pages and reports has_more; raw calls here may serve one bounded page (check has_more/note in the result). Requires memory:read permission. |
| `kemory_get_context` | Get contextual memories relevant to a conversation or topic. Searches across all accessible namespaces (or a specific namespace) and returns the most relevant memories, optionally synthesised by the AI backend. Use it for background before reasoning about a topic; use kemory_recall to find specific records you will cite or edit, and kemory_get_user_context for a whole-vault overview at session start. Requires memory:read permission. |
| `kemory_get_history` | Return the full provenance history of a memory — every state change with actor, reason, and before/after snapshots. Requires memory:read permission. |
| `kemory_get_namespace_summary` | Get one namespace's consolidated cross-session summary: its human-readable description, the rolling L3.1 summary (falling back to the latest L3.0 concept memory when L3.1 has not been synthesised yet), the summary tier and when it was last updated, plus any related namespaces the matcher flagged as near-duplicates. Use this to orient on a single namespace before recalling from it. Requires memory:read permission on the namespace. |
| `kemory_get_profile` | Return the user's profile — 'static' (stable preferences) and 'dynamic' (recent activity) halves. Read-only: no write and no LLM call. A fresh stored profile is served from one lookup (source 'stored'); otherwise it is computed from the memories this caller can read and returned without being saved (source 'live'). Use section to fetch one half. Requires memory:read permission. |
| `kemory_get_raw` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three. |
| `kemory_get_session_context` | Get an optimized, prompt-ready context block for one namespace session. For a topic across namespaces use kemory_get_context; for a whole-vault overview use kemory_get_user_context. This keeps the latest raw user/assistant exchanges readable and folds older exchanges into a rolling token-budgeted digest. Namespace and session summaries are included as long-term background orientation; the digest itself is grounded only in prior digest + source exchanges. AAAK is never returned here because AAAK is byte-oriented storage/export compression, not the default LLM-context representation. Append the current user message after this tool output. |
| `kemory_get_user_context` | Get a cross-namespace memory overview for the user. Ideal for session-start context injection — gives the agent a single block covering all of the user's memory namespaces. For one topic use kemory_get_context; for specific records use kemory_recall. |
| `kemory_list_namespaces` | List all namespaces in the user's Kemory vault with memory counts and their tag tree (tag1, and the tag2s under it, written tag1:tag2). Use this before store_memory so a new write reuses an established tag instead of fragmenting the namespace. |
| `kemory_list_projects` | List the user's projects with their namespace mapping and memory counts. Explicit projects (created aliases spanning 1+ namespaces) merge with implicit ones (bare project:* namespaces). Pass a returned project name to kemory_memory / kemory_recall via their 'project' argument for project-scoped writes and reads. |
| `kemory_list_skills` | List all stored agent skills — learned procedures with name, trigger, and steps. Requires memory:read permission. |
| `kemory_plan_usage` | Report the caller's Kemory plan and how much of it has been used: memories stored against the plan's cap, connected AIs against the plan's cap, and Fair-Use position where the plan defines one. Read-only, takes no arguments. Use it to answer questions like 'how much room do I have left?' — and to mention headroom before a write is refused rather than after. A null limit means the plan has no cap on that axis; when the plan cannot be read every meter reports 'unavailable' and nothing is capped. Reads the same resolved snapshot the dashboard shows, so the two cannot disagree. |
| `kemory_recall` | SURFACES: memories only — chats and files are separate stores this tool never reads; kemory_ask searches all three. |
| `kemory_recall_memory` | Search and retrieve memories from the user's Kemory vault. Supports text search, namespace filtering, content type filtering, and pagination. kemory_recall returns identical results; either name works. Use this to find specific records you will cite, rate or edit; for background on a topic use kemory_get_context. Requires memory:read permission. |
| `kemory_rehydrate_session_sources` | Expand selected rolling-digest source IDs back to exact raw L1 memories or chat turns. This is read-only and token-budgeted: whole source items are included or omitted with a reason, never sliced, stop-word stripped, entity-coded, or returned as AAAK. Use this after kemory_get_session_context returns expansion hooks or when a query needs full-fidelity detail. |
| `kemory_whoami` | Return the calling identity as Kemory sees it: user id, agent registry entry (when agent-authenticated), and organisation scope. Use to verify which tenant and agent a session is bound to before writing. |

### Write — `destructiveHint: false`

| Tool | What it does |
|---|---|
| `kemory_consolidate_session` | Bring a session's summaries up to date now and return them. Kemory already summarises every session automatically as memories arrive (the per-session rollup) and compacts older exchanges into a rolling digest; this refreshes both on demand, for example before /compact or when a session ends, and returns the session summary for each namespace the session wrote to. It writes no memory and never changes or deletes the session's memories, which keep ageing through normal decay to the archive. Pair with kemory_capture_session, passing the same session_id to both. Requires memory:write permission. |
| `kemory_promote_memory` | Promote a transient chunk (E09 multi-modal pipeline) so the CogOS retire pass leaves it alive. Use BEFORE referencing a transient memory from a skill or memory that won't carry a cited_memory_id, or as an explicit pin when you know an artifact is load-bearing. Idempotent — promoting an already-promoted memory is a no-op. |
| `kemory_rate_memory` | Report whether an item returned by a read tool was actually useful, so kemory's own recall metrics reflect usage rather than just fetch counts. Works for anything search returns: pass the item's `id` as target_id and its `type` (memory, chat or file) as target_type — kemory_ask returns all three, and a chat id rated as a memory is rejected. Pass the recall response's retrieval.recall_id when you have it — it ties the rating to the exact recall event. Not idempotent — each call inserts a new append-only rating row, so re-rating the same item records a separate event rather than overwriting the last one; metrics read the latest per item. |
| `kemory_restore_version` | Put a memory's earlier wording back. When a save was absorbed as a near-duplicate, the memory was refreshed to the newer text and the earlier text kept as a revision (kemory_get_history lists them in displaced_revisions; a store response names it as dedup.previous_version_id). This restores that revision and keeps the current wording as a revision in its place, so nothing is lost and the returned previous_version_id undoes it. Use it only when the user says the merge was wrong. Requires memory:write permission. |

### Destructive — `destructiveHint: true`

| Tool | What it does |
|---|---|
| `kemory_capture_session` | Store several memories the user has already agreed to keep, in one call. Each item carries its content, an existing namespace and a content_type, and the call requires user_confirmed=true: the user has seen these exact items in this conversation and agreed to store them. It takes discrete items only, never conversation history or a transcript, and accepts at most 10 items of up to 2000 characters each. Each item goes through the normal write path (&lt;private&gt; redaction, enrichment, provenance). A near-duplicate of an existing memory in the same namespace and content type updates that memory in place with the new text; the earlier text is normally kept as a revision readable through kemory_get_history, but that copy is not guaranteed. Content under 20 characters, credential-shaped content and items whose namespace is not in the caller's inventory are skipped and counted; an empty vault accepts user:preferences and project:general. For one narrative summary of a session use kemory_consolidate_session. Requires memory:write permission. |
| `kemory_delete_memory` | Soft-delete a memory from the user's Kemory vault by its ID. Same action as kemory_forget. To mark a fact outdated by a newer one rather than remove it, use kemory_resolve_conflict. Requires memory:delete permission. |
| `kemory_forget` | Forget (soft-delete) one memory by its ID. Friendly alias of kemory_delete_memory — same soft-delete path, recoverable by an administrator. Requires memory:delete permission. |
| `kemory_memory` | Save one memory. Friendly alias of kemory_store_memory: same storage path and dedup/enrichment. Stores content the user has already agreed to keep. Usually a call adds a memory, but a near-duplicate in the same namespace and content type updates the existing memory in place with the new text, metadata and expiry. The earlier text is normally kept as a revision readable through kemory_get_history, but that copy is not guaranteed. Pass namespace/project explicitly. If omitted in a non-empty vault, this call returns existing destinations and an advisory suggestion without writing; retry with your choice. Only a brand-new vault files it itself: 'user:preferences' for content_type='preference', otherwise 'project:general'. Use user:preferences for how the user likes to work and project:&lt;topic&gt; (e.g. project:acme) for project facts, plans, decisions, and releases. Requires memory:write permission. |
| `kemory_reinstate_memory` | Bring back a memory that kemory_resolve_conflict superseded. By default both memories are then current (keep both). With supersede_winner=true the memory that had replaced it is superseded instead (keep the other one), in the same step. Only memories a conflict resolution superseded qualify: deleted memories and earlier versions are refused. Nothing is deleted either way. Use it only when the user says a resolution was wrong. Requires memory:write (and memory:delete with supersede_winner). |
| `kemory_resolve_conflict` | Resolve a contradiction between two memories: the loser is soft-superseded (bi-temporal invalid_at + superseded_by marker, same mechanics as the automatic contradiction judge), a conflict_resolved provenance event is recorded, and a 'supersedes' relation edge is written. Idempotent — resolving an already-resolved pair changes nothing. Requires memory:delete permission. |
| `kemory_store_memory` | Store a new memory in the user's Kemory vault. Stores content the user has already agreed to keep. The memory needs an explicit destination — a namespace, or a project (from kemory_list_projects) routed to that project's primary namespace — and can include metadata, content type, and an optional TTL. Use 'user:preferences' for how the user likes to work; file project facts, plans, decisions, and releases in their project namespace (e.g. 'project:acme'). Call kemory_list_namespaces or kemory_list_projects when the destination is unknown. kemory_memory is the same write with a friendlier name; to store several user-confirmed items in one call, use kemory_capture_session. Requires memory:write permission. |
| `kemory_store_skill` | Store a learned skill (procedural memory) with name, trigger, and ordered steps, in the caller's authenticated Kemory vault. The skill is private to the user, kept only in that vault and never sent to a third-party destination. A near-duplicate of an existing skill is updated in place with the new steps; the earlier version is normally kept as a revision readable through kemory_get_history, but that copy is not guaranteed. Requires memory:write permission. |

<!-- TOOLS:END -->

**On annotations.** MCP clients read these hints when deciding what to auto-approve and what
to confirm with you. They are hints: the MCP specification says a client must treat
annotations from an untrusted server as untrusted. They are not Kemory's access control.
Permissions are enforced server-side on every call, whatever a client decides to do with the
hint.

### Saving a session: capture, then refresh the summary

Two write tools work as a pair.

**`kemory_capture_session`** stores discrete items the user has confirmed — at most 10 per
call, each with its content, an existing namespace and a `content_type`, and the call
requires `user_confirmed: true`. It does not take a conversation window or a transcript: the
model picks the items, shows them to you, and sends only those. An optional `session_id` tags
every item so it counts towards that session's summary.

**`kemory_consolidate_session`** brings a session's summary up to date and returns it. Kemory
already keeps a summary of every session automatically: it is rebuilt as memories carrying the
session id arrive, and older exchanges are folded into a rolling digest. Consolidate refreshes
both on demand (before `/compact`, say) and returns the summary for each namespace the session
wrote to. It stores no new memory and never changes or deletes the session's memories; they age
through normal decay into the archive, where search can still find them. Run it twice and the
second call reports `already_current`.

Ask and Enhance use these session summaries: when a result comes from a session, its summary
is added to the background the answer is grounded in.

The `save-session` prompt below runs both in order.

### When a save updates a memory you already had

If you save something very close to a memory you already have, Kemory updates that memory
instead of keeping two near-copies, and the save reports it. The earlier wording is not
thrown away: it is kept in the memory's history, and `kemory_get_history` returns it under
`displaced_revisions`.

**`kemory_restore_version`** puts that earlier wording back. It takes the memory id and the
revision id (the save names it as `dedup.previous_version_id`). The wording it replaces is
kept in history in the same step, so nothing is lost, and the response's
`previous_version_id` undoes the restore. Use it when the two were meant to stay
different. It needs write access to the memory.

---

## Prompts, resources and cards

Tools are not the whole surface. Kemory also offers MCP prompts, which hosts surface as slash
commands, and resource templates, which hosts surface as @-mentions. These are rolling out
server by server; a server that does not offer them yet simply shows none.

### Prompts

| Prompt | Arguments | What it does |
|---|---|---|
| `enhance` | `request` (required), `project` (optional) | Returns your request with the stored memories that bear on it appended, each cited by memory id, capped at about 1,500 tokens. If nothing relevant is stored, the request comes back unchanged with a one-line note. Retrieval only — no model writes or invents context |
| `save-session` | `project` (optional) | Run it before `/compact` or when you stop work. Claude lists the session's decisions, open questions, next steps and durable facts — at most 10 items — stores them with `kemory_capture_session`, then calls `kemory_consolidate_session` so the session's summary includes them |
| `cards` | `mode` (`open`, `collapsed` or `off`; optional), `app` (`this` or `all`; optional) | Sets how Kemory's cards show up, through `kemory_settings`: for the AI app you are in, or for every app. With no mode it tells you the current setting |

In Claude Code: `/mcp__kemory__enhance <request>`, `/mcp__kemory__save-session` and
`/mcp__kemory__cards off`. With the
[plugin](#connect-claude-code) the server is plugin-namespaced, so the names are
`/mcp__plugin_kemory_kemory__enhance` and `/mcp__plugin_kemory_kemory__save-session`.

### Resources

| Resource | What it reads |
|---|---|
| `kemory://memory/{id}` | One memory, by the id recall returns |
| `kemory://project/{name}` | A project's namespaces and their stored summaries. Project names auto-complete |

A signed-in resource list also shows each of your projects individually. A memory or project
you cannot see reads exactly like one that does not exist, so a resource never confirms that
something is there. In Claude Code, type `@kemory:` and pick.

### Cards in chat

Cards are rolling out behind a feature flag. Hosts that support MCP Apps — Claude on the web
and desktop, ChatGPT, VS Code — render recall results and "memory saved" confirmations as
interactive cards instead of plain text.

Cards stay out of the way of the conversation:

- **One line until you open it.** Every card starts as a single line, such as "Used 5
  memories · from Claude, ChatGPT" or "Saved · project:kemory" with **Undo**. Open it to see
  the detail; lists (memories, sources, the two sides of a conflict) page one at a time as a
  carousel.
- **No more than two per turn.** A third card in the same turn takes no space; its result
  still reaches the assistant as text. The saved card, which carries Undo, always shows.
- **Nothing to show, no card.** A recall that found nothing shows no card. Each result says
  **Why this:** — how strong the match is, which AI's chat it came from, and how many passages
  agree.
- **First card, a short welcome.** The first card you ever get, in any AI, opens with a
  five-slide introduction to Kemory, the Chrome extension and the web app, and ends with a
  choice of how cards should show up.

**Choose how cards show up:** open, collapsed to one line (the default) or hidden, for every AI
or for one app — for example open in claude.ai and hidden in Claude Code. Set it in Kemory's
**Settings → Kemory cards in your AI chats**, with the `cards` prompt above, or by asking your AI
("turn off Kemory cards"), which calls `kemory_settings`. A change applies from the next card;
reconnect Kemory or refresh its tools if an empty space still shows where a hidden card was.

- **Recall card.** Results grouped by conversation: each chat's title, Kemory, AI and date
  once, the best passage first and the rest a click away, with the best overall marked
  **Best match**. Thumbs up or down tells Kemory whether a result helped; thumbs down asks
  why (not relevant, out of date, duplicate). **Open chat** and **Open in Kemory** open the
  item inside its own Kemory, and the Kemory label opens the Kemory itself. **Forget** sits
  behind the ⋯ menu, needs a second click, and is not offered on memories shared with you.
- **Saved card.** Says plainly what happened: saved, updated a memory you already had,
  already in your Kemory, or not saved. A brand-new memory offers **Undo** (second click to
  confirm). An update shows the earlier and the new wording side by side, with
  **Restore previous**, which [`kemory_restore_version`](#restore) carries out and which can
  itself be undone.
- **Conflict card.** After `kemory_resolve_conflict`, what was kept and what was replaced,
  side by side. **Keep both** or **Keep the other one instead** undo the decision through
  `kemory_reinstate_memory`; each needs a second click, and nothing is deleted.
- **Answer card.** A `kemory_ask` answer with how well it is grounded in your Kemory, and the
  sources it used, each opening in its own Kemory.
- **Overview card.** For `kemory_list_projects`, `kemory_plan_usage` and
  `kemory_get_namespace_summary`: your Kemories at a glance (totals, recently active,
  largest), your plan usage, or one Kemory's summary.

Cards are self-contained and make no network requests of their own; their buttons act
through your host's ordinary tool calls, under the same connection and permissions. Hosts
without MCP Apps, Claude Code among them, show the same text results as before.

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

**Revoking access.** [Dashboard](https://kemory.sekondbrain.ai) → Connectors lists every agent connected to your
account,
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

What Kemory will not do is make the decision for you. Capture — `kemory_capture_session`,
the plugin's session capture and the Kora sync — drops or redacts credential-shaped text
instead of persisting it, even though that text was already in the conversation you had. The asymmetry is
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
| `-32601 Method not found` | An MCP method Kemory does not implement. |
| `-32002 Resource not found` | A `kemory://` resource that does not exist, or that you cannot see — the two read the same. |
| `429` | Rate limited. Back off and retry. |

Calls using the old `s9nmem_*` tool names return `Unknown tool` — the prefix was
retired in August 2026 and no longer resolves. Something is still naming the old
tools, and it is usually a standing instruction or rules file written before the
rename rather than the connection itself. Change those names to `kemory_*`;
reconnecting on its own will not fix it.

---

## Support

- **Dashboard:** https://kemory.sekondbrain.ai
- **Support:** support@sekondbrain.ai
- **Privacy policy:** https://docs.sekondbrain.ai/legal/privacy/

Kemory is built by SeKondBrain AI Labs. We own and operate the API, the domain and the
infrastructure this connector reaches.
