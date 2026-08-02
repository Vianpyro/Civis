"""Structural rules of content/impacts/<election>.json — L-01 to L-10, L-18, L-19.

One case per rule, each asserting on the rule name in the message: a check that
fires without naming what it enforces is unusable in review, so the name is part
of the contract and is tested as such.

The fixture is a minimal but complete entry — one implication, one affected group,
one deduced effect — because every bound of DP-33 has a floor as well as a ceiling.
Each test breaks exactly one thing.
"""

from __future__ import annotations

import json
import unittest

from pipeline import llm
from pipeline.check import (
    ELECTION,
    Report,
    canonical,
    check_impacts,
    is_iso_date,
    quote_digest,
)
from pipeline.extract import haystack
from pipeline.fetch import ROOT

QUOTE = "réduisant la dépense publique plutôt qu'en augmentant la pression fiscale"
DOCUMENT = haystack(f"Nous tiendrons l'ordre dans nos comptes en {QUOTE}.")

POINTS = {"lr-depense": {"quote": QUOTE, "party": "lr", "source_id": "lr-doc"}}
TEXTS = {"lr-doc": DOCUMENT}
POSITIONS = {"q-depense": [{"point": "lr-depense", "stance": 1}]}
# No formation here: L-11 is a lexical rule and is exercised in test_neutrality.
PARTIES: list[dict] = []


def implication(**overrides):
    return {
        "kind": "implication",
        "basis": "text",
        "span": "réduisant la dépense publique",
        "fr": "La mesure porte l'ajustement sur le niveau de dépense.",
        "en": "The measure places the adjustment on spending levels.",
        **overrides,
    }


def affected(**overrides):
    return {
        "kind": "affected",
        "basis": "text",
        "span": "l'ordre dans nos comptes",
        "who": "state_services",
        "directness": "direct",
        "fr": "Les administrations de l'État sont visées par l'ajustement décrit.",
        "en": "State administrations are targeted by the described adjustment.",
        **overrides,
    }


def effect(**overrides):
    return {
        "kind": "effect",
        "basis": "inferred",
        "fr": "Les arbitrages budgétaires pourraient être révisés.",
        "en": "Budget trade-offs could be revised.",
        **overrides,
    }


def entry(**overrides):
    return {
        "of": quote_digest(QUOTE),
        # The current model, so that only the tests about W-03 raise it.
        "model": llm.MODEL,
        "reviewed": "2026-08-02",
        "items": [implication(), affected(), effect()],
        **overrides,
    }


def document(entries=None, **overrides):
    return {"election": ELECTION, "impacts": entries if entries is not None else {"lr-depense": entry()}, **overrides}


class ImpactsCase(unittest.TestCase):
    def run_check(self, data, raw=None, texts=TEXTS, positions=POSITIONS):
        """Raw defaults to the canonical form, so only the rule under test fires."""
        report = Report()
        check_impacts(
            data, raw if raw is not None else canonical(data), ELECTION, POINTS, positions, texts, PARTIES, report
        )
        return report

    def assertRule(self, data, rule, raw=None, texts=TEXTS):
        report = self.run_check(data, raw=raw, texts=texts)
        self.assertTrue(
            any(rule in error for error in report.errors),
            f"expected a {rule} failure, got {report.errors}",
        )

    def assertClean(self, data, **kwargs):
        report = self.run_check(data, **kwargs)
        self.assertEqual(report.errors, [])
        return report


class ValidEntry(ImpactsCase):
    def test_a_complete_entry_passes(self):
        report = self.assertClean(document())
        self.assertEqual(report.warnings, [])

    def test_an_empty_file_passes(self):
        # The state the repository ships in: no analysis is not a defect.
        self.assertClean(document({}))


class Structure(ImpactsCase):
    def test_unknown_key_at_every_level(self):
        cases = {
            "top-level": document(extra=1),
            "entry": document({"lr-depense": entry(extra=1)}),
            "item": document({"lr-depense": {**entry(), "items": [implication(extra=1), affected(), effect()]}}),
        }
        for level, data in cases.items():
            with self.subTest(level=level):
                self.assertRule(data, "L-01")

    def test_unknown_point_id(self):
        self.assertRule(document({"lr-inconnu": entry()}), "L-02")

    def test_election_must_match_the_file(self):
        data = document()
        data["election"] = "fr-2032"
        report = self.run_check(data)
        self.assertTrue(any("election" in error for error in report.errors))


