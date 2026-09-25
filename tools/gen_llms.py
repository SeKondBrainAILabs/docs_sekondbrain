"""Generate the llms.txt files from the published HTML.

    python tools/gen_llms.py

Writes three files (https://llmstxt.org):

    llms.txt               site index — every product, the legal documents
    kemory/llms.txt        Kemory index — one linked line per page
    kemory/llms-full.txt   every Kemory page as Markdown, in one file

The HTML is the source. pages.yml runs this before every deploy and the outputs are
gitignored, so they cannot drift from the pages and there is nothing to hand-edit.
Titles and descriptions come from each page's <title> and <meta name="description">; the
full text comes from the page's hero and <main>. Standard library only, like preflight.py.
"""
import os
import re
from html.parser import HTMLParser
from urllib.parse import urljoin

SITE = "https://docs.sekondbrain.ai/"

# Order is reading order. A new page is listed here deliberately, not picked up by a glob.
KEMORY = [
    ("kemory/", "Docs"),
    ("kemory/optimise/", "Docs"),
    ("kemory/retrieval/", "Docs"),
    ("kemory/cli/", "Docs"),
    ("kemory/plugin/", "Docs"),
    ("kemory/api/", "Reference"),
    ("kemory/benchmarks/", "Reference"),
    ("kemory/community/", "Reference"),
]
PRODUCTS = ["cognition/", "reasoning/", "heve/", "redaction/", "kora-hai/"]
LEGAL = [
    "legal/privacy/", "legal/terms/", "legal/business-terms/", "legal/extension-privacy/",
    "legal/fair-usage/", "legal/refunds/", "legal/cookies/", "subprocessors/",
]

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "img", "input", "nav", "header", "footer", "svg", "button"}
SKIP_CLASSES = {"ct", "pill", "nav-btn", "shot"}
BLOCK = {"p", "div", "section", "ul", "ol", "li", "pre", "table", "h1", "h2", "h3", "h4",
         "h5", "h6", "blockquote", "dl", "dt", "dd", "main", "article", "label"}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.parent, self.children = tag, parent, []
        self.attrs = dict(attrs)
        self.classes = set((self.attrs.get("class") or "").split())


