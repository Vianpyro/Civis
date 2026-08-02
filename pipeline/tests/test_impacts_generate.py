"""Pass 1: the blind draft, its window of context, and the one call point.

The load-bearing case is A-9. A leak of party identity into a prompt is silent —
nothing in the output reveals it, the draft looks exactly the same, and the
damage only shows up as content aligned with a camp's usual framing. A test is
the only thing standing there, so it runs over the real corpus and the real point
ids rather than over a convenient fixture.

A-16 and A-17 are one assertion each: they guard a shape that is easy to break by
accident — an extra step in `all`, a second write path out of review/.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import unittest
from unittest import mock

from pipeline import impacts, llm
from pipeline.extract import context, haystack
from pipeline.fetch import ROOT, load_sources
from pipeline.run import ALL, STEPS

ELECTION = "fr-2027"
WORD = re.compile(r"[a-zà-ÿ]+")


def quiet():
    """The pipeline reports on stdout; a test run is not the place to read it."""
    return contextlib.redirect_stdout(io.StringIO())


def parties() -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))["party"]
        for path in sorted((ROOT / "content" / "programs" / ELECTION).glob("*.json"))
    ]


def fake_documents() -> dict[str, str]:
    """One synthetic document per source, holding that source's real quotes.

    The cached documents are not committed, so a test that needed them would be
    vacuous on a clean checkout. Building the document out of the quotes keeps the
    real point ids, the real themes and the real routing through positions.json —
    which is what A-9 is about — without depending on a fetch.
    """
    documents: dict[str, list[str]] = {}
    for path in sorted((ROOT / "content" / "programs" / ELECTION).glob("*.json")):
        program = json.loads(path.read_text(encoding="utf-8"))
        documents.setdefault(program["source_id"], []).extend(
            point["quote"] for point in program["points"]
        )
    return {
        source_id: "Introduction du document. " + " ".join(quotes) + " Fin du document."
        for source_id, quotes in documents.items()
    }


class Context(unittest.TestCase):
    DOCUMENT = "Alpha bravo charlie. La mesure porte sur le seuil retenu. Delta echo foxtrot."
    QUOTE = "La mesure porte sur le seuil retenu."

    def test_quote_is_inside_the_window(self):
        self.assertIn(self.QUOTE, context(self.DOCUMENT, self.QUOTE))

    def test_window_wider_than_the_document_returns_it_whole(self):
        self.assertEqual(context(self.DOCUMENT, self.QUOTE), self.DOCUMENT)

    def test_quote_at_the_very_start(self):
        text = self.QUOTE + " " + "mot " * 200
        self.assertTrue(context(text, self.QUOTE, window=50).startswith(self.QUOTE))

    def test_quote_at_the_very_end(self):
        text = "mot " * 200 + self.QUOTE
        self.assertTrue(context(text, self.QUOTE, window=50).endswith(self.QUOTE))

    def test_absent_quote_yields_nothing(self):
        # Nothing honest to send about a measure we cannot locate in its document.
        self.assertEqual(context(self.DOCUMENT, "Une phrase absente du document."), "")

    def test_cut_on_word_boundaries(self):
        text = "alphabet " * 100 + self.QUOTE + " sigma " * 100
        window = context(text, self.QUOTE, window=30)
        self.assertNotIn("bet alphabet", window[:3])
        for edge in (window.split(" ")[0], window.split(" ")[-1]):
            self.assertIn(edge, text.split())

    def test_window_bounds_the_document(self):
        text = "mot " * 5000 + self.QUOTE + " mot" * 5000
        window = context(text, self.QUOTE, window=200)
        self.assertLess(len(window), len(self.QUOTE) + 500)

    def test_a_line_break_does_not_hide_the_quote(self):
        # The window is cut out of haystack() text, so a span copied from it is
        # still found verbatim by check (INV-19).
        text = "Alpha bravo.\nLa mesure porte sur\nle seuil retenu.\nDelta echo."
        window = context(text, self.QUOTE)
        self.assertIn(self.QUOTE, window)
        self.assertIn(window, haystack(text))


class Blindness(unittest.TestCase):
    """A-9 — no formation identity, no document title, no file name in a request."""

    def setUp(self):
        documents = fake_documents()
        patch = mock.patch.object(
            impacts, "cached_text", lambda election, source_id: documents.get(source_id)
        )
        patch.start()
        self.addCleanup(patch.stop)
        self.units = impacts.units(ELECTION)
        self.requests = impacts.build_requests(self.units)

    def bodies(self) -> list[str]:
        return [request["system"] + "\n" + request["user"] for request in self.requests]

    def written(self) -> list[str]:
        """What this module composes around the data: the user message minus the
        quote, the document window and the vocabulary.

        Those three are given: the quote is committed content, the window is the
        document speaking, the vocabulary is a closed list of identifiers. What is
        left is written here, and it must carry no formation identity at all — no
        exemption, no documented false positive.
        """
        vocabulary = "\n".join(impacts.VOCABULARY)
        # The window before the quote: the window contains the quote, so removing
        # the quote first would leave a mangled window standing.
        return [
            request["user"]
            .replace(unit["context"], " ")
            .replace(unit["quote"], " ")
            .replace(vocabulary, " ")
            for request, unit in zip(self.requests, self.units)
        ]

    def test_the_corpus_is_actually_exercised(self):
        # A vacuous pass would be worse than no test at all here.
        self.assertGreaterEqual(len(self.requests), 10)

    def test_no_party_label_in_what_this_module_writes(self):
        for body in self.written():
            lowered = body.lower()
            words = set(WORD.findall(lowered))
            for party in parties():
                for label in (party["id"], party["short"]):
                    self.assertNotIn(label.lower(), words, f"party label {label!r} in a request")
                self.assertNotIn(party["name"].lower(), lowered, "party name in a request")

    def test_the_only_label_collision_in_the_prompt_is_the_documented_one(self):
        """The system prompt is normative text (§9.1) and cannot be rephrased.

        It forbids « l'ensemble des », and "Ensemble" is also a party short name:
        the false positive already documented in check.py, where the answer is to
        rephrase the question. Here the wording is fixed by the DP, so the
        collision is named instead — and asserted, so that a second one, or a real
        formation name added to the prompt, fails right here.
        """
        words = set(WORD.findall(impacts.SYSTEM.lower()))
        labels = {label.lower() for party in parties() for label in (party["id"], party["short"])}
        self.assertEqual(words & labels, {"ensemble"})
        for party in parties():
            self.assertNotIn(party["name"].lower(), impacts.SYSTEM.lower())

    def test_no_point_id_in_any_body(self):
        # The custom_id carries the point id, and a point id carries a party
        # prefix (`lr-depense-publique`). That is the vector DP-35 names.
        ids = [unit["id"] for unit in self.units]
        for body in self.bodies():
            for point_id in ids:
                self.assertNotIn(point_id, body)

    def test_no_source_id_or_document_title_in_any_body(self):
        sources = load_sources(ELECTION)
        for body in self.bodies():
            lowered = body.lower()
            for source in sources:
                self.assertNotIn(source["id"].lower(), lowered)
                self.assertNotIn(source["title"].lower(), lowered)

    def test_no_file_name_in_any_body(self):
        names = [path.name for path in (ROOT / "content" / "programs" / ELECTION).glob("*.json")]
        for body, written in zip(self.bodies(), self.written()):
            # The stem as a whole word — "rn" is a substring of "gouvernement",
            # the same trap check_questions documents.
            words = set(WORD.findall(written.lower()))
            for name in names:
                self.assertNotIn(name, body)
                self.assertNotIn(name.removesuffix(".json").lower(), words)

    def test_the_custom_id_is_still_the_point_id(self):
        # Blind in the body, addressable outside it: the reviewer needs to know
        # which measure an answer belongs to.
        self.assertEqual([r["custom_id"] for r in self.requests], [u["id"] for u in self.units])

    def test_only_referenced_points_are_drafted(self):
        positions = json.loads(
            (ROOT / "content" / "questions" / f"{ELECTION}.positions.json").read_text(encoding="utf-8")
        )
        referenced = {entry["point"] for mapped in positions.values() for entry in mapped}
        self.assertTrue({unit["id"] for unit in self.units} <= referenced)

    def test_the_vocabulary_is_offered_to_the_model(self):
        for request in self.requests:
            self.assertIn("local_authorities", request["user"])


class Steps(unittest.TestCase):
    def test_impacts_is_registered(self):
        self.assertIs(STEPS["impacts"], impacts.main)

    def test_all_does_not_run_impacts(self):
        # A-16, DT-28: a model call costs money and needs a reviewer.
        self.assertNotIn("impacts", ALL)
        self.assertNotIn("generate", ALL)


class WritePaths(unittest.TestCase):
    """A-17 — impacts.py has no write path outside review/ (INV-23)."""

    SOURCE = (ROOT / "pipeline" / "impacts.py").read_text(encoding="utf-8")
    WRITES = re.compile(r"([\w.]+)\.(?:write_text|write_bytes|mkdir|touch|unlink|open)\(")

    def test_the_only_write_target_is_the_review_file(self):
        targets = set(self.WRITES.findall(self.SOURCE))
        self.assertTrue(targets, "the write path moved; this test must follow it")
        for target in targets:
            self.assertTrue(target.startswith("out"), f"write through {target!r}")
        self.assertIn('out = ROOT / "review" / f"{election}-impacts-draft.json"', self.SOURCE)

    def test_nothing_is_written_without_credentials(self):
        with mock.patch.object(llm, "configured", return_value=False):
            with mock.patch.object(impacts, "units") as units_:
                with quiet():
                    self.assertEqual(impacts.main(ELECTION), 0)
        units_.assert_not_called()


class Provider(unittest.TestCase):
    def test_the_default_provider_resolves(self):
        self.assertIn("call", llm.provider())
        self.assertEqual(llm.provider(), llm.PROVIDERS[llm.PROVIDER])

    def test_an_unknown_provider_fails_naming_it(self):
        with self.assertRaises(ValueError) as raised:
            llm.provider("mistral")
        self.assertIn("mistral", str(raised.exception))

    def test_an_unknown_provider_is_not_read_as_missing_credentials(self):
        with mock.patch.object(llm, "PROVIDER", "mistral"):
            with self.assertRaises(ValueError):
                llm.configured()

    def test_the_output_schema_is_stripped_for_the_provider(self):
        # Gemini's schema subset rejects `additionalProperties`; the DP's schema
        # carries it. The conversion belongs to llm.py and to nothing else.
        stripped = json.dumps(llm.openapi(impacts.SCHEMA))
        self.assertNotIn("additionalProperties", stripped)
        self.assertIn("implication", stripped)
        self.assertIn("additionalProperties", json.dumps(impacts.SCHEMA))

    def test_run_batch_keys_answers_by_custom_id(self):
        calls = []

        def call(request, key):
            calls.append(request["custom_id"])
            return {"items": []}

        with mock.patch.dict(llm.PROVIDERS, {"gemini": {"call": call, "env": ("X",)}}):
            with mock.patch.dict("os.environ", {"X": "token"}):
                answers = llm.run_batch([{"custom_id": "a", "system": "", "user": "", "schema": {}}])
        self.assertEqual(calls, ["a"])
        self.assertEqual(answers, {"a": {"items": []}})

    def test_a_failing_point_does_not_lose_the_others(self):
        def call(request, key):
            if request["custom_id"] == "a":
                raise RuntimeError("429")
            return {"items": []}

        with mock.patch.dict(llm.PROVIDERS, {"gemini": {"call": call, "env": ("X",)}}):
            with mock.patch.dict("os.environ", {"X": "token"}), quiet():
                answers = llm.run_batch(
                    [{"custom_id": name, "system": "", "user": "", "schema": {}} for name in ("a", "b")]
                )
        self.assertEqual(list(answers), ["b"])
