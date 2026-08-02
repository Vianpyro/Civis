"""Lexical neutrality of impact statements — rules L-11 to L-17.

One module, imported by check.py for committed content and, later, by impacts.py
to annotate a draft. Never two copies: a duplicated lexicon diverges, and the
copy that diverges is always the one in CI.

The guarantee is on the product, not on the producer. A prompt instruction is
not verifiable and does not survive a change of model or provider; a list
applied to what is committed does (INV-21, DT-29).

Applied to the `fr` and `en` fields only. A span is a fragment of an official
document and a quote is evidence: an evaluative word inside one is the document
speaking, not us, and blocking it would be censoring the source.

The lexicon is itself an editorial artefact. It is short, in the open, and
extended by review — never by an exception for one entry, which is the shape
this rule is most likely to be broken by (INV-21). It produces false positives,
and the repository's doctrine is to rephrase: strict verification beats clever
verification.
"""

from __future__ import annotations

import re

LANGS = ("fr", "en")

# A word, in the sense used for matching: letters only, accents included. The
# same tokenisation as check_questions, so "rn" cannot hide inside
# "gouvernement" and "très" is found inside "très fortement".
WORD = re.compile(r"[a-zà-ÿ]+")

EVALUATIVE = {
    "fr": (
        "ambitieux",
        "bon",
        "bonne",
        "catastrophique",
        "courageux",
        "dérisoire",
        "désastreux",
        "enfin",
        "excellent",
        "excellente",
        "généreux",
        "historique",
        "indispensable",
        "inéquitable",
        "injuste",
        "insuffisant",
        "juste",
        "laxiste",
        "massif",
        "massive",
        "mauvais",
        "mauvaise",
        "nécessaire",
        "remarquable",
        "ruineux",
        "salutaire",
        "scandaleux",
        "urgent",
        "véritable",
        "équitable",
    ),
    "en": (
        "ambitious",
        "bad",
        "catastrophic",
        "courageous",
        "devastating",
        "essential",
        "excellent",
        "fair",
        "generous",
        "good",
        "historic",
        "insufficient",
        "massive",
        "necessary",
        "negligible",
        "remarkable",
        "scandalous",
        "unfair",
        "urgent",
    ),
}

VALUE_VERBS = {
    "fr": (
        "aider",
        "améliorer",
        "défavoriser",
        "dégrader",
        "favoriser",
        "nuire",
        "pénaliser",
        "protéger",
        "punir",
        "récompenser",
        "sanctionner",
    ),
    "en": (
        "favor",
        "favour",
        "harm",
        "help",
        "improve",
        "penalise",
        "penalize",
        "protect",
        "punish",
        "reward",
        "worsen",
    ),
}

INTENSIFIERS = {
    "fr": (
        "considérablement",
        "dramatiquement",
        "extrêmement",
        "fortement",
        "particulièrement",
        "très",
        "énormément",
    ),
    "en": (
        "considerably",
        "dramatically",
        "extremely",
        "greatly",
        "hugely",
        "particularly",
        "significantly",
        "very",
    ),
}

SUPERLATIVES = {
    "fr": ("la moins", "la plus", "le moins", "le plus"),
    "en": ("the least", "the most"),
}

# A quantification is a claim about coverage. It is admissible only when the
# document makes it, which is why it needs the span to carry the same word.
QUANTIFIERS = {
    "fr": (
        "aucun",
        "aucune",
        "chaque",
        "jamais",
        "la totalité",
        "l'ensemble des",
        "tous",
        "toujours",
        "toutes",
    ),
    "en": ("all", "always", "every", "never", "none"),
}

UNCERTAINTY = {
    "fr": (
        "devrait",
        "devraient",
        "en fonction de",
        "peut",
        "peuvent",
        "pourrait",
        "pourraient",
        "selon",
        "serait",
        "seraient",
        "susceptible",
        "susceptibles",
    ),
    "en": ("are expected to", "could", "depending on", "is expected to", "may", "might", "would"),
}

