"""Content invariants, enforced in CI. `python -m pipeline.check`

The load-bearing one is quote verification: every quote in content/programs must
appear verbatim in the document its source declares. That is what makes the
neutrality claim checkable by a machine rather than asserted in a README.

It needs the fetched documents, so CI runs fetch before check. Offline, that one
check is skipped and reported as skipped — never silently passed.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

from . import llm, neutrality
from .extract import cached_text, haystack
from .fetch import ROOT, digest_file, load_sources

ELECTION = "fr-2027"
STANCES = {-1, 1}
THEMES = {
    "economy",
    "social",
    "ecology",
    "institutions",
    "security",
    "immigration",
    "europe",
    "education",
    "health",
}

# Closed vocabulary of affected groups (DP-32). The labels live in
# web/src/lib/ui.js and a Node test checks that both sides hold the same keys
# (DT-27) — the same arrangement as THEMES, which works.
GROUPS = {
    "associations",
    "businesses",
    "citizens",
    "departments",
    "employees",
    "farmers",
    "foreign_nationals",
    "healthcare",
    "judiciary",
    "law_enforcement",
    "local_authorities",
    "municipalities",
    "owners",
    "public_bodies",
    "regions",
    "retirees",
    "schools",
    "self_employed",
    "state_services",
    "students",
    "taxpayers",
    "tenants",
}

# Impact analyses: shape, bounds and canonical order (DP-31, DP-33, DT-25).
KINDS = ("implication", "affected", "effect")  # also the canonical order
BOUNDS = {"implication": (1, 4), "affected": (1, 5), "effect": (0, 4)}
TOTAL_BOUNDS = (3, 10)
MAX_STATEMENT = 200
MAX_SPAN = 300
BASES = {"text", "inferred"}
# `model` of an entry written by hand (§5.2). A provenance, not a model name.
MANUAL = "manual"
DIRECTNESS = {"direct", "indirect"}
TOP_KEYS = {"election", "impacts"}
ENTRY_KEYS = {"of", "model", "reviewed", "items"}
ITEM_KEYS = {"kind", "basis", "span", "who", "directness", "fr", "en"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.skipped: list[str] = []
        # Fail on what is wrong, warn on what is missing (DT-26). A partially
        # covered corpus is the normal state of work in progress, not an error.
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> bool:
        if not condition:
            self.errors.append(message)
        return condition


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_election(election: str, report: Report) -> None:
    sources = {s["id"]: s for s in load_sources(election)}

    for path in (ROOT / "content" / "sources" / election).glob("*.sha256"):
        report.require(
            path.stem in sources,
            f"orphan digest {path.name}: no matching entry in sources.json",
        )

    for source_id in sources:
        path = digest_file(election, source_id)
        if not report.require(path.exists(), f"missing digest: {path.name}"):
            continue
        line = path.read_text(encoding="utf-8").strip().split()
        report.require(
            len(line) == 2 and re.fullmatch(r"[0-9a-f]{64}", line[0]) is not None,
            f"malformed digest line in {path.name}",
        )
        report.require(
            line[-1] == sources[source_id]["url"],
            f"{path.name} points at a different URL than sources.json",
        )

    programs = [load(p) for p in sorted((ROOT / "content" / "programs" / election).glob("*.json"))]
    report.require(bool(programs), "no programs found")

    points: dict[str, dict] = {}
    for program in programs:
        party = program["party"]["id"]
        report.require(
            program["source_id"] in sources,
            f"{party}: unknown source_id {program['source_id']!r}",
        )
        for point in program["points"]:
            report.require(point["id"] not in points, f"duplicate point id {point['id']!r}")
            report.require(point["theme"] in THEMES, f"{point['id']}: unknown theme")
            points[point["id"]] = {**point, "party": party, "source_id": program["source_id"]}

    texts = document_texts(election, sources)
    check_quotes(points, texts, report)

    questions = load(ROOT / "content" / "questions" / f"{election}.json")
    positions = load(ROOT / "content" / "questions" / f"{election}.positions.json")
    check_questions(questions, positions, points, [p["party"] for p in programs], report)

    impacts_path = ROOT / "content" / "impacts" / f"{election}.json"
    if report.require(impacts_path.exists(), f"missing {impacts_path.name}: the file is part of the schema"):
        raw = impacts_path.read_text(encoding="utf-8")
        check_impacts(
            json.loads(raw), raw, election, points, positions, texts, [p["party"] for p in programs], report
        )


def document_texts(election: str, sources: dict) -> dict[str, str | None]:
    """Whitespace-collapsed text of each cached document, or None if absent."""
    texts: dict[str, str | None] = {}
    for source_id in sources:
        text = cached_text(election, source_id)
        texts[source_id] = haystack(text) if text is not None else None
    return texts


def check_quotes(points: dict, texts: dict, report: Report) -> None:
    """Every quote must be a verbatim substring of the document it cites."""
    for point_id, point in points.items():
        text = texts[point["source_id"]]
        if text is None:
            report.skipped.append(point_id)
            continue
        report.require(
            needle(point["quote"]) in text,
            f"{point_id}: quote not found verbatim in {point['source_id']}",
        )


def check_questions(
    questions: dict, positions: dict, points: dict, parties: list[dict], report: Report
) -> None:
    seen: set[str] = set()
    for question in questions["questions"]:
        report.require(question["id"] not in seen, f"duplicate question id {question['id']!r}")
        seen.add(question["id"])
        report.require(question["theme"] in THEMES, f"{question['id']}: unknown theme")
        for lang in ("fr", "en"):
            report.require(
                bool(question["text"].get(lang, "").strip()),
                f"{question['id']}: missing {lang} text",
            )

    # The blind invariant, checked structurally: the questionnaire bundle carries
    # no party identity at all, so it cannot leak one however the client renders.
    # ponytail: substring match on names, word match on ids. It false-positives on
    # a party short name that is also a common word ("Ensemble") — rephrase the
    # question; a stricter check beats a smarter one here.
    blind = json.dumps(questions, ensure_ascii=False).lower()
    words = set(re.findall(r"[a-zà-ÿ]+", blind))
    for party in parties:
        # Ids and short names are matched as whole words — "rn" is a substring of
        # "gouvernement". The full name is multi-word, so substring is safe there.
        for label in (party["id"], party["short"]):
            report.require(
                label.lower() not in words,
                f"party label {label!r} appears in the blind questions file",
            )
        report.require(
            party["name"].lower() not in blind,
            f"party name {party['name']!r} appears in the blind questions file",
        )

    mapped = set()
    for question_id, entries in positions.items():
        report.require(question_id in seen, f"positions: unknown question {question_id!r}")
        mapped.add(question_id)
        parties = set()
        for entry in entries:
            if report.require(
                entry["point"] in points, f"{question_id}: unknown point {entry['point']!r}"
            ):
                party = points[entry["point"]]["party"]
                report.require(
                    party not in parties, f"{question_id}: two positions for {party!r}"
                )
                parties.add(party)
            report.require(entry["stance"] in STANCES, f"{question_id}: stance must be -1 or 1")

    for question_id in seen - mapped:
        report.errors.append(f"{question_id}: no position maps to it")


def quote_digest(quote: str) -> str:
    """`of`: the fingerprint of the quote, never of the document (DT-23).

    A PDF re-exported without a text change gets a new document digest; keying
    on it would expire every analysis for nothing. Normalised the way a quote is
    normalised before it is looked for, so the same string yields the same digest
    on both sides. The generator computes this too, from here, never twice.
    """
    return hashlib.sha256(needle(quote).encode("utf-8")).hexdigest()


def needle(text: str) -> str:
    """What is looked for inside a haystack(): whitespace collapsed, nothing else."""
    return re.sub(r"\s+", " ", text).strip()


def canonical(data: dict) -> str:
    """The one accepted serialisation of the impacts file (DT-25).

    One line of comparison that removes any formatting divergence between a
    machine regeneration and a hand correction — which matters because human
    review is the load-bearing filter, and it degrades on unreadable diffs.
    """
    order = {kind: rank for rank, kind in enumerate(KINDS)}
    impacts = {
        point_id: {
            **entry,
            "items": sorted(
                entry["items"],
                # Stable, so the order inside a kind is the order of the file.
                # Anything malformed sorts last rather than raising: the entry
                # loop has already reported it, and a traceback would hide it.
                key=lambda item: order.get(item.get("kind") if isinstance(item, dict) else None, len(KINDS)),
            ),
        }
        if isinstance(entry, dict) and isinstance(entry.get("items"), list)
        else entry
        for point_id, entry in sorted(data.get("impacts", {}).items())
    }
    return json.dumps({**data, "impacts": impacts}, ensure_ascii=False, indent=2) + "\n"


def as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def check_impacts(
    data: dict,
    raw: str,
    election: str,
    points: dict,
    positions: dict,
    texts: dict,
    parties: list[dict],
    report: Report,
) -> None:
    """Structural rules of content/impacts/<election>.json — L-01 to L-10, L-18, L-19.

    The lexical rules (L-11 to L-17) live in pipeline/neutrality.py, which is
    called per statement from check_impact_item.
    """
    report.require(data.get("election") == election, f"impacts: election is not {election!r}")
    unknown = sorted(set(data) - TOP_KEYS)
    report.require(not unknown, f"impacts: unknown top-level key(s) {unknown} (L-01)")

    entries = data.get("impacts")
    if not report.require(isinstance(entries, dict), "impacts: `impacts` must be an object"):
        return

    for point_id, entry in entries.items():
        check_impact_entry(point_id, entry, points, texts, parties, report)

    report.require(canonical(data) == raw, "impacts: file is not in canonical form (L-19)")
    check_impact_coverage(entries, positions, points, report)


def check_impact_entry(
    point_id: str, entry: dict, points: dict, texts: dict, parties: list[dict], report: Report
) -> None:
    label = f"impacts[{point_id}]"
    if not report.require(isinstance(entry, dict), f"{label}: entry must be an object"):
        return

    unknown = sorted(set(entry) - ENTRY_KEYS)
    report.require(not unknown, f"{label}: unknown key(s) {unknown} (L-01)")

    point = points.get(point_id)
    if not report.require(point is not None, f"{label}: unknown point id (L-02)"):
        return

    of = as_text(entry.get("of"))
    report.require(
        re.fullmatch(r"[0-9a-f]{64}", of) is not None and of == quote_digest(point["quote"]),
        f"{label}: `of` is not the digest of the point's quote (L-03)",
    )
    model = as_text(entry.get("model")).strip()
    report.require(bool(model), f"{label}: missing `model`")
    # W-03. llm.MODEL is the current model of the pipeline (DT-31), and a drift
    # is a warning rather than a failure: an entry produced by another model is
    # still valid content, it is a batch to read again rather than to reject.
    # A hand-written entry is not a drift: it has no model to drift from, and it
    # is already what a flagged entry is re-read into (DT-33).
    if model and model not in (llm.MODEL, MANUAL):
        report.warnings.append(f"W-03 {label}: produced by {model!r}, current model is {llm.MODEL!r}")
    report.require(
        is_iso_date(entry.get("reviewed")),
        f"{label}: `reviewed` is missing or not YYYY-MM-DD (L-18)",
    )

    items = entry.get("items")
    if not report.require(isinstance(items, list), f"{label}: `items` must be an array"):
        return

    text = texts.get(point["source_id"])
    for index, item in enumerate(items):
        check_impact_item(f"{label}.items[{index}]", item, text, parties, report)

    check_impact_bounds(label, items, report)


def check_impact_item(label: str, item: dict, text: str | None, parties: list[dict], report: Report) -> None:
    if not report.require(isinstance(item, dict), f"{label}: item must be an object"):
        return

    # The lexical rules, on the statements alone: the span and the quote are the
    # document speaking, and the lexicon is never applied to them (L-11 to L-17).
    for violation in neutrality.violations(item, parties):
        report.errors.append(f"{label}: {violation}")

    unknown = sorted(set(item) - ITEM_KEYS)
    report.require(not unknown, f"{label}: unknown key(s) {unknown} (L-01)")

    kind = item.get("kind")
    basis = item.get("basis")
    report.require(kind in KINDS, f"{label}: `kind` must be one of {list(KINDS)}")
    report.require(basis in BASES, f"{label}: `basis` must be one of {sorted(BASES)}")

    # The proof is the mark (DP-31): a statement said to be provided for by the
    # document carries its fragment, one that is merely deduced carries none.
    span = item.get("span")
    report.require(
        (span is not None) == (basis == "text"),
        f"{label}: `span` is required if and only if basis is \"text\" (L-04)",
    )
    if isinstance(span, str):
        report.require(len(span) <= MAX_SPAN, f"{label}: `span` is over {MAX_SPAN} characters (L-10)")
        if text is None:
            report.warnings.append(f"W-04 {label}: span not verified, document not cached")
        else:
            report.require(needle(span) in text, f"{label}: `span` not found verbatim in the document (L-05)")

    affected = kind == "affected"
    for field in ("who", "directness"):
        report.require(
            (item.get(field) is not None) == affected,
            f"{label}: `{field}` is required if and only if kind is \"affected\" (L-06)",
        )
    if affected:
        report.require(item.get("who") in GROUPS, f"{label}: `who` is outside the vocabulary (L-07)")
        report.require(
            item.get("directness") in DIRECTNESS,
            f"{label}: `directness` must be one of {sorted(DIRECTNESS)}",
        )

    for lang in ("fr", "en"):
        statement = as_text(item.get(lang))
        report.require(bool(statement.strip()), f"{label}: `{lang}` is missing or empty (L-10)")
        report.require(
            len(statement) <= MAX_STATEMENT,
            f"{label}: `{lang}` is over {MAX_STATEMENT} characters (L-10)",
        )


def check_impact_bounds(label: str, items: list, report: Report) -> None:
    """Identical caps for every formation (DP-33): volume is an argument, so an
    analysis cannot be richer for one side than for another by construction."""
    kinds = [item.get("kind") for item in items if isinstance(item, dict)]
    for kind, (low, high) in BOUNDS.items():
        count = kinds.count(kind)
        report.require(low <= count <= high, f"{label}: {count} {kind} statement(s), {low} to {high} allowed (L-08)")

    low, high = TOTAL_BOUNDS
    report.require(low <= len(items) <= high, f"{label}: {len(items)} statements, {low} to {high} allowed (L-08)")

    bases = [item.get("basis") for item in items if isinstance(item, dict)]
    report.require(
        bases.count("inferred") <= bases.count("text"),
        f"{label}: more inferred than text statements (L-08)",
    )

    ranked = [KINDS.index(kind) for kind in kinds if kind in KINDS]
    report.require(ranked == sorted(ranked), f"{label}: `items` are not in canonical order (L-09)")


def check_impact_coverage(entries: dict, positions: dict, points: dict, report: Report) -> None:
    """All or nothing per question (DP-34), reported and never enforced.

    An uneven coverage inside one question is a bias — the reader compares the
    positions side by side and the one carrying an analysis looks documented.
    The renderer drops the whole question; here we only say so.
    """
    missing: list[str] = []
    for question_id, mapped in positions.items():
        ids = [entry["point"] for entry in mapped if entry["point"] in points]
        analysed = [point_id for point_id in ids if point_id in entries]
        if analysed and len(analysed) < len(ids):
            report.warnings.append(
                f"W-01 {question_id}: {len(analysed)} of {len(ids)} positions analysed — "
                "nothing will be shown for this question"
            )
        missing += [point_id for point_id in ids if point_id not in entries]

    if missing:
        report.warnings.append(
            f"W-02 {len(missing)} point(s) referenced by positions.json have no analysis entry"
        )


def is_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return len(value) == 10


def main(election: str = ELECTION) -> int:
    report = Report()
    check_election(election, report)

    if report.skipped:
        print(f"skipped quote verification for {len(report.skipped)} point(s): no cached documents")
        print("  run `python -m pipeline.run --step fetch` first")
    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"FAIL  {error}")
    if report.errors:
        print(f"\n{len(report.errors)} problem(s)")
        return 1
    print(f"ok — {election} content consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
