#!/usr/bin/env python3
"""Fail unless index.html has exactly one accessibility-statement link
and exactly one EqualWeb accessibility widget.

The link must point to the exact statement URL, carry the exact text
"הצהרת נגישות", and have no target attribute. The widget is the inline
`window.interdeal` config plus the loader that reads `interdeal.domains.js`
(served from cdn.equalweb.com); each marker must appear exactly once.
Run from the repo root.
"""
import sys
from html.parser import HTMLParser

URL = "https://aimprove.co.il/accessibility-statement/"
TEXT = "הצהרת נגישות"
WIDGET_MARKERS = ("window.interdeal", "cdn.equalweb.com", "interdeal.domains.js")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self._open = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._open = {"attrs": dict(attrs), "has_target": any(k == "target" for k, _ in attrs), "text": ""}

    def handle_data(self, data):
        if self._open is not None:
            self._open["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._open is not None:
            self.anchors.append(self._open)
            self._open = None


def main():
    with open("index.html", encoding="utf-8") as f:
        source = f.read()
    collector = Collector()
    collector.feed(source)
    matches = [a for a in collector.anchors if a["attrs"].get("href") == URL]
    problems = []
    if len(matches) != 1:
        problems.append("expected exactly 1 anchor with href %s, found %d" % (URL, len(matches)))
    for a in matches:
        if a["text"] != TEXT:
            problems.append("anchor text is %r, expected %r" % (a["text"], TEXT))
        if a["has_target"]:
            problems.append("anchor has a target attribute")
    for marker in WIDGET_MARKERS:
        found = source.count(marker)
        if found != 1:
            problems.append("expected exactly 1 occurrence of %r (EqualWeb widget), found %d" % (marker, found))
    if problems:
        for p in problems:
            print("check-a11y-link: FAIL - " + p)
        return 1
    print("check-a11y-link: OK (one statement link, one EqualWeb widget)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
