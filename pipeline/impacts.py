"""Two passes over the consequences of a measure, blind and offline (DP-35, DP-36).

Pass 1 proposes, pass 2 signals, and neither decides: this module writes into
review/ and nowhere else (INV-23), and a human reads every statement against its
quote before anything reaches content/.

Blindness is structural rather than promised. Nothing a party name, a party id
or a document title could be read from reaches a request: what the model gets is
a theme, the quote, a window of the document around it and the closed
vocabulary. The `custom_id` carries the point id, and a point id carries a party
prefix, so it is never part of the message body (DP-35). The one place party
labels are read is `party_labels`, used only to lint an answer that already came
back — never to compose a request, which is what A-9 checks.

Pass 2 never sees the prompt of pass 1 (DP-36): the two prompts are two
constants that share no text, because an auditor who knows the rule rationalises
its violation. It annotates every statement and removes none — a filtered draft
would hide the drift of the prompt, which is precisely what a review is for.
"""

from __future__ import annotations

import json

from . import llm, neutrality
from .check import ELECTION, GROUPS, quote_digest
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

# Pass 2 (§9.2). Written out in full rather than assembled from the constants
# above: sharing a single line between the two prompts is the natural way to
# break DP-36, and the audit must not be able to infer what pass 1 was told.
AUDIT_SYSTEM = """Tu vérifies des énoncés produits par un autre système. Tu ne \
les réécris pas, tu les juges un par un. Tu ne connais pas les consignes suivies \
pour les produire et tu ne dois pas les supposer.

Verdicts possibles :
- ok          : descriptif, soutenu, sans jugement
- evaluative  : jugement de valeur, verbe de valeur, terme connoté,
                intensificateur
- speculative : présenté comme certain sans être écrit dans le document, ou
                rédigé au futur de l'indicatif
- unsupported : basis "text", mais le span ne soutient pas l'énoncé
- overgeneral : généralisation ou quantification sans support textuel
- partisan    : marqueur de camp, parti, personnalité, mouvement
- offtopic    : ne découle pas de la mesure citée

`evidence` : le fragment exact de l'énoncé qui motive le verdict, ou "" si ok.

Dans le doute, tu signales. Un faux signalement coûte une lecture ; un
signalement manqué coûte la neutralité du produit."""

AUDIT_USER = """Mesure :
« {quote} »

Contexte du document :
{context}

Énoncés à juger, numérotés à partir de 0 :
{statements}"""

VERDICTS = ["ok", "evaluative", "speculative", "unsupported", "overgeneral", "partisan", "offtopic"]

AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "verdict": {"type": "string", "enum": VERDICTS},
                    "evidence": {"type": "string"},
                },
                "required": ["index", "verdict", "evidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
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


def committed(election: str) -> dict[str, dict]:
    """The analyses already reviewed and committed.

    The cache is the committed file (DT-24): there is no cache layer to build and
    none to invalidate, and what expires an entry is visible in a diff.
    """
    path = ROOT / "content" / "impacts" / f"{election}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("impacts", {})


def party_labels(election: str) -> list[dict]:
    """Party blocks, read for one purpose only: L-11 on an answer that already
    came back. No request is composed from them — build_requests reads a unit and
    nothing else, and A-9 checks that from the outside."""
    return [
        json.loads(path.read_text(encoding="utf-8"))["party"]
        for path in sorted((ROOT / "content" / "programs" / election).glob("*.json"))
    ]


def units(election: str, limit: int | None = None, force: bool = False) -> list[dict]:
    """One unit per point referenced by positions.json, in file order (DT-24).

    A point that is never displayed does not need an analysis, a point whose
    document is not cached or whose quote cannot be located is skipped rather
    than sent without its context, and a point whose committed `of` still matches
    its quote is current — in steady state this returns nothing and the step
    calls no model at all (A-15). `--force` ignores that, `--limit` caps the
    number of points a single run pays for.
    """
    points = program_points(election)
    path = ROOT / "content" / "questions" / f"{election}.positions.json"
    positions = json.loads(path.read_text(encoding="utf-8"))
    done = {} if force else committed(election)

    seen: set[str] = set()
    skipped: list[str] = []
    current: list[str] = []
    out: list[dict] = []
    for entries in positions.values():
        for entry in entries:
            point_id = entry["point"]
            point = points.get(point_id)
            if point_id in seen or point is None:
                continue
            seen.add(point_id)
            if (done.get(point_id) or {}).get("of") == quote_digest(point["quote"]):
                current.append(point_id)
                continue
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
    if current:
        print(f"  skipped {len(current)} point(s): analysis up to date (--force to redraft)")
    return out[:limit] if limit else out


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


def numbered(items: list[dict]) -> str:
    """The statements as the auditor reads them: both languages, the kind, the
    basis and the span if there is one — and no trace of what produced them."""
    lines: list[str] = []
    for index, item in enumerate(items):
        lines.append(f"{index}. [{item.get('kind')} / {item.get('basis')}]")
        lines.append(f"   fr : {item.get('fr', '')}")
        lines.append(f"   en : {item.get('en', '')}")
        if item.get("span"):
            lines.append(f"   span : « {item['span']} »")
    return "\n".join(lines)


def audit_requests(drafts: dict[str, dict]) -> list[dict]:
    """One pass 2 request per drafted point (DT-24), on what pass 1 answered.

    The body carries the measure, the document window and the statements. Not the
    instructions pass 1 followed (DP-36), and not the point id, which the
    `custom_id` carries as in pass 1.
    """
    return [
        {
            "custom_id": point_id,
            "system": AUDIT_SYSTEM,
            "user": AUDIT_USER.format(
                quote=draft["quote"],
                context=draft["context"],
                statements=numbered(draft["items"]),
            ),
            "schema": AUDIT_SCHEMA,
        }
        for point_id, draft in drafts.items()
        if draft["items"]
    ]


def annotate(drafts: dict[str, dict], verdicts: dict[str, dict], parties: list[dict]) -> None:
    """`lint` and `audit` on every statement, and on every statement produced.

    The two annotations orient the reading, they do not replace it (§8): a
    statement marked `ok` can still be refused. Nothing is dropped here — a
    filtered draft would hide a systematic drift of the prompt, which is the one
    thing a review needs to see (DP-36).
    """
    for point_id, draft in drafts.items():
        by_index = {
            verdict.get("index"): verdict
            for verdict in verdicts.get(point_id, {}).get("verdicts", [])
        }
        for index, item in enumerate(draft["items"]):
            # The lexicon on the statements only: a span is the document speaking
            # (INV-21). Same module as CI, never a second copy (DT-26).
            item["lint"] = neutrality.violations(item, parties)
            # None when pass 2 said nothing about this statement — an absence
            # that reads as an absence rather than as a verdict it never gave.
            item["audit"] = by_index.get(index)


def main(election: str = ELECTION, limit: int | None = None, force: bool = False) -> int:
    # No credentials, no failure: CI never depends on a model call. Same shape as
    # generate.py, for the same reason.
    if not llm.configured():
        print("no LLM credentials in the environment; skipping impact drafting")
        return 0

    units_ = units(election, limit=limit, force=force)
    if not units_:
        print("nothing to draft: no point is out of date (run fetch first if the cache is empty)")
        return 0

    print(f"{len(units_)} point(s) to draft with {llm.MODEL}")
    answers = llm.run_batch(build_requests(units_))

    # Grouped by point, quote first, context next: the draft is read point by
    # point and that reading is the load-bearing filter (DP-36, R-5). `of` and
    # `model` travel with it, so the transfer into content/ stays a copy rather
    # than a computation done by hand.
    drafts = {
        unit["id"]: {
            "of": quote_digest(unit["quote"]),
            "model": llm.MODEL,
            "quote": unit["quote"],
            "context": unit["context"],
            "items": answers[unit["id"]].get("items", []),
        }
        for unit in units_
        if unit["id"] in answers
    }

    print(f"auditing {len(drafts)} point(s)")
    annotate(drafts, llm.run_batch(audit_requests(drafts)), party_labels(election))

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
