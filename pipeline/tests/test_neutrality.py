"""Lexical rules L-11 to L-17, and the guarantee that they stop at the statement.

One case per rule, asserting on the rule name in the message, plus the two cases
that matter most in review: a term of the lexicon inside a span must NOT fail —
that is the document speaking — and the six examples of the original request,
which are the first fixture of the linter (A-3).
"""

from __future__ import annotations

import unittest

from pipeline.check import Report, canonical, check_impacts
from pipeline.neutrality import violations
from pipeline.tests.test_impacts_schema import (
    ELECTION,
    POINTS,
    POSITIONS,
    TEXTS,
    affected,
    document,
    effect,
    entry,
    implication,
)

PARTIES = [{"id": "lr", "short": "LR", "name": "Les Républicains"}]


def statement(**overrides):
    """A neutral statement, to be broken one field at a time."""
    return {
        "kind": "implication",
        "basis": "text",
        "span": "réduisant la dépense publique",
        "fr": "La mesure porte l'ajustement sur le niveau de dépense.",
        "en": "The measure places the adjustment on spending levels.",
        **overrides,
    }


class NeutralityCase(unittest.TestCase):
    def assertRule(self, item, rule, parties=PARTIES):
        found = violations(item, parties)
        self.assertTrue(any(rule in message for message in found), f"expected {rule}, got {found}")

    def assertClean(self, item, parties=PARTIES):
        self.assertEqual(violations(item, parties), [])


class Baseline(NeutralityCase):
    def test_a_descriptive_statement_passes(self):
        self.assertClean(statement())

    def test_an_inferred_statement_in_the_conditional_passes(self):
        self.assertClean(
            statement(
                basis="inferred",
                span=None,
                fr="Les arbitrages budgétaires pourraient être révisés.",
                en="Budget trade-offs could be revised.",
            )
        )


class Formations(NeutralityCase):
    def test_an_identifier_as_a_whole_word(self):
        self.assertRule(statement(fr="La mesure du lr porte sur la dépense."), "L-11")

    def test_a_full_name_as_a_substring(self):
        self.assertRule(statement(fr="Les Républicains portent cette mesure."), "L-11")

    def test_an_identifier_hidden_inside_a_word_is_not_a_match(self):
        # "lr" inside a longer word is not the formation, and a checker that
        # flagged it would be unusable. Same mechanic as check_questions.
        self.assertClean(statement(fr="Le calendrier alrédigé n'existe pas."))


class Lexicon(NeutralityCase):
    def test_an_evaluative_term(self):
        self.assertRule(statement(fr="Cette mesure est une réforme véritable."), "L-12")

    def test_a_value_verb(self):
        self.assertRule(statement(fr="La mesure vise à protéger les locataires."), "L-12")

    def test_an_intensifier(self):
        self.assertRule(statement(fr="La dépense est très encadrée par le texte."), "L-12")

    def test_the_english_lexicon_applies_to_the_english_field(self):
        self.assertRule(statement(en="This is a massive change to the rules."), "L-12")

    def test_a_superlative(self):
        self.assertRule(statement(fr="C'est le plus large des dispositifs prévus."), "L-13")

    def test_an_exclamation_mark(self):
        self.assertRule(statement(fr="Le dispositif entre en vigueur immédiatement !"), "L-13")


class Quantifiers(NeutralityCase):
    def test_a_quantifier_absent_from_the_span(self):
        self.assertRule(statement(fr="Toutes les collectivités appliquent le dispositif."), "L-14")

    def test_a_quantifier_carried_by_the_span_is_admitted(self):
        self.assertClean(
            statement(
                span="toutes les collectivités",
                fr="Toutes les collectivités appliquent le dispositif.",
                en="The measure applies to the listed authorities.",
            )
        )

    def test_a_quantifier_in_an_inferred_statement_is_never_admitted(self):
        # Nothing supports it: an inferred statement has no span by construction.
        self.assertRule(
            statement(
                basis="inferred",
                span=None,
                fr="Toutes les collectivités pourraient appliquer le dispositif.",
                en="Authorities could apply the arrangement.",
            ),
            "L-14",
        )


