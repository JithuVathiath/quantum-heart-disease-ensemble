"""Copy the aggregate benchmark artefact into the static evidence explorer."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="artifacts/public/results.json")
    parser.add_argument("--destination", default="apps/explorer/public/results.json")
    args = parser.parse_args()
    source = Path(args.source)
    destination = Path(args.destination)
    payload = json.loads(source.read_text(encoding="utf-8"))
    required = {"artefact_sha256", "leaderboard", "dataset", "quantum_diagnostics"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Public result artefact is missing: {sorted(missing)}")
    if any("row_id" in key for key in _walk_keys(payload)):
        raise ValueError("Patient-level row identifiers must not enter the public explorer")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    print(f"Synced {payload['artefact_sha256']} to {destination}")
    return 0


def _walk_keys(value: object) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key in value] + [
            nested for item in value.values() for nested in _walk_keys(item)
        ]
    if isinstance(value, list):
        return [nested for item in value for nested in _walk_keys(item)]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
