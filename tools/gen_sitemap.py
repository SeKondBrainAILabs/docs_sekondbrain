"""Generate sitemap.xml and robots.txt from the published HTML.

    python tools/gen_sitemap.py

A page is listed when its <link rel="canonical"> points at its own URL and it carries no
noindex, so an alias such as kemory/optimize/ (canonical kemory/optimise/, noindex) stays
out. <lastmod> is the date of the last commit that touched the page; pages.yml checks out
full history for it, and without history the element is left out rather than guessed.
Like llms.txt, both outputs are written at deploy time and gitignored. Standard library only.
"""
import os
import re
import subprocess
from xml.sax.saxutils import escape

SITE = "https://docs.sekondbrain.ai/"
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)"')
NOINDEX = re.compile(r'<meta name="robots" content="[^"]*noindex', re.I)


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
        with open(path, encoding="utf-8") as f:
            html = f.read()
        m = CANONICAL.search(html)
        if not m:
            raise SystemExit(f"gen_sitemap: {path} has no <link rel=\"canonical\">")
        url = own_url(path)
        if m.group(1) != url or NOINDEX.search(html):
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
