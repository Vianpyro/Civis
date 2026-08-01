"""Draft questions from extracted program points, one Claude batch job per run.

This never runs at request time and never writes into content/questions/. It
writes a draft to review/, a human reads every question against its quote, and
only then does the reviewed file get committed. The batch API is the right shape
here: the work is offline, bulk, and not latency-sensitive.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .extract import cached_text, candidates
from .fetch import ROOT, load_sources

MODEL = "claude-opus-5"
POINTS_PER_SOURCE = 40

SYSTEM = """Tu transformes des extraits de programmes politiques officiels en \
questions neutres pour un questionnaire à l'aveugle.

Règles absolues :
- La question ne doit contenir aucun nom de parti, de personnalité, de \
mouvement, ni aucun marqueur lexical propre à un camp politique.
- La question porte sur UNE mesure concrète et vérifiable, formulée à la \
première personne du pluriel du point de vue de l'électeur ("Faut-il ...").
- Le champ `quote` doit reproduire À L'IDENTIQUE un fragment de l'extrait \
fourni, sans reformulation, sans coupure au milieu d'un mot.
- Si un extrait n'exprime pas une mesure vérifiable, ne produis pas de question \
pour cet extrait.
- Rends un tableau JSON et rien d'autre."""

SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string",
                        "enum": [
                            "economy",
                            "social",
                            "ecology",
                            "institutions",
                            "security",
                            "immigration",
                            "europe",
                            "education",
                            "health",
                        ],
                    },
                    "text_fr": {"type": "string"},
                    "text_en": {"type": "string"},
                    "quote": {"type": "string"},
                    "stance": {"type": "integer", "enum": [-1, 1]},
                },
                "required": ["theme", "text_fr", "text_en", "quote", "stance"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}


def build_requests(election: str) -> list[dict]:
    """One batch request per source, each carrying that source's candidates."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    requests_ = []
    for source in load_sources(election):
        text = cached_text(election, source["id"])
        if text is None:
            continue
        points = candidates(text)[:POINTS_PER_SOURCE]
        if not points:
            continue
        listing = "\n".join(f"{i}. {p}" for i, p in enumerate(points))
        requests_.append(
            Request(
                custom_id=source["id"],
                params=MessageCreateParamsNonStreaming(
                    model=MODEL,
                    max_tokens=16000,
                    system=SYSTEM,
                    thinking={"type": "adaptive"},
                    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                f"Document : {source['title']}\n\n"
                                f"Extraits :\n{listing}\n\n"
                                "Produis une question par extrait exploitable."
                            ),
                        }
                    ],
                ),
            )
        )
    return requests_


def main(election: str) -> int:
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        print("no Anthropic credentials in the environment; skipping generation")
        return 0

    import anthropic

    client = anthropic.Anthropic()
    requests_ = build_requests(election)
    if not requests_:
        print("nothing to generate (run fetch first)")
        return 0

    batch = client.messages.batches.create(requests=requests_)
    print(f"batch {batch.id}: {len(requests_)} request(s)")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        time.sleep(30)

    drafts: dict[str, list] = {}
    for result in client.messages.batches.results(batch.id):
        if result.result.type != "succeeded":
            print(f"  {result.custom_id}: {result.result.type}")
            continue
        message = result.result.message
        payload = next(b.text for b in message.content if b.type == "text")
        drafts[result.custom_id] = json.loads(payload)["questions"]

    out = ROOT / "review" / f"{election}-draft.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(drafts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(len(v) for v in drafts.values())
    print(f"wrote {total} draft question(s) to {out.relative_to(ROOT)} — review before committing")
    return 0