class Certainty(NeutralityCase):
    def test_an_inferred_statement_without_an_uncertainty_marker(self):
        self.assertRule(
            statement(
                basis="inferred",
                span=None,
                fr="Les arbitrages budgétaires sont révisés chaque année.",
                en="Budget trade-offs are revised.",
            ),
            "L-15",
        )

    def test_an_inferred_statement_in_the_indicative_future(self):
        # The uncertainty marker is present, so only L-16 is at stake here.
        self.assertRule(
            statement(
                basis="inferred",
                span=None,
                fr="Le dispositif sera révisé selon les modalités retenues.",
                en="The arrangement could be revised depending on the terms.",
            ),
            "L-16",
        )

    def test_a_text_statement_needs_no_marker(self):
        self.assertClean(statement(fr="Le texte fixe le niveau de la dépense.", en="The text sets the spending level."))


class Figures(NeutralityCase):
    def test_a_figure_in_an_inferred_statement(self):
        self.assertRule(
            statement(
                basis="inferred",
                span=None,
                fr="La dépense pourrait baisser de 3 points.",
                en="Spending could fall by 3 points.",
            ),
            "L-17",
        )

    def test_a_figure_absent_from_the_span(self):
        self.assertRule(statement(fr="Le texte fixe un plafond de 12 mois."), "L-17")

    def test_a_figure_carried_by_the_span_is_admitted(self):
        self.assertClean(
            statement(
                span="un plafond de 12 mois",
                fr="Le texte fixe un plafond de 12 mois.",
                en="The text sets a 12 month cap.",
            )
        )


class NotAppliedToTheDocument(NeutralityCase):
    def test_an_evaluative_term_inside_a_span_does_not_fail(self):
        # The load-bearing case of this module. A span is the document speaking:
        # blocking a word it contains would be censoring the source, and would
        # make it impossible to quote whole categories of measures.
        self.assertClean(
            statement(
                span="une réforme véritable et un effort massif",
                fr="Le texte engage un effort budgétaire sur la période.",
                en="The text commits a budget effort over the period.",
            )
        )


class OriginalExamples(NeutralityCase):
    """A-3 — the six examples of the original request as the first fixture."""

    CORRECT = (
        statement(),
        statement(
            kind="affected",
            who="state_services",
            directness="direct",
            span="l'ordre dans nos comptes",
            fr="Les administrations de l'État sont visées par l'ajustement décrit.",
            en="State administrations are targeted by the described adjustment.",
        ),
        statement(
            kind="effect",
            basis="inferred",
            span=None,
            fr="Les arbitrages budgétaires pourraient être révisés selon les modalités retenues.",
            en="Annual budget trade-offs could be revised depending on the arrangements chosen.",
        ),
    )

    def test_the_three_correct_examples_pass(self):
        for item in self.CORRECT:
            with self.subTest(fr=item["fr"]):
                self.assertClean(item)

    def test_aidera_enormement_is_rejected(self):
        self.assertRule(statement(fr="La mesure aidera énormément les entreprises."), "L-12")

    def test_penalisera_is_rejected(self):
        # Written as the deduction it is, this is caught by L-15: an inferred
        # statement stated as a fact. See the report — the DP maps this example
        # to L-16, whose closed list does not hold "pénalisera".
        self.assertRule(
            statement(basis="inferred", span=None, fr="La mesure pénalisera les entreprises.", en="The measure will affect businesses."),
            "L-15",
        )

    def test_cette_excellente_reforme_is_rejected(self):
        self.assertRule(statement(fr="Cette excellente réforme entre en vigueur."), "L-12")


class Wiring(NeutralityCase):
    """The rules must fire through pipeline.check, not only when called directly."""

    def test_an_evaluative_statement_fails_the_content_check(self):
        data = document({"lr-depense": {**entry(), "items": [implication(fr="Une mesure véritable."), affected(), effect()]}})
        report = Report()
        check_impacts(data, canonical(data), ELECTION, POINTS, POSITIONS, TEXTS, PARTIES, report)
        self.assertTrue(any("L-12" in error for error in report.errors), report.errors)

    def test_the_committed_content_holds_no_lexical_violation(self):
        # Empty today; the day PR-20 lands, this test starts saying something.
        from pipeline.check import ELECTION as election, load
        from pipeline.fetch import ROOT

        data = load(ROOT / "content" / "impacts" / f"{election}.json")
        for point_id, item in data["impacts"].items():
            for index, statement_ in enumerate(item["items"]):
                with self.subTest(point=point_id, index=index):
                    self.assertEqual(violations(statement_, PARTIES), [])
