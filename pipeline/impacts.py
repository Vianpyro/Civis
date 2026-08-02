"""Pass 1: draft the consequences of a measure, blind and offline (DP-35, DP-36).

The generator proposes, it never decides: it writes into review/ and nowhere
else (INV-23), and a human reads every statement against its quote before
anything reaches content/.

Blindness is structural here rather than promised. This module never reads a
party name, a party id or a document title — it has no use for any of them. What
reaches the model is a theme, the quote, a window of the document around it and
the closed vocabulary. The `custom_id` carries the point id, and a point id
carries a party prefix, so it is never part of the message body (DP-35).
"""

from __future__ import annotations

import json

from . import llm
from .check import ELECTION, GROUPS
from .extract import cached_text, context
from .fetch import ROOT

VOCABULARY = sorted(GROUPS)

SYSTEM = """Tu décris les conséquences d'une mesure extraite d'un document \
officiel. Tu ne sais pas de quelle formation politique elle provient, tu ne dois \
pas le deviner et tu ne dois jamais l'évoquer.

Trois catégories d'énoncés :
- implication : ce que la mesure change mécaniquement — obligation, droit,
  restriction, procédure, règle fiscale ou réglementaire.
- affected : une catégorie de personnes ou d'organismes concernée, et en quoi.
  La catégorie est CHOISIE dans la liste fournie, jamais rédigée. Un énoncé
  porte exactement une catégorie. Si le document ne nomme pas le niveau de
  collectivité, emploie « local_authorities ».
- effect : un effet concret raisonnablement attendu.

Chaque énoncé porte un `basis` :
- "text"     : soutenu par le document. Tu fournis alors `span`, copié À
               L'IDENTIQUE depuis le contexte fourni, sans reformulation, sans
               coupure au milieu d'un mot, 300 caractères au plus.
- "inferred" : non écrit dans le document. Pas de `span`. Formulation
               obligatoirement conditionnelle.

Interdits absolus :
- terme évaluatif : bon, mauvais, juste, injuste, excellent, catastrophique,
  massif, historique, courageux, laxiste, généreux, indispensable, dérisoire,
  véritable, enfin ;
- verbe de valeur : aider, pénaliser, protéger, favoriser, défavoriser,
  sanctionner, nuire, récompenser, punir, améliorer, dégrader ;
- intensificateur : énormément, considérablement, dramatiquement, fortement,
  très, extrêmement, particulièrement ;
- jugement sur l'opportunité, l'efficacité, le coût politique ou le mérite ;
- chiffre absent du document ;
- scénario politique : élection, majorité, opposition, mandat, réaction ;
- superlatif, point d'exclamation ;
- « tous », « toutes », « aucun », « chaque », « toujours », « jamais »,
  « l'ensemble des » — sauf si le mot figure dans le span que tu fournis ;
- nom de parti, de personnalité, de mouvement, ou marqueur lexical de camp.

Un énoncé "inferred" emploie le conditionnel ou un marqueur d'incertitude
(« pourrait », « pourraient », « serait », « est susceptible de », « selon les
modalités retenues », « en fonction de »). Jamais le futur de l'indicatif.

Lorsque plusieurs effets sont plausibles, tu les énonces tous plutôt que d'en
choisir un.
Lorsque tu n'as pas de quoi produire un énoncé, tu n'en produis pas : un
tableau court est correct, un tableau inventé ne l'est pas.

Bornes, par mesure :
- 1 à 4 énoncés "implication", 1 à 5 énoncés "affected", 0 à 4 énoncés "effect" ;
- 10 énoncés au total au plus ;
- le nombre d'énoncés "inferred" ne dépasse jamais celui des énoncés "text" ;
- chaque énoncé fait 200 caractères au plus, en français comme en anglais, et
  les deux versions disent la même chose.

Rends du JSON conforme au schéma et rien d'autre."""