class Fingerprint(ImpactsCase):
    def test_of_must_be_the_digest_of_the_quote(self):
        self.assertRule(document({"lr-depense": entry(of="0" * 64)}), "L-03")

    def test_of_must_be_a_sha256(self):
        self.assertRule(document({"lr-depense": entry(of="pas-une-empreinte")}), "L-03")

    def test_a_line_break_in_the_quote_does_not_change_the_digest(self):
        # DT-23: the digest is the expiry signal. If a re-wrapped quote produced
        # a new one, every entry would expire on a cosmetic change.
        self.assertEqual(quote_digest(QUOTE), quote_digest(QUOTE.replace(" ", "\n", 1)))


class Proof(ImpactsCase):
    def test_a_text_statement_without_a_span(self):
        item = implication()
        del item["span"]
        self.assertRule(document({"lr-depense": {**entry(), "items": [item, affected(), effect()]}}), "L-04")

    def test_an_inferred_statement_with_a_span(self):
        data = document({"lr-depense": {**entry(), "items": [implication(), affected(), effect(span="l'ordre")]}})
        self.assertRule(data, "L-04")

    def test_a_span_absent_from_the_document(self):
        data = document({"lr-depense": {**entry(), "items": [implication(span="jamais écrit ici"), affected(), effect()]}})
        self.assertRule(data, "L-05")

    def test_a_span_is_reported_not_verified_when_the_document_is_missing(self):
        # A-6, the same doctrine as check_quotes: offline the check is reported
        # as skipped, never silently passed.
        report = self.assertClean(document(), texts={"lr-doc": None})
        self.assertTrue(any(warning.startswith("W-04") for warning in report.warnings))


class Groups(ImpactsCase):
    def test_who_on_a_statement_that_is_not_affected(self):
        data = document({"lr-depense": {**entry(), "items": [implication(who="citizens"), affected(), effect()]}})
        self.assertRule(data, "L-06")

    def test_affected_without_directness(self):
        item = affected()
        del item["directness"]
        self.assertRule(document({"lr-depense": {**entry(), "items": [implication(), item, effect()]}}), "L-06")

    def test_who_outside_the_vocabulary(self):
        data = document({"lr-depense": {**entry(), "items": [implication(), affected(who="les_gens"), effect()]}})
        self.assertRule(data, "L-07")


class Bounds(ImpactsCase):
    def test_too_many_statements_of_one_kind(self):
        items = [implication() for _ in range(5)] + [affected()]
        self.assertRule(document({"lr-depense": {**entry(), "items": items}}), "L-08")

    def test_no_affected_statement(self):
        items = [implication(), implication(), implication()]
        self.assertRule(document({"lr-depense": {**entry(), "items": items}}), "L-08")

    def test_more_than_ten_statements_in_total(self):
        # Each kind stays within its own bounds: only the total is broken.
        items = [implication() for _ in range(4)] + [affected() for _ in range(5)] + [effect(basis="text", span="l'ordre dans nos comptes") for _ in range(4)]
        self.assertRule(document({"lr-depense": {**entry(), "items": items}}), "L-08")

    def test_more_inferred_than_text_statements(self):
        items = [implication(), affected(), effect(), effect(), effect()]
        self.assertRule(document({"lr-depense": {**entry(), "items": items}}), "L-08")

    def test_items_out_of_canonical_order(self):
        items = [affected(), implication(), effect()]
        self.assertRule(document({"lr-depense": {**entry(), "items": items}}), "L-09")


class Lengths(ImpactsCase):
    def test_an_empty_statement(self):
        data = document({"lr-depense": {**entry(), "items": [implication(fr="  "), affected(), effect()]}})
        self.assertRule(data, "L-10")

    def test_a_statement_over_two_hundred_characters(self):
        data = document({"lr-depense": {**entry(), "items": [implication(en="a" * 201), affected(), effect()]}})
        self.assertRule(data, "L-10")

    def test_a_span_over_three_hundred_characters(self):
        data = document({"lr-depense": {**entry(), "items": [implication(span="a" * 301), affected(), effect()]}})
        self.assertRule(data, "L-10")


