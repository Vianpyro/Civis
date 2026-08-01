"""Download declared source documents, fingerprint them, report what moved.

The .sha256 file is the diffable artifact: one line, `<digest>  <url>`. When a
party republishes a PDF the digest changes and git shows exactly one changed
line in one file. That diff is the transparency claim, so it is committed.

The documents themselves are not committed (binary, large, republished often);
they live in .cache/ and are re-fetched by CI before every check.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
UA = "civis-pipeline/0.1 (+https://github.com/Vianpyro/Civis)"


def sources_path(election: str) -> Path:
    return ROOT / "content" / "sources" / election / "sources.json"


def load_sources(election: str) -> list[dict]:
    return json.loads(sources_path(election).read_text(encoding="utf-8"))


def digest_file(election: str, source_id: str) -> Path:
    return ROOT / "content" / "sources" / election / f"{source_id}.sha256"


def cached_file(election: str, source_id: str, media_type: str) -> Path:
    ext = "pdf" if "pdf" in media_type else "html"
    return CACHE / election / f"{source_id}.{ext}"


def read_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").split()[0]


def fetch_one(election: str, source: dict) -> dict:
    """Download one source, write its cache file and .sha256. Returns a status dict."""
    url = source["url"]
    response = requests.get(url, timeout=60, headers={"User-Agent": UA})
    response.raise_for_status()

    body = response.content
    digest = hashlib.sha256(body).hexdigest()
    media_type = response.headers.get("content-type", "")

    cache = cached_file(election, source["id"], media_type)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(body)

    target = digest_file(election, source["id"])
    previous = read_digest(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"{digest}  {url}\n", encoding="utf-8")

    if previous is None:
        status = "new"
    elif previous != digest:
        status = "changed"
    else:
        status = "unchanged"
    return {"id": source["id"], "status": status, "bytes": len(body), "digest": digest}


def fetch_all(election: str) -> list[dict]:
    results = []
    for source in load_sources(election):
        try:
            results.append(fetch_one(election, source))
        except Exception as error:  # noqa: BLE001 - one bad host must not stop the run
            results.append({"id": source["id"], "status": "error", "error": str(error)})
    return results


def main(election: str) -> int:
    results = fetch_all(election)
    for result in results:
        detail = result.get("error", f"{result.get('bytes', 0)} bytes")
        print(f"{result['status']:>9}  {result['id']}  {detail}")
    moved = [r for r in results if r["status"] in ("new", "changed")]
    if moved:
        print(f"\n{len(moved)} document(s) moved. Re-run extraction and review the questions.")
    return 1 if any(r["status"] == "error" for r in results) else 0