class Tree(HTMLParser):
    """A minimal DOM. The pages are known-balanced — preflight.py fails the build otherwise."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("#root", [], None)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def find(node, pred):
    for c in node.children:
        if isinstance(c, Node):
            if pred(c):
                return c
            hit = find(c, pred)
            if hit:
                return hit
    return None


def text(node):
    return "".join(c if isinstance(c, str) else text(c) for c in node.children)


class Markdown:
    def __init__(self, url, shift=0):
        self.url, self.shift = url, shift
        self.seen_pre = set()

    def inline(self, node):
        out = []
        for c in node.children:
            if isinstance(c, str):
                out.append(re.sub(r"\s+", " ", c))
                continue
            if c.tag in SKIP_TAGS or c.classes & SKIP_CLASSES:
                continue
            if c.tag == "br":
                out.append(" ")
            elif "k" in c.classes and c.tag == "span":  # label of a label/value list item
                out.append(f"**{self.inline(c).strip()}:** ")
            elif "flag" in c.classes:  # "no auth" / "deprecated" beside an API path
                out.append(f" *({self.inline(c).strip()})*")
            elif "ann" in c.classes:  # the raw MCP annotation beside a tool grade
                out.append(f" `{text(c).strip()}`")
            elif c.tag == "code":
                t = re.sub(r"\s+", " ", text(c)).strip()
                out.append(f"`{t}`" if t else "")
            elif c.tag in ("strong", "b"):
                t = self.inline(c).strip()
                out.append(f"**{t}**" if t else "")
            elif c.tag in ("em", "i"):
                t = self.inline(c).strip()
                out.append(f"*{t}*" if t else "")
            elif c.tag == "a":
                t = self.inline(c).strip()
                href = c.attrs.get("href")
                out.append(f"[{t}]({urljoin(self.url, href)})" if href and t else t)
            else:
                out.append(self.inline(c))
        return "".join(out)

    def blocks(self, node):
        out, run = [], []

        def flush():
            para = re.sub(r"\s+", " ", "".join(run)).strip()
            if para:
                out.append(para)
            run.clear()

        for c in node.children:
            if isinstance(c, str):
                run.append(c)
                continue
            if c.tag in SKIP_TAGS or c.classes & SKIP_CLASSES:
                continue
            if c.tag not in BLOCK:
                wrapper = Node("span", [], None)
                wrapper.children = [c]
                run.append(self.inline(wrapper))
                continue
            flush()
            out.extend(self.block(c))
        flush()
        return out

    def block(self, c):
        tag = c.tag
        if tag[0] == "h" and tag[1:].isdigit():
            level = min(int(tag[1]) + self.shift, 6)
            return ["#" * level + " " + self.inline(c).strip()]
        if tag == "label":  # tab labels on the optimise page name the AI the panel is for
            return ["#" * min(4 + self.shift, 6) + " " + self.inline(c).strip()]
        if tag == "pre":
            body = text(c).strip("\n")
            if len(body) > 200 and body in self.seen_pre:
                return ["*(Same text as the earlier block on this page.)*"]
            self.seen_pre.add(body)
            fence = "````" if "```" in body else "```"
            return [f"{fence}\n{body}\n{fence}"]
        if tag in ("ul", "ol"):
            items = [li for li in c.children if isinstance(li, Node) and li.tag == "li"]
            lines = []
            for i, li in enumerate(items, 1):
                marker = f"{i}." if tag == "ol" else "-"
                parts = self.blocks(li)
                first = parts[0] if parts else ""
                lines.append(f"{marker} {first}")
                for p in parts[1:]:
                    lines.append("   " + p.replace("\n", "\n   "))
            return ["\n".join(lines)] if lines else []
        if tag == "table":
            return self.table(c)
        if tag == "div" and "bar" in c.classes:  # one row of a benchmark bar chart
            label = find(c, lambda n: "lbl" in n.classes)
            num = find(c, lambda n: "num" in n.classes)
            return [f"- {text(label).strip()}: {text(num).strip()}"]
        if tag == "div" and "route" in c.classes:
            steps = [self.inline(b).strip() for b in c.children
                     if isinstance(b, Node) and b.tag == "b"]
            return ["Path: " + " › ".join(f"**{s}**" for s in steps)]
        if "note" in c.classes and tag == "div" or tag == "blockquote":
            inner = self.blocks(c)
            if inner and "lbl" in (find(c, lambda n: "lbl" in n.classes) or Node("x", [], None)).classes:
                inner[0] = f"**{inner[0]}**"
            return ["\n>\n".join("> " + p.replace("\n", "\n> ") for p in inner)] if inner else []
        return self.blocks(c)

    def table(self, t):
        rows = []
        for tr in iter_tag(t, "tr"):
            cells = [self.inline(td).strip().replace("|", "\\|")
                     for td in tr.children if isinstance(td, Node) and td.tag in ("td", "th")]
            if cells:
                rows.append(cells)
        if not rows:
            return []
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        has_head = find(t, lambda n: n.tag == "th") is not None
        head = rows.pop(0) if has_head else [""] * width
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in rows]
        return ["\n".join(lines)]


def iter_tag(node, tag):
    for c in node.children:
        if isinstance(c, Node):
            if c.tag == tag:
                yield c
            yield from iter_tag(c, tag)


def load(path):
    with open(os.path.join(path, "index.html"), encoding="utf-8") as f:
        tree = Tree()
        tree.feed(f.read())
    return tree.root


def meta(root):
    title = text(find(root, lambda n: n.tag == "title")).strip()
    title = re.split(r"\s+\|\s+", title)[0]
    desc = find(root, lambda n: n.tag == "meta" and n.attrs.get("name") == "description")
    return title, (desc.attrs.get("content", "").strip() if desc else "")


def page_markdown(path):
    root = load(path)
    url = SITE + path
    title, desc = meta(root)
    md = Markdown(url, shift=1)  # page title is H1, so the page's own H2s become H3s
    parts = [f"## {title}", f"Source: {url}"]
    hero = find(root, lambda n: n.tag == "div" and "hero" in n.classes)
    if hero:
        hero_body = Node("div", [], None)
        hero_body.children = [c for c in hero.children
                              if not (isinstance(c, Node) and c.tag == "h1")]
        addr = find(hero, lambda n: "addr" in n.classes)
        if addr:
            hero_body.children.remove(addr)
        parts += md.blocks(hero_body)
        if addr:
            label = find(addr, lambda n: "k" in n.classes)
            code = find(addr, lambda n: n.tag == "code")
            parts.append(f"**{text(label).strip()}:** `{text(code).strip()}`")
    main = find(root, lambda n: n.tag == "main")
    parts += md.blocks(main)
    return "\n\n".join(parts).replace(" ", " ")


def index_line(path):
    title, desc = meta(load(path))
    return f"- [{title}]({SITE}{path}): {desc}"


def kemory_index():
    title, desc = meta(load("kemory/"))
    lines = [
        "# Kemory",
        "",
        f"> {desc} Kemory is a remote MCP server (Streamable HTTP) with a REST API, a CLI "
        "and a Claude Code plugin, run by SeKondBrain.",
        "",
        "- MCP server address: `https://api.kemory.s9n.ai/mcp/v1` (OAuth sign-in, no key "
        "to copy for web AIs)",
        "- Dashboard and account: https://kemory.sekondbrain.ai",
        f"- Everything below in one file: {SITE}kemory/llms-full.txt",
    ]
    for group in dict.fromkeys(g for _, g in KEMORY):
        lines += ["", f"## {group}", ""]
        lines += [index_line(p) for p, g in KEMORY if g == group]
    lines += ["", "## Optional", ""]
    lines += [index_line(p) for p in LEGAL]
    return "\n".join(lines) + "\n"


def kemory_full():
    head = ("# Kemory — full documentation\n\n"
            f"> Every page of {SITE}kemory/ as Markdown, generated from the published HTML. "
            f"Index: {SITE}kemory/llms.txt")
    pages = [page_markdown(p) for p, _ in KEMORY]
    return head + "\n\n" + "\n\n---\n\n".join(pages) + "\n"


def site_index():
    _, desc = meta(load("."))
    lines = [
        "# SeKondBrain documentation",
        "",
        f"> {desc} Kemory, the memory layer for AI agents, has the most complete "
        "documentation and its own llms.txt.",
        "",
        "## Kemory",
        "",
        f"- [Kemory llms.txt]({SITE}kemory/llms.txt): index of every Kemory page",
        f"- [Kemory llms-full.txt]({SITE}kemory/llms-full.txt): every Kemory page in one "
        "Markdown file",
        index_line("kemory/"),
        "",
        "## Platform",
        "",
    ]
    lines += [index_line(p) for p in PRODUCTS]
    lines += ["", "## Legal", ""]
    lines += [index_line(p) for p in LEGAL]
    return "\n".join(lines) + "\n"


def main():
    outputs = {
        "llms.txt": site_index(),
        "kemory/llms.txt": kemory_index(),
        "kemory/llms-full.txt": kemory_full(),
    }
    for path, body in outputs.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"wrote {path} ({len(body):,} bytes)")


if __name__ == "__main__":
    main()