# Closed list: the indicative future, which states a deduction as a fact.
ASSERTIVE = {
    "fr": (
        "augmentera",
        "aura",
        "auront",
        "devra",
        "devront",
        "entraînera",
        "entraîneront",
        "permettra",
        "permettront",
        "réduira",
        "sera",
        "seront",
    ),
    "en": ("shall", "will"),
}


def hits(text: str, terms: tuple[str, ...]) -> list[str]:
    """Terms present in `text`: whole word for a word, substring for a phrase."""
    lowered = text.lower()
    words = set(WORD.findall(lowered))
    return [term for term in terms if (term in words if term.isalpha() else term in lowered)]


def violations(item: dict, parties: list[dict]) -> list[str]:
    """Every lexical rule broken by one statement, each naming its rule.

    Returns messages rather than raising: a review reads the whole list at once,
    and stopping at the first one would hide a systematic drift.
    """
    found: list[str] = []
    basis = item.get("basis")
    span = item.get("span") if isinstance(item.get("span"), str) else ""

    for lang in LANGS:
        statement = item.get(lang)
        # An empty or missing statement is reported by the schema check; there is
        # nothing lexical to say about it.
        if not isinstance(statement, str) or not statement.strip():
            continue
        found += formations(statement, lang, parties)
        found += lexicon(statement, lang)
        found += quantifiers(statement, lang, basis, span)
        found += certainty(statement, lang, basis)
        found += figures(statement, lang, basis, span)
    return found


def formations(statement: str, lang: str, parties: list[dict]) -> list[str]:
    """L-11 — no formation identity in a statement, whatever the wording."""
    lowered = statement.lower()
    words = set(WORD.findall(lowered))
    found = []
    for party in parties:
        # Ids and short names as whole words — "rn" is a substring of
        # "gouvernement". A full name is multi-word, so substring is safe.
        for label in (party["id"], party["short"]):
            if label.lower() in words:
                found.append(f'L-11 formation label "{label}" in `{lang}`')
        if party["name"].lower() in lowered:
            found.append(f'L-11 formation name "{party["name"]}" in `{lang}`')
    return found


def lexicon(statement: str, lang: str) -> list[str]:
    """L-12 and L-13 — the judgement words, and the two shapes that carry one
    without being a word: a superlative, and an exclamation mark."""
    found = [f'L-12 evaluative term "{term}" in `{lang}`' for term in hits(statement, EVALUATIVE[lang])]
    found += [f'L-12 value verb "{term}" in `{lang}`' for term in hits(statement, VALUE_VERBS[lang])]
    found += [f'L-12 intensifier "{term}" in `{lang}`' for term in hits(statement, INTENSIFIERS[lang])]
    found += [f'L-13 superlative "{term}" in `{lang}`' for term in hits(statement, SUPERLATIVES[lang])]
    if "!" in statement:
        found.append(f"L-13 exclamation mark in `{lang}`")
    return found


def quantifiers(statement: str, lang: str, basis: str | None, span: str) -> list[str]:
    """L-14 — a quantifier holds only if the document quantifies too."""
    supported = basis == "text"
    return [
        f'L-14 unsupported quantifier "{term}" in `{lang}`'
        for term in hits(statement, QUANTIFIERS[lang])
        if not (supported and hits(span, (term,)))
    ]


def certainty(statement: str, lang: str, basis: str | None) -> list[str]:
    """L-15 and L-16 — a deduction is written as a deduction.

    Uncertainty is carried by the wording because DP-31 refused to carry it by a
    label or a score: a model producing a confidence figure could not justify it.
    """
    if basis != "inferred":
        return []
    found = []
    if not hits(statement, UNCERTAINTY[lang]):
        found.append(f"L-15 inferred statement without an uncertainty marker in `{lang}`")
    found += [f'L-16 assertive form "{term}" in an inferred statement in `{lang}`' for term in hits(statement, ASSERTIVE[lang])]
    return found


def figures(statement: str, lang: str, basis: str | None, span: str) -> list[str]:
    """L-17 — a figure comes from the document or it does not appear."""
    return [
        f'L-17 figure "{number}" not found in the span, in `{lang}`'
        for number in re.findall(r"\d+", statement)
        if basis != "text" or number not in span
    ]