USER = """Thème : {theme}

Mesure :
« {quote} »

Contexte du document :
{context}

Catégories admises pour `who` :
{who_vocabulary}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["implication", "affected", "effect"]},
                    "basis": {"type": "string", "enum": ["text", "inferred"]},
                    "span": {"type": "string"},
                    "who": {"type": "string", "enum": VOCABULARY},
                    "directness": {"type": "string", "enum": ["direct", "indirect"]},
                    "fr": {"type": "string"},
                    "en": {"type": "string"},
                },
                # The conditionalities (`span` iff text, `who` iff affected) are
                # not expressed here: they would need a `oneOf` that strict API
                # schemas do not accept uniformly. The linter checks them, and it
                # is the opposable layer anyway.
                "required": ["kind", "basis", "fr", "en"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}


def program_points(election: str) -> dict[str, dict]:
    """Points by id, each with the source it comes from — never the party, never
    the document title: this module has no use for either (DP-35)."""
    points: dict[str, dict] = {}
    for path in sorted((ROOT / "content" / "programs" / election).glob("*.json")):
        program = json.loads(path.read_text(encoding="utf-8"))
        for point in program["points"]:
            points[point["id"]] = {**point, "source_id": program["source_id"]}
    return points


def units(election: str) -> list[dict]:
    """One unit per point referenced by positions.json, in file order (DT-24).

    A point that is never displayed does not need an analysis, and a point whose
    document is not cached or whose quote cannot be located is skipped rather
    than sent without its context.
    """
    points = program_points(election)
    path = ROOT / "content" / "questions" / f"{election}.positions.json"
    positions = json.loads(path.read_text(encoding="utf-8"))

    seen: set[str] = set()
    skipped: list[str] = []
    out: list[dict] = []
    for entries in positions.values():
        for entry in entries:
            point_id = entry["point"]
            point = points.get(point_id)
            if point_id in seen or point is None:
                continue
            seen.add(point_id)
            text = cached_text(election, point["source_id"])
            window = context(text, point["quote"]) if text is not None else ""
            if not window:
                skipped.append(point_id)
                continue
            out.append(
                {
                    "id": point_id,
                    "theme": point["theme"],
                    "quote": point["quote"],
                    "context": window,
                }
            )

    # Reported once with a count, not once per point: without a cache every point
    # is skipped, and a warning repeated forty-five times stops being read (DT-32).
    if skipped:
        print(f"  skipped {len(skipped)} point(s): document not cached, or quote not found in it")
    return out


def build_requests(units_: list[dict]) -> list[dict]:
    """The message body carries the theme, the quote, the document window and the
    vocabulary — and nothing else (DP-35, §9.1 of the DP)."""
    return [
        {
            "custom_id": unit["id"],
            "system": SYSTEM,
            "user": USER.format(
                theme=unit["theme"],
                quote=unit["quote"],
                context=unit["context"],
                who_vocabulary="\n".join(VOCABULARY),
            ),
            "schema": SCHEMA,
        }
        for unit in units_
    ]


def main(election: str = ELECTION) -> int:
    # No credentials, no failure: CI never depends on a model call. Same shape as
    # generate.py, for the same reason.
    if not llm.configured():
        print("no LLM credentials in the environment; skipping impact drafting")
        return 0

    units_ = units(election)
    if not units_:
        print("nothing to draft (run fetch first)")
        return 0

    print(f"{len(units_)} point(s) to draft with {llm.MODEL}")
    answers = llm.run_batch(build_requests(units_))

    # Grouped by point, quote first, context next: the draft is read point by
    # point and that reading is the load-bearing filter (DP-36, R-5).
    drafts = {
        unit["id"]: {
            "quote": unit["quote"],
            "context": unit["context"],
            "model": llm.MODEL,
            "items": answers[unit["id"]].get("items", []),
        }
        for unit in units_
        if unit["id"] in answers
    }

    # The one write path of this module (INV-23). Nothing here writes to content/:
    # the transfer is a human gesture.
    out = ROOT / "review" / f"{election}-impacts-draft.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(drafts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    statements = sum(len(draft["items"]) for draft in drafts.values())
    print(
        f"wrote {statements} statement(s) over {len(drafts)} point(s) to "
        f"{out.relative_to(ROOT)} — review before committing"
    )
    return 0
