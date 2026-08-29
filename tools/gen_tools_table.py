#!/usr/bin/env python3
"""
Regenerate the Kemory tool table from a live `tools/list`.

The Connectors Directory Definition of Done requires published tool descriptions
to match what the server actually returns. Hand-maintaining the table guarantees
drift, so CI regenerates it and fails if the committed copy and the server
disagree.

Both the Markdown source and the published HTML carry the same markers:

    <!-- TOOLS:BEGIN -->  ...  <!-- TOOLS:END -->

Usage
-----
    # rewrite both files in place
    python tools/gen_tools_table.py --url "$KEMORY_MCP_URL" --api-key "$KEMORY_DOCS_KEY" \
        --write kemory/docs.md --write kemory/index.html

    # CI gate: exit 1 if either committed table is stale
    python tools/gen_tools_table.py --url "$KEMORY_MCP_URL" --api-key "$KEMORY_DOCS_KEY" \
        --check kemory/docs.md --check kemory/index.html

Format is inferred from the file extension. Beyond staleness, the script fails on
two conditions that would sink a directory submission on their own:

  * a tool with no `title`
  * a tool whose annotations do not classify it as read / write / destructive
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import urllib.error
import urllib.request

BEGIN = "<!-- TOOLS:BEGIN -->"
END = "<!-- TOOLS:END -->"

# (heading, annotation as displayed, css class, predicate on the annotations dict)
#
# The write predicate requires destructiveHint to be *explicitly* false. Treating an
# absent annotation as a safe write is the vacuous pass that lets a newly added,
# unannotated tool be published as harmless — the exact hole the server-side tests
# guard against. Undeclared behaviour fails the build instead.
GROUPS = (
    ("Read-only", "readOnlyHint: true", "read",
     lambda a: a.get("readOnlyHint") is True),
    ("Write", "destructiveHint: false", "write",
     lambda a: a.get("readOnlyHint") is not True and a.get("destructiveHint") is False),
    ("Destructive", "destructiveHint: true", "del",
     lambda a: a.get("readOnlyHint") is not True and a.get("destructiveHint") is True),
)


# --------------------------------------------------------------------------- fetch

def fetch_tools(url: str, api_key: str) -> list[dict]:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        sys.exit(f"tools/list failed: HTTP {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        sys.exit(f"tools/list unreachable: {exc.reason}")

    if "error" in payload:
        sys.exit(f"tools/list returned an error: {payload['error']}")
    tools = payload.get("result", {}).get("tools")
    if not tools:
        sys.exit("tools/list returned no tools")
    return tools


# --------------------------------------------------------------------------- shape

def clean(text: str) -> str:
    """Tool descriptions carry an appended tenant-scope hint aimed at the model.
    The docs want the human-facing sentence, not the guardrail."""
    head = (text or "").split("\n")[0].strip()
    for marker in (" Tenant scope:", " Tenant-scope:", " Note:", " Scope:"):
        head = head.split(marker)[0]
    return head.rstrip().replace("|", "\\|")


def classify(tools: list[dict]) -> list[tuple[str, str, str, list[dict]]]:
    undeclared = sorted(
        t["name"] for t in tools
        if not {"readOnlyHint", "destructiveHint"} & set((t.get("annotations") or {}))
    )
    if undeclared:
        sys.exit(
            "tools declaring neither readOnlyHint nor destructiveHint: "
            f"{undeclared}\nThe directory requires one of the two on every tool, and this "
            "script will not guess. Annotate them server-side."
        )

    out, seen = [], set()
    for heading, annotation, css, predicate in GROUPS:
        members = [t for t in sorted(tools, key=lambda t: t["name"])
                   if predicate(t.get("annotations") or {})]
        seen.update(t["name"] for t in members)
        if members:
            out.append((heading, annotation, css, members))

    unclassified = sorted({t["name"] for t in tools} - seen)
    if unclassified:
        sys.exit(f"tools with unusable annotations: {unclassified}")

    untitled = sorted(t["name"] for t in tools if not t.get("title"))
    if untitled:
        sys.exit(f"tools missing a title — the submission portal will reject these: {untitled}")

    return out


# --------------------------------------------------------------------------- render

INTRO = ("Kemory exposes **{n} tool{s}**, all prefixed `kemory_`. Every one carries a `title` "
         "and MCP\nbehaviour annotations, so your client can tell reading from writing from "
         "deleting before it\nruns anything.")


def render_md(tools: list[dict]) -> str:
    lines = [BEGIN, INTRO.format(n=len(tools), s="" if len(tools) == 1 else "s"), ""]
    for heading, annotation, _css, members in classify(tools):
        lines += [f"### {heading} — `{annotation}`", "", "| Tool | What it does |", "|---|---|"]
        # Literal angle brackets in a description ("<private> redaction") read
        # as an HTML tag to Markdown renderers and vanish — escape them.
        lines += [
            f"| `{t['name']}` | {clean(t.get('description')).replace('<', '&lt;').replace('>', '&gt;')} |"
            for t in members
        ]
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def render_html(tools: list[dict]) -> str:
    n = len(tools)
    lines = [
        BEGIN,
        f'      <p>Kemory exposes <strong>{n} tool{"" if n == 1 else "s"}</strong>, all prefixed <code>kemory_</code>. '
        'Every one carries a <code>title</code> and MCP behaviour annotations, so your client '
        'can tell reading from writing from deleting before it runs anything.</p>',
        "",
    ]
    for heading, annotation, css, members in classify(tools):
        count = f"{len(members)} tool" + ("s" if len(members) != 1 else "")
        lines += [
            f'      <div class="grade"><span class="dot {css}"></span><h3>{heading}</h3>'
            f'<span class="ann">{annotation}</span></div>',
            f'      <p class="count">{count}</p>',
            "      <table>",
            "        <tbody>",
        ]
        for t in members:
            # Live descriptions are plain text and may contain literal angle
            # brackets (kemory_capture_session says "<private> redaction") —
            # unescaped they read as tags and break the published page.
            desc = html.escape(clean(t.get("description")).replace("\\|", "|"), quote=False)
            lines.append(f'          <tr><td><code>{html.escape(t["name"])}</code></td><td>{desc}</td></tr>')
        lines += ["        </tbody>", "      </table>", ""]
    lines.append(END)
    return "\n".join(lines)


def splice(source: str, block: str, path: str) -> str:
    if BEGIN not in source or END not in source:
        sys.exit(f"{path}: markers {BEGIN} / {END} not found")
    return source.split(BEGIN)[0] + block + source.split(END, 1)[1]


# --------------------------------------------------------------------------- main

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Kemory MCP endpoint, e.g. https://.../mcp/v1")
    p.add_argument("--api-key", required=True)
    p.add_argument("--write", action="append", default=[], metavar="PATH")
    p.add_argument("--check", action="append", default=[], metavar="PATH")
    args = p.parse_args()

    if not (args.write or args.check):
        sys.exit("pass at least one --write or --check")

    tools = fetch_tools(args.url, args.api_key)
    stale = []

    for path in args.write + args.check:
        block = render_html(tools) if path.endswith((".html", ".htm")) else render_md(tools)
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        updated = splice(source, block, path)

        if path in args.check and updated != source:
            stale.append(path)
        elif path in args.write:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            print(f"wrote tool table into {path}")

    if stale:
        sys.exit(
            "Tool table is stale in: " + ", ".join(stale) +
            "\nThe published docs no longer match the live tools/list."
            "\nRerun with --write and commit the result."
        )

    if args.check:
        print(f"tool table matches the live server ({len(tools)} tools)")


if __name__ == "__main__":
    main()
