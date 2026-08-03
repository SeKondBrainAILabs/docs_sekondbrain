"""Sanity-check the static site before handover: tag balance and local link resolution."""
import os
import re
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
ROOT = "."
failures = []


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            failures.append(f"{self.path}: stray </{tag}>")
        elif self.stack[-1] != tag:
            failures.append(f"{self.path}: </{tag}> closes <{self.stack[-1]}>")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in {".git", ".github"}]
    for fn in filenames:
        if fn.endswith(".html"):
            pages.append(os.path.join(dirpath, fn))

for page in sorted(pages):
    html = open(page, encoding="utf-8").read()
    p = Balance()
    p.path = page
    p.feed(html)
    p.close()
    if p.stack:
        failures.append(f"{page}: unclosed {p.stack}")

    # local link / asset resolution
    for attr in re.findall(r'(?:href|src)="([^"]+)"', html):
        if attr.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        target = attr.split("#")[0].split("?")[0]
        if not target:
            continue
        base = ROOT if target.startswith("/") else os.path.dirname(page)
        resolved = os.path.normpath(os.path.join(base, target.lstrip("/")))
        if os.path.isdir(resolved):
            resolved = os.path.join(resolved, "index.html")
        if not os.path.exists(resolved):
            failures.append(f"{page}: link does not resolve -> {attr} ({resolved})")

    print(f"parsed {page} ({len(html):,} bytes)")

# the page that is the deliverable
kem = open("kemory/index.html", encoding="utf-8").read()
for needle, label in [
    ("TOOLS:BEGIN", "tool-table marker"),
    ("kemory_REPLACE_WITH_YOUR_KEY", "placeholder key, not a live credential"),
    ("legal/privacy/", "privacy policy link"),
    ('id="scoping"', "scoping section"),
]:
    if needle not in kem:
        failures.append(f"kemory/index.html: missing {label}")

tool_rows = len(re.findall(r"<code>kemory_[a-z_]+</code>", kem))
if tool_rows < 17:
    failures.append(f"kemory/index.html: only {tool_rows} tool rows, expected >= 17")
else:
    print(f"tool rows in table: {tool_rows}")

# the legal documents must all be present — they are linked from the index, the
# footers and the Chrome Web Store listing
for page, label in [
    ("legal/index.html", "legal index"),
    ("legal/privacy/index.html", "Privacy Policy"),
    ("legal/terms/index.html", "Terms of Service"),
    ("legal/business-terms/index.html", "Business Terms and DPA"),
    ("legal/extension-privacy/index.html", "extension privacy policy"),
]:
    if not os.path.exists(page):
        failures.append(f"{page}: missing — {label} is linked from published pages")

# internal drafting apparatus must never reach a published page. The source documents
# carry drafting notes and risk flags addressed to us, not to the reader.
INTERNAL = ["Internal drafting note", "RISK FLAG", "remove before signature", "ship gate",
            "Draft for review", "DIVERGENCE FROM SOURCE"]
for page in sorted(pages):
    body = open(page, encoding="utf-8").read()
    for needle in INTERNAL:
        if needle.lower() in body.lower():
            failures.append(f"{page}: internal drafting apparatus leaked -> {needle!r}")

# no live credential must ever be committed
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        try:
            body = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for hit in re.findall(r"kemory_[A-Za-z0-9]{16,}", body):
            if "REPLACE" not in hit:
                failures.append(f"{path}: possible live key {hit[:20]}...")

print()
if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    raise SystemExit(1)
print("ALL PRE-FLIGHT CHECKS PASSED")
