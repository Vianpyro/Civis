"""The single boundary between Civis and an LLM provider (DT-29, DT-31).

No other module builds an HTTP request, knows an API URL, a model identifier or
the shape of a provider's answer. That is the whole decision: changing provider
means rewriting the function below, not threading a new type through the
pipeline. And what makes such a change safe is not an adapter — it is the linter
running in CI on the committed content (DT-29, INV-21).

Configuration, not abstraction: two constants overridable by the environment and
a dict of providers. There is no interface, no class and no dependency
inversion, and a second provider costs one function and one line.

generate.py is deliberately not migrated here (DT-31): it drafts questions
against Anthropic and that is a separate concern from this feature.
"""

from __future__ import annotations

import json
import os
import time

import requests

PROVIDER = os.environ.get("CIVIS_LLM_PROVIDER", "gemini")
MODEL = os.environ.get("CIVIS_LLM_MODEL", "gemini-2.5-pro")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

TIMEOUT = 180
ATTEMPTS = 4
BACKOFF = 5  # seconds, multiplied by the attempt number


def post(url: str, body: dict, headers: dict) -> dict:
    """One POST, retrying 429 and 5xx with a linear backoff.

    Written by hand, once, here: it is the assumed cost of calling an HTTP API
    without an SDK (DT-31). Any other status is raised — a 400 is a defect in
    the request, not weather, and retrying it only wastes the quota.
    """
    for attempt in range(1, ATTEMPTS + 1):
        response = requests.post(url, json=body, headers=headers, timeout=TIMEOUT)
        if (response.status_code == 429 or response.status_code >= 500) and attempt < ATTEMPTS:
            time.sleep(BACKOFF * attempt)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("unreachable: the loop above returns or raises")


def openapi(schema: object) -> object:
    """The output schema, in the subset Gemini accepts.

    Gemini's `responseSchema` is OpenAPI-flavoured and rejects the
    `additionalProperties` that the strict schema of the DP carries. Dropping it
    belongs here rather than in impacts.py, so that the schema written there
    stays the one the DP writes.
    """
    if isinstance(schema, dict):
        return {key: openapi(value) for key, value in schema.items() if key != "additionalProperties"}
    if isinstance(schema, list):
        return [openapi(item) for item in schema]
    return schema


def gemini(request: dict, key: str) -> dict:
    body = {
        "systemInstruction": {"parts": [{"text": request["system"]}]},
        "contents": [{"role": "user", "parts": [{"text": request["user"]}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": openapi(request["schema"]),
        },
    }
    answer = post(GEMINI_URL.format(model=MODEL), body, {"x-goog-api-key": key})
    parts = answer["candidates"][0]["content"]["parts"]
    return json.loads("".join(part.get("text", "") for part in parts))


PROVIDERS = {
    "gemini": {"call": gemini, "env": ("GEMINI_API_KEY", "GOOGLE_API_KEY")},
}


def provider(name: str | None = None) -> dict:
    """Fails immediately, naming the provider: a typo in the environment must not
    read as "no credentials" and silently skip the step."""
    name = name or PROVIDER
    if name not in PROVIDERS:
        raise ValueError(f"unknown LLM provider {name!r} (known: {', '.join(sorted(PROVIDERS))})")
    return PROVIDERS[name]


def api_key() -> str | None:
    for variable in provider()["env"]:
        value = os.environ.get(variable)
        if value:
            return value
    return None


def configured() -> bool:
    """Whether a call can be made at all. The caller never learns which variable
    carries the credential, which is the point of this module."""
    return api_key() is not None


def run_batch(requests_: list[dict]) -> dict[str, dict]:
    """Answers keyed by `custom_id` — the one call point of the pipeline (DT-29).

    A request is `{custom_id, system, user, schema}` and an answer is the parsed
    JSON object: neither the caller nor the callee shares anything else.

    Synchronous loop: DT-31 admits it explicitly, and a pilot of four points does
    not justify a batch API. A failing point is reported and skipped rather than
    losing the others — a draft is a review artefact, not a transaction.
    """
    call = provider()["call"]
    key = api_key()
    answers: dict[str, dict] = {}
    for request in requests_:
        try:
            answers[request["custom_id"]] = call(request, key)
        except Exception as error:  # noqa: BLE001 - one bad point must not stop the run
            print(f"  {request['custom_id']}: {error}")
    return answers
