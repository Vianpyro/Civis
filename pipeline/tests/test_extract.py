"""The text layer every quote check rests on.

`haystack()` is what INV-06 comes down to in practice: a quote is "verbatim" if
it survives this function on both sides. Until now nothing tested it, so what
"verbatim" tolerates — a line break inside a PDF sentence, a typographic
apostrophe, a ligature — was written nowhere and could have been widened by
accident. These cases are that definition, written down.

`flatten()` and `candidates()` feed the drafting pass. A defect there produces
worse drafts, never a wrong invariant, so they are covered more lightly.
"""

from __future__ import annotations

import unittest

from pipeline.extract import candidates, flatten, haystack, normalise


class Normalise(unittest.TestCase):
    # One entry per replacement in the table. A character dropped from it stops
    # being normalised on the document side while quotes keep arriving with the
    # plain form, and every quote citing that document silently fails to match.
    REPLACEMENTS = [
        ("\xa0", " "),  # no-break space
        (" ", " "),  # narrow no-break space
        ("’", "'"),  # right single quotation mark
        ("‘", "'"),  # left single quotation mark
        ("“", '"'),
        ("”", '"'),
        ("–", "-"),  # en dash
        ("—", "-"),  # em dash
        ("ﬁ", "fi"),  # fi ligature, produced by PDF extraction
        ("ﬂ", "fl"),
        ("œ", "oe"),
        ("Œ", "OE"),
    ]

    def test_every_replacement_of_the_table(self):
        for source, expected in self.REPLACEMENTS:
            with self.subTest(source=source):
                self.assertEqual(normalise(f"un{source}mot"), f"un{expected}mot")

    def test_collapses_spaces_and_tabs(self):
        self.assertEqual(normalise("un  \t  mot"), "un mot")

    def test_leaves_line_breaks_alone(self):
        # Paragraph structure is what flatten() reads afterwards. Collapsing new
        # lines here would erase it before anyone got to use it.
        self.assertEqual(normalise("un\n\nmot"), "un\n\nmot")


class Haystack(unittest.TestCase):
    def test_a_quote_broken_by_a_line_break_is_found(self):
        # The load-bearing case. A line break in a PDF is a rendering artefact,
        # so a quote spanning one is still verbatim.
        document = "Nous créons une allocation\npour les aidants familiaux."
        self.assertIn("Nous créons une allocation pour les aidants familiaux.", haystack(document))

    def test_a_quote_with_one_word_changed_is_not_found(self):
        document = haystack("Nous créons une allocation pour les aidants familiaux.")
        self.assertNotIn("Nous créons une allocation pour les aidants isolés.", document)

    def test_typography_is_normalised_on_the_document_side(self):
        # check.py collapses whitespace on the needle but does not normalise it:
        # the plain form is what matches, and the typographic form is what does
        # not. That asymmetry is why quotes are stored already normalised in
        # content/ — a quote committed with a curly apostrophe never matches.
        document = haystack("l’ordre dans nos comptes")
        self.assertIn("l'ordre dans nos comptes", document)
        self.assertNotIn("l’ordre dans nos comptes", document)


class Flatten(unittest.TestCase):
    def test_a_bullet_opens_a_paragraph_mid_sentence(self):
        # Program PDFs are mostly bullet lists. Merging across items fabricates
        # sentences, and a fabricated sentence can become a fabricated quote.
        text = "Nous créons une allocation\n• Nous supprimons la taxe"
        self.assertEqual(flatten(text), "Nous créons une allocation\nNous supprimons la taxe")

    def test_a_line_without_terminal_punctuation_continues(self):
        text = "Une phrase coupée\npar la mise en page."
        self.assertEqual(flatten(text), "Une phrase coupée par la mise en page.")

    def test_a_blank_line_closes_a_paragraph(self):
        text = "Un début\n\nUne suite."
        self.assertEqual(flatten(text), "Un début\nUne suite.")

    def test_trailing_text_is_not_lost(self):
        self.assertEqual(flatten("Sans ponctuation finale"), "Sans ponctuation finale")


class Candidates(unittest.TestCase):
    TEXT = (
        "Nous créons une allocation pour les aidants familiaux.\n"
        "Ce paragraphe ne ressemble pas à un engagement vérifiable.\n"
        "Nous créons une allocation pour les aidants familiaux.\n"
        "Supprimer la taxe intérieure sur la consommation finale d'électricité.\n"
        "Nous agirons.\n"
    )

    def test_keeps_commitments_in_order_without_duplicates(self):
        self.assertEqual(
            candidates(self.TEXT),
            [
                "Nous créons une allocation pour les aidants familiaux.",
                "Supprimer la taxe intérieure sur la consommation finale d'électricité.",
            ],
        )

    def test_deduplicates_regardless_of_case(self):
        text = "Nous créons une allocation pour les aidants familiaux.\n" "NOUS CRÉONS UNE ALLOCATION POUR LES AIDANTS FAMILIAUX.\n"
        self.assertEqual(len(candidates(text)), 1)

    def test_length_bounds_are_parameters(self):
        # "Nous agirons." is a commitment by shape and useless by length; the
        # floor is what excludes it, not the pattern.
        self.assertNotIn("Nous agirons.", candidates(self.TEXT))
        self.assertIn("Nous agirons.", candidates(self.TEXT, min_len=10))

    def test_an_overlong_sentence_is_dropped(self):
        self.assertEqual(candidates("Nous " + "prolongeons " * 40 + "."), [])
