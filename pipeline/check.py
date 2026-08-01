"""Content invariants, enforced in CI. `python -m pipeline.check`

The load-bearing one is quote verification: every quote in content/programs must
appear verbatim in the document its source declares. That is what makes the
neutrality claim checkable by a machine rather than asserted in a README.

It needs the fetched documents, so CI runs fetch before check. Offline, that one
check is skipped and reported as skipped — never silently passed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

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


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.skipped: list[str] = []

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

    check_quotes(election, sources, points, report)

    questions = load(ROOT / "content" / "questions" / f"{election}.json")
    positions = load(ROOT / "content" / "questions" / f"{election}.positions.json")
    check_questions(questions, positions, points, [p["party"] for p in programs], report)


def check_quotes(election: str, sources: dict, points: dict, report: Report) -> None:
    """Every quote must be a verbatim substring of the document it cites."""
    texts: dict[str, str | None] = {}
    for source_id in sources:
        text = cached_text(election, source_id)
        texts[source_id] = haystack(text) if text is not None else None

    for point_id, point in points.items():
        text = texts[point["source_id"]]
        if text is None:
            report.skipped.append(point_id)
            continue
        needle = re.sub(r"\s+", " ", point["quote"]).strip()
        report.require(
            needle in text,
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


def main(election: str = ELECTION) -> int:
    report = Report()
    check_election(election, report)

    if report.skipped:
        print(f"skipped quote verification for {len(report.skipped)} point(s): no cached documents")
        print("  run `python -m pipeline.run --step fetch` first")
    for error in report.errors:
        print(f"FAIL  {error}")
    if report.errors:
        print(f"\n{len(report.errors)} problem(s)")
        return 1
    print(f"ok — {election} content consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
