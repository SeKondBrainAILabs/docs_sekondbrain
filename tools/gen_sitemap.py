"""Generate sitemap.xml and robots.txt from the published HTML.

    python tools/gen_sitemap.py

A page is listed when its <link rel="canonical"> points at its own URL and it carries no
noindex, so an alias such as kemory/optimize/ (canonical kemory/optimise/, noindex) stays
out. <lastmod> is the date of the last commit that touched the page; pages.yml checks out
full history for it, and without history the element is left out rather than guessed.
Like llms.txt, both outputs are written at deploy time and gitignored. Standard library only.
"""
import os
import subprocess
from html.parser import HTMLParser
from xml.sax.saxutils import escape

SITE = "https://docs.sekondbrain.ai/"


class Head(HTMLParser):
    """The canonical URL and the noindex flag, whatever order the attributes are in."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical, self.noindex = None, False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = self.canonical or a.get("href")
        elif (tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot")
              and "noindex" in a.get("content", "").lower()):
            self.noindex = True


def pages():
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        if "index.html" in filenames:
            yield os.path.normpath(os.path.join(dirpath, "index.html"))


def own_url(path):
    d = os.path.dirname(path)
    return SITE if d in ("", ".") else f"{SITE}{d}/"


def lastmod(path):
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    try:
        if git("rev-parse", "--is-shallow-repository") == "true":
            return ""
        return git("log", "-1", "--format=%cs", "--", path)
    except (OSError, subprocess.CalledProcessError):
        return ""


def entries():
    for path in pages():
        head = Head()
        with open(path, encoding="utf-8") as f:
            head.feed(f.read())
        if not head.canonical:
            raise SystemExit(f"gen_sitemap: {path} has no <link rel=\"canonical\">")
        url = own_url(path)
        if head.canonical != url or head.noindex:
            continue
        yield url, lastmod(path)


def sitemap():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, mod in entries():
        mod = f"<lastmod>{mod}</lastmod>" if mod else ""
        lines.append(f"  <url><loc>{escape(url)}</loc>{mod}</url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"


def main():
    for path, body in {"sitemap.xml": sitemap(), "robots.txt": robots()}.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"wrote {path} ({len(body):,} bytes)")


if __name__ == "__main__":
    main()
