"""Validate that the committed explorer artefact is aggregate and internally consistent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def walk_keys(value: object) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key in value] + [
            nested for item in value.values() for nested in walk_keys(item)
        ]
    if isinstance(value, list):
        return [nested for item in value for nested in walk_keys(item)]
    return []


def validate(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fingerprint = payload.pop("artefact_sha256", None)
    if not fingerprint or fingerprint != canonical_hash(payload):
        raise ValueError(f"Invalid artefact fingerprint in {path}")
    prohibited = {"row_id", "patient_id", "patient_rows", "raw_records"}
    exposed = prohibited.intersection(walk_keys(payload))
    if exposed:
        raise ValueError(f"Patient-level fields found in public artefact: {sorted(exposed)}")
    if payload.get("publication_context", {}).get("reported_accuracy") != 0.9016:
        raise ValueError("The historical paper result boundary is missing")
    if len(payload.get("leaderboard", [])) < 8:
        raise ValueError("The expected complete benchmark leaderboard is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        validate(path)
        print(f"Validated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

