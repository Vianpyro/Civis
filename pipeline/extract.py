"""Turn a cached document into plain text, then into candidate program points.

A "candidate" is a sentence that reads like a commitment. The heuristic is
deliberately loose: it feeds an LLM draft that a human reads before commit, so
recall matters and precision does not.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pypdf

from .fetch import CACHE, load_sources

SKIP_TAGS = {"script", "style", "head", "noscript", "svg"}

# A list item opens a new logical paragraph even mid-sentence: program PDFs are
# mostly bullet lists, and merging them across items fabricates sentences.
BULLET = re.compile(r"^([•▪●◦‣]|[-–]\s|\d+[.)]\s)\s*")

# Leading verbs and markers that open a commitment in French program prose.
COMMITMENT = re.compile(
    r"^(nous |je |il faut |cr[ée]|augment|r[ée]tabl|supprim|abrog|instaur|garant"
    r"|interdi|baiss|port(er|ons)|d[ée]velopp|renforc|g[ée]n[ée]ralis|invest"
    r"|r[ée]duir|r[ée]duis|doubl|tripl|lanc|mett|met |plafonn|exon[ée]r|indexe"
    r"|conditionn|nationalis|sortir|sortons|bloqu|revaloris|financ|construir"
    r"|recrut|ouvrir|fermer|expuls|r[ée]serv|donner|rend|assur)",
    re.IGNORECASE,
)


class _Text(HTMLParser):
    """Minimal HTML-to-text. ponytail: no BeautifulSoup — we need visible text,
    not a DOM. Swap it in if a source ever needs selector-based extraction."""

    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skipping += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skipping:
            self.skipping -= 1
        elif tag in ("p", "li", "div", "br", "h1", "h2", "h3", "h4"):
            self.chunks.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            self.chunks.append(data)


def normalise(text: str) -> str:
    """Collapse the whitespace and typography noise that breaks quote matching."""
    text = text.replace(" ", " ").replace(" ", " ").replace("’", "'")
    text = text.replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-").replace("ﬁ", "fi")
    text = text.replace("ﬂ", "fl").replace("œ", "oe").replace("Œ", "OE")
    return re.sub(r"[ \t]+", " ", text)


def document_text(path: Path) -> str:
    if path.suffix == ".pdf":
        reader = pypdf.PdfReader(str(path))
        raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        parser = _Text()
        parser.feed(path.read_bytes().decode("utf-8", errors="replace"))
        raw = "".join(parser.chunks)
    return normalise(raw)


def cached_text(election: str, source_id: str) -> str | None:
    for path in sorted((CACHE / election).glob(f"{source_id}.*")):
        return document_text(path)
    return None


def flatten(text: str) -> str:
    """One line per logical paragraph. PDF extraction hard-wraps mid-sentence, so
    a line that does not end in terminal punctuation continues into the next."""
    paragraphs: list[str] = []
    buffer = ""
    for line in text.splitlines():
        line = normalise(line).strip()
        starts_item = bool(BULLET.match(line))
        line = BULLET.sub("", line).strip()
        if not line or starts_item:
            if buffer:
                paragraphs.append(buffer.strip())
                buffer = ""
            if not line:
                continue
        buffer = f"{buffer} {line}".strip() if buffer else line
        if line.endswith((".", "!", "?", ":", ";")):
            paragraphs.append(buffer)
            buffer = ""
    if buffer:
        paragraphs.append(buffer.strip())
    return "\n".join(paragraphs)


def candidates(text: str, min_len: int = 40, max_len: int = 320) -> list[str]:
    """Sentences that look like policy commitments, deduplicated, in order."""
    out: list[str] = []
    seen: set[str] = set()
    for line in flatten(text).splitlines():
        for sentence in re.split(r"(?<=[.!?])\s+", line.strip(" -–")):
            sentence = sentence.strip()
            key = sentence.lower()
            if min_len <= len(sentence) <= max_len and COMMITMENT.match(sentence) and key not in seen:
                seen.add(key)
                out.append(sentence)
    return out


def haystack(text: str) -> str:
    """Whitespace-collapsed document text: what a quote is checked against.

    Line breaks in a PDF are a rendering artefact, so a quote that spans one is
    still verbatim. Collapsing whitespace on both sides is the honest comparison.
    """
    return re.sub(r"\s+", " ", normalise(text))


def main(election: str) -> int:
    for source in load_sources(election):
        text = cached_text(election, source["id"])
        if text is None:
            print(f"  missing  {source['id']} (run fetch first)")
            continue
        found = candidates(text)
        print(f"{len(found):>5} candidates  {source['id']}")
    return 0