class Review(ImpactsCase):
    def test_reviewed_is_required(self):
        item = entry()
        del item["reviewed"]
        self.assertRule(document({"lr-depense": item}), "L-18")

    def test_reviewed_must_be_a_real_date(self):
        for value in ("2026-8-2", "02/08/2026", "2026-02-30", ""):
            with self.subTest(value=value):
                self.assertRule(document({"lr-depense": entry(reviewed=value)}), "L-18")

    def test_iso_date_accepts_only_full_dates(self):
        self.assertTrue(is_iso_date("2026-08-02"))
        self.assertFalse(is_iso_date("2026-08"))
        self.assertFalse(is_iso_date(20260802))


class ModelDrift(ImpactsCase):
    """W-03 — llm.MODEL is the current model of the pipeline (DT-31)."""

    def test_an_entry_from_another_model_warns_without_failing(self):
        report = self.assertClean(document({"lr-depense": entry(model="un-autre-modele")}))
        self.assertTrue(any(warning.startswith("W-03") for warning in report.warnings))
        self.assertIn("un-autre-modele", " ".join(report.warnings))

    def test_an_entry_from_the_current_model_warns_about_nothing(self):
        self.assertEqual(self.assertClean(document()).warnings, [])

    def test_a_hand_written_entry_is_not_a_drift(self):
        # `model: "manual"` is a provenance, not a model name (DT-33): there is
        # no model it could have drifted from, and re-reading a flagged entry by
        # hand is what W-03 asks for — warning on the answer would be a loop.
        self.assertEqual(self.assertClean(document({"lr-depense": entry(model="manual")})).warnings, [])


class Canonical(ImpactsCase):
    def test_a_file_that_is_not_canonical_fails(self):
        data = document()
        self.assertRule(data, "L-19", raw=json.dumps(data) + "\n")

    def test_point_keys_are_sorted(self):
        data = {"election": ELECTION, "impacts": {"z-point": entry(), "a-point": entry()}}
        self.assertLess(canonical(data).index('"a-point"'), canonical(data).index('"z-point"'))

    def test_items_are_sorted_by_kind_and_stable_within_a_kind(self):
        first, second = implication(fr="premier"), implication(fr="second")
        data = {"election": ELECTION, "impacts": {"lr-depense": {**entry(), "items": [effect(), first, second, affected()]}}}
        kinds = [item["kind"] for item in json.loads(canonical(data))["impacts"]["lr-depense"]["items"]]
        self.assertEqual(kinds, ["implication", "implication", "affected", "effect"])
        statements = [item["fr"] for item in json.loads(canonical(data))["impacts"]["lr-depense"]["items"]]
        self.assertEqual(statements[:2], ["premier", "second"])

    def test_the_committed_file_is_canonical(self):
        # A-18 on the real file, not on a fixture.
        path = ROOT / "content" / "impacts" / f"{ELECTION}.json"
        raw = path.read_text(encoding="utf-8")
        self.assertEqual(canonical(json.loads(raw)), raw)


class Coverage(ImpactsCase):
    POSITIONS = {"q-depense": [{"point": "lr-depense", "stance": 1}, {"point": "rn-depense", "stance": -1}]}
    POINTS = {**POINTS, "rn-depense": {"quote": "autre", "party": "rn", "source_id": "lr-doc"}}

    def test_a_partly_covered_question_warns_without_failing(self):
        # A-5 on the CI side: DP-34 hides the question, check only says so.
        report = Report()
        check_impacts(
            document(), canonical(document()), ELECTION, self.POINTS, self.POSITIONS, TEXTS, PARTIES, report
        )
        self.assertEqual(report.errors, [])
        self.assertTrue(any(warning.startswith("W-01") for warning in report.warnings))

    def test_points_without_an_entry_are_counted(self):
        report = self.run_check(document({}))
        self.assertIn("W-02 1 point(s)", " ".join(report.warnings))

    def test_a_fully_covered_question_warns_about_nothing(self):
        self.assertEqual(self.assertClean(document()).warnings, [])
