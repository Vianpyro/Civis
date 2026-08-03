"""The two passes: the blind draft, the audit, and the one call point.

The load-bearing case is A-9. A leak of party identity into a prompt is silent —
nothing in the output reveals it, the draft looks exactly the same, and the
damage only shows up as content aligned with a camp's usual framing. A test is
the only thing standing there, so it runs over the real corpus and the real point
ids rather than over a convenient fixture.

A-15 is the second one: incremental regeneration is what makes a steady state
free, and it fails silently in the expensive direction — a run that redrafts
everything looks exactly like a run that redrafts what expired.

A-16 and A-17 are one assertion each: they guard a shape that is easy to break by
accident — an extra step in `all`, a second write path out of review/.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline import check, impacts, llm, run
from pipeline.check import Report, quote_digest
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


def statements() -> list[dict]:
    """Two statements as pass 1 returns them: one clean, one the lexicon rejects."""
    return [
        {
            "kind": "implication",
            "basis": "text",
            "span": "réduisant la dépense publique",
            "fr": "La mesure porte l'ajustement sur le niveau de dépense.",
            "en": "The measure places the adjustment on spending levels.",
        },
        {
            "kind": "effect",
            "basis": "inferred",
            "fr": "Cette excellente réforme réduira la dépense.",
            "en": "This excellent reform will reduce spending.",
        },
    ]


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


class Corpus(unittest.TestCase):
    """The real corpus and the real routing, over synthetic documents."""

    def setUp(self):
        documents = fake_documents()
        patch = mock.patch.object(
            impacts, "cached_text", lambda election, source_id: documents.get(source_id)
        )
        patch.start()
        self.addCleanup(patch.stop)
        # Nothing committed, so the fixture is the whole referenced corpus however
        # much of it PR-20 and PR-23 fill in. What the committed file actually
        # holds is exercised by its own test, where the coupling is the subject.
        empty = mock.patch.object(impacts, "committed", return_value={})
        empty.start()
        self.addCleanup(empty.stop)
        # review/ is the second cache since PR-B, so a draft left on the machine
        # running the tests would change what the corpus contains. The draft path
        # points at a file that does not exist yet; the tests that need a real one
        # write to it.
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.draft = Path(directory.name) / "draft.json"
        path = mock.patch.object(impacts, "draft_path", lambda election: self.draft)
        path.start()
        self.addCleanup(path.stop)
        self.units = impacts.units(ELECTION)
        self.requests = impacts.build_requests(self.units)

    def drafts(self, units_=None) -> dict[str, dict]:
        """The shape main() hands to pass 2, without calling a model."""
        return {
            unit["id"]: {
                "of": quote_digest(unit["quote"]),
                "model": llm.MODEL,
                "quote": unit["quote"],
                "context": unit["context"],
                "items": statements(),
            }
            for unit in (self.units if units_ is None else units_)
        }


class Blindness(Corpus):
    """A-9 — no formation identity, no document title, no file name in a request."""

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


class Incremental(Corpus):
    """A-15 — the cache is the committed file (DT-24), so a steady state is free."""

    def entries(self, of=None) -> dict[str, dict]:
        return {
            unit["id"]: {"of": of if of is not None else quote_digest(unit["quote"])}
            for unit in self.units
        }

    def test_a_second_run_without_a_content_change_produces_no_request(self):
        self.assertTrue(self.units, "the corpus must be exercised, or this proves nothing")
        with mock.patch.object(impacts, "committed", return_value=self.entries()):
            with quiet():
                again = impacts.units(ELECTION)
        self.assertEqual(again, [])
        self.assertEqual(impacts.build_requests(again), [])

    def test_an_entry_whose_quote_changed_is_redrafted(self):
        # `of` is the expiry signal (DT-23): a stale digest brings the point back.
        with mock.patch.object(impacts, "committed", return_value=self.entries(of="0" * 64)):
            self.assertEqual(len(impacts.units(ELECTION)), len(self.units))

    def test_force_redrafts_an_entry_that_is_up_to_date(self):
        with mock.patch.object(impacts, "committed", return_value=self.entries()):
            self.assertEqual(len(impacts.units(ELECTION, force=True)), len(self.units))

    def test_force_does_not_even_read_the_committed_file(self):
        with mock.patch.object(impacts, "committed") as committed:
            impacts.units(ELECTION, force=True)
        committed.assert_not_called()

    def test_limit_caps_the_points_of_one_run(self):
        capped = impacts.units(ELECTION, limit=3)
        self.assertEqual(len(capped), 3)
        # The prefix of the full run, so two capped runs in a row are not two
        # random samples of the same corpus.
        self.assertEqual(capped, self.units[:3])


class DraftCache(Corpus):
    """review/ is the second cache (PR-B): a point already drafted and awaiting a
    human is not drafted again. Same field, same comparison, no new format — and
    no step closer to content/, which review/ still never reaches (INV-23)."""

    def pending(self, of=None) -> dict[str, dict]:
        return {
            unit["id"]: {"of": of if of is not None else quote_digest(unit["quote"])}
            for unit in self.units
        }

    def test_a_point_absent_from_the_draft_is_drafted(self):
        with mock.patch.object(impacts, "drafted", return_value={}):
            with quiet():
                self.assertEqual(len(impacts.units(ELECTION)), len(self.units))

    def test_a_point_already_drafted_with_the_same_of_is_skipped(self):
        self.assertTrue(self.units, "the corpus must be exercised, or this proves nothing")
        with mock.patch.object(impacts, "drafted", return_value=self.pending()):
            with quiet():
                self.assertEqual(impacts.units(ELECTION), [])

    def test_a_drafted_point_whose_quote_changed_is_redrafted(self):
        # `of` is the expiry signal in review/ exactly as it is in content/.
        with mock.patch.object(impacts, "drafted", return_value=self.pending(of="0" * 64)):
            with quiet():
                self.assertEqual(len(impacts.units(ELECTION)), len(self.units))

    def test_force_ignores_the_draft_as_it_ignores_the_content(self):
        with mock.patch.object(impacts, "drafted") as drafted:
            with quiet():
                self.assertEqual(len(impacts.units(ELECTION, force=True)), len(self.units))
        drafted.assert_not_called()

    def test_a_committed_entry_wins_over_a_stale_draft(self):
        # content/ is the source of truth: a reviewed entry ends the point's life
        # in the queue whatever review/ still holds for it.
        with mock.patch.object(impacts, "committed", return_value=self.pending()):
            with mock.patch.object(impacts, "drafted", return_value=self.pending(of="0" * 64)):
                with quiet():
                    self.assertEqual(impacts.units(ELECTION), [])

    def test_an_absent_draft_file_reads_as_empty(self):
        self.assertFalse(self.draft.exists())
        self.assertEqual(impacts.drafted(ELECTION), {})


class Resume(Corpus):
    """An interruption costs the points the run did not reach, never those it had
    already obtained — and a capped run resumed does not pay twice."""

    def setUp(self):
        super().setUp()
        self.asked: list[list[str]] = []
        for patch in (
            mock.patch.object(llm, "configured", return_value=True),
            mock.patch.object(llm, "run_batch", self.answer),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    def answer(self, requests_: list[dict]) -> dict[str, dict]:
        """Pass 1 by its schema, pass 2 by elimination. No model, no network."""
        self.asked.append([request["custom_id"] for request in requests_])
        if requests_ and requests_[0]["schema"] is impacts.SCHEMA:
            return {request["custom_id"]: {"items": statements()} for request in requests_}
        return {request["custom_id"]: {"verdicts": []} for request in requests_}

    def read(self) -> dict[str, dict]:
        return json.loads(self.draft.read_text(encoding="utf-8"))

    def test_a_capped_run_resumed_keeps_what_the_first_run_produced(self):
        with quiet():
            impacts.main(ELECTION, limit=2)
        first = self.read()
        self.assertEqual(len(first), 2)

        with quiet():
            impacts.main(ELECTION, limit=2)
        second = self.read()
        self.assertEqual(len(second), 4)
        for point_id, draft in first.items():
            self.assertEqual(second[point_id], draft, f"{point_id} was drafted a second time")

    def test_the_second_run_asks_only_for_points_the_first_did_not_reach(self):
        with quiet():
            impacts.main(ELECTION, limit=2)
            impacts.main(ELECTION, limit=2)
        # Four batches: pass 1 and pass 2 of each run.
        self.assertEqual(len(self.asked), 4)
        self.assertEqual(set(self.asked[0]) & set(self.asked[2]), set())

    def test_a_stale_draft_entry_is_dropped_rather_than_left_for_the_reviewer(self):
        stale = self.units[-1]["id"]
        self.draft.write_text(json.dumps({stale: {"of": "0" * 64, "items": []}}), encoding="utf-8")
        with quiet():
            impacts.main(ELECTION, limit=1)
        # Back in the queue by `of`, and gone from the file: nobody transfers an
        # analysis of a quote that changed.
        self.assertNotIn(stale, self.read())

    def test_nothing_outside_review_is_written(self):
        # INV-23 on the run itself, not only on the source: `content/` is read.
        before = (ROOT / "content" / "impacts" / f"{ELECTION}.json").read_bytes()
        with quiet():
            impacts.main(ELECTION, limit=1)
        self.assertEqual((ROOT / "content" / "impacts" / f"{ELECTION}.json").read_bytes(), before)


class CommittedFile(unittest.TestCase):
    """The shipped state, read on the file itself — no mock, no fixture."""

    def test_an_absent_analyses_file_reads_as_empty(self):
        # No analysis is not a defect, and it is not a crash.
        self.assertEqual(impacts.committed("fr-2032"), {})

    def test_every_committed_entry_is_current(self):
        # A-15 in real conditions (DP-40, condition 4): each entry carries the
        # digest of the quote it analyses, so a second run asks for nothing.
        points = impacts.program_points(ELECTION)
        entries = impacts.committed(ELECTION)
        self.assertTrue(entries, "the pilot must be committed, or this proves nothing")
        for point_id, entry in entries.items():
            self.assertEqual(entry["of"], quote_digest(points[point_id]["quote"]), point_id)


class Fingerprint(unittest.TestCase):
    """`of` is computed once, in one place, and read by both modules (DT-26)."""

    def test_the_draft_and_the_linter_share_the_function(self):
        self.assertIs(impacts.quote_digest, check.quote_digest)

    def test_the_digest_the_draft_writes_is_the_one_L_03_expects(self):
        # On the real corpus rather than on a fixture: L-03 compares against the
        # quote of a committed point, and that is where a divergence would show.
        points = impacts.program_points(ELECTION)
        self.assertTrue(points)
        report = Report()
        for point_id, point in points.items():
            entry = {
                "of": impacts.quote_digest(point["quote"]),
                "model": llm.MODEL,
                "reviewed": "2026-08-02",
                "items": [],
            }
            check.check_impact_entry(point_id, entry, {point_id: point}, {}, [], report)
        self.assertEqual([error for error in report.errors if "L-03" in error], [])

    def test_a_digest_of_something_else_fails_L_03(self):
        points = impacts.program_points(ELECTION)
        point_id, point = next(iter(points.items()))
        report = Report()
        entry = {"of": quote_digest("autre chose"), "model": llm.MODEL, "reviewed": "2026-08-02", "items": []}
        check.check_impact_entry(point_id, entry, {point_id: point}, {}, [], report)
        self.assertTrue(any("L-03" in error for error in report.errors))


class SecondPass(Corpus):
    """The audit signals, it never rewrites and never drops (DP-36)."""

    @staticmethod
    def lines(prompt: str) -> set[str]:
        return {line.strip() for line in prompt.splitlines() if len(line.strip()) >= 20}

    def test_the_two_prompts_share_no_line(self):
        # An auditor who knows the rule rationalises its violation, and sharing a
        # constant is the natural way to get there.
        self.assertEqual(self.lines(impacts.SYSTEM) & self.lines(impacts.AUDIT_SYSTEM), set())
        self.assertNotIn(impacts.SYSTEM, impacts.AUDIT_SYSTEM)
        self.assertNotIn(impacts.AUDIT_SYSTEM, impacts.SYSTEM)

    def test_the_audit_does_not_learn_the_rules_of_pass_one(self):
        for tell in ("Bornes, par mesure", "Interdits absolus", "local_authorities", "énormément"):
            self.assertNotIn(tell, impacts.AUDIT_SYSTEM)

    def test_one_request_per_drafted_point_with_numbered_statements(self):
        requests = impacts.audit_requests(self.drafts())
        self.assertEqual(len(requests), len(self.units))
        body = requests[0]["user"]
        self.assertIn("0. [implication / text]", body)
        self.assertIn("1. [effect / inferred]", body)
        self.assertIn("span : « réduisant la dépense publique »", body)
        self.assertIn("en : The measure places", body)

    def test_a_point_without_a_statement_is_not_audited(self):
        drafts = self.drafts()
        for draft in drafts.values():
            draft["items"] = []
        self.assertEqual(impacts.audit_requests(drafts), [])

    def test_no_point_id_in_an_audit_body(self):
        drafts = self.drafts()
        for request in impacts.audit_requests(drafts):
            self.assertIn(request["custom_id"], drafts)
            for point_id in drafts:
                self.assertNotIn(point_id, request["user"])

    def test_every_statement_is_annotated_and_none_is_removed(self):
        drafts = self.drafts(self.units[:1])
        point_id = next(iter(drafts))
        verdicts = {
            point_id: {"verdicts": [{"index": 1, "verdict": "evaluative", "evidence": "excellente"}]}
        }
        impacts.annotate(drafts, verdicts, impacts.party_labels(ELECTION))

        items = drafts[point_id]["items"]
        self.assertEqual(len(items), 2, "a flagged statement stays in the draft")
        self.assertEqual([item["kind"] for item in items], ["implication", "effect"])
        for item in items:
            self.assertIn("lint", item)
            self.assertIn("audit", item)

        self.assertEqual(items[0]["lint"], [])
        self.assertIsNone(items[0]["audit"], "a statement the audit skipped carries no verdict")
        self.assertEqual(items[1]["audit"]["verdict"], "evaluative")
        # The linter of CI, called on the draft: same module, never a second copy.
        self.assertTrue(any("L-12" in violation for violation in items[1]["lint"]))
        self.assertTrue(any("L-16" in violation for violation in items[1]["lint"]))

    def test_a_verdict_for_an_unknown_index_annotates_nothing(self):
        drafts = self.drafts(self.units[:1])
        point_id = next(iter(drafts))
        impacts.annotate(drafts, {point_id: {"verdicts": [{"index": 9, "verdict": "ok", "evidence": ""}]}}, [])
        self.assertEqual([item["audit"] for item in drafts[point_id]["items"]], [None, None])

    def test_the_audit_answers_are_keyed_the_way_annotate_reads_them(self):
        # run_batch keys by custom_id and annotate looks up by point id: one
        # rename away from silently annotating nothing at all.
        drafts = self.drafts(self.units[:1])
        requests = impacts.audit_requests(drafts)
        self.assertEqual([request["custom_id"] for request in requests], list(drafts))


class Pacing(unittest.TestCase):
    """PR-A — the free tier allows five requests per minute. `post` recovers from
    a 429; `pace` is what keeps a run from earning one."""

    def setUp(self):
        # The clock is module state: a test must not inherit the previous one's.
        reset = mock.patch.object(llm, "_last_call", float("-inf"))
        reset.start()
        self.addCleanup(reset.stop)

    def batch(self, count: int, failing: str | None = None) -> list[float]:
        """The delays `run_batch` asked for, over `count` requests named 0, 1, …"""
        slept: list[float] = []

        def call(request, key):
            if request["custom_id"] == failing:
                raise RuntimeError("429")
            return {"items": []}

        requests_ = [
            {"custom_id": str(index), "system": "", "user": "", "schema": {}}
            for index in range(count)
        ]
        with mock.patch.object(llm.time, "sleep", slept.append):
            with mock.patch.dict(llm.PROVIDERS, {"gemini": {"call": call, "env": ("X",)}}):
                with mock.patch.dict("os.environ", {"X": "token"}), quiet():
                    llm.run_batch(requests_)
        return slept

    def test_the_first_call_of_a_process_is_not_delayed(self):
        self.assertEqual(self.batch(1), [])

    def test_calls_are_spaced_by_the_interval(self):
        delays = self.batch(3)
        self.assertEqual(len(delays), 2)
        for delay in delays:
            self.assertAlmostEqual(delay, llm.INTERVAL, delta=1)

    def test_the_spacing_holds_across_two_batches(self):
        # The two passes of a run share one quota, so the ceiling cannot be
        # per-batch: the first request of pass 2 follows the last of pass 1.
        self.batch(1)
        self.assertEqual(len(self.batch(1)), 1)

    def test_a_failing_call_still_consumes_its_slot(self):
        # A 429 is a request the provider counted. Skipping the pause after it
        # would send the next one straight into the same ceiling.
        self.assertEqual(len(self.batch(3, failing="1")), 2)

    def test_a_failing_call_is_still_reported_against_its_custom_id(self):
        out = io.StringIO()
        with mock.patch.object(llm.time, "sleep"):
            with mock.patch.dict(llm.PROVIDERS, {"gemini": {"call": self.raiser, "env": ("X",)}}):
                with mock.patch.dict("os.environ", {"X": "token"}):
                    with contextlib.redirect_stdout(out):
                        answers = llm.run_batch(
                            [{"custom_id": "lr-depense-publique", "system": "", "user": "", "schema": {}}]
                        )
        self.assertEqual(answers, {})
        self.assertIn("lr-depense-publique", out.getvalue())

    @staticmethod
    def raiser(request, key):
        raise RuntimeError("boom")


class Flags(unittest.TestCase):
    """`--limit` and `--force` belong to the impacts step and to no other."""

    def run_cli(self, argv: list[str]) -> dict[str, dict]:
        seen: dict[str, dict] = {}

        def record(name):
            def step(election, **flags):
                seen[name] = flags
                return 0

            return step

        steps = {name: record(name) for name in ("fetch", "impacts")}
        with mock.patch.dict(run.STEPS, steps, clear=True):
            with mock.patch("sys.argv", argv), quiet():
                self.assertEqual(run.main(), 0)
        return seen

    def test_limit_and_force_reach_the_impacts_step(self):
        seen = self.run_cli(["run", "--step", "impacts", "--limit", "2", "--force"])
        self.assertEqual(seen["impacts"], {"limit": 2, "force": True})

    def test_they_default_to_off(self):
        seen = self.run_cli(["run", "--step", "impacts"])
        self.assertEqual(seen["impacts"], {"limit": None, "force": False})

    def test_another_step_is_called_without_them(self):
        self.assertEqual(self.run_cli(["run", "--step", "fetch"])["fetch"], {})


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
        # Named once (PR-B), because the draft is now read back as well as
        # written. Under review/ and nowhere else, which is the whole of A-17.
        self.assertIn('return ROOT / "review" / f"{election}-impacts-draft.json"', self.SOURCE)
        self.assertIn("out = draft_path(election)", self.SOURCE)

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

    def test_the_retry_strategy_is_still_the_one_DT_31_describes(self):
        # Pacing is prevention; this is recovery. PR-A must not have replaced one
        # with the other — a 429 that slips through is still retried.
        self.assertEqual((llm.ATTEMPTS, llm.BACKOFF), (4, 5))

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
