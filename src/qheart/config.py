"""Typed experiment configuration and deterministic fingerprints."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration that fully identifies a benchmark protocol."""

    schema_version: int = 1
    experiment_id: str = "cleveland-reference-v1"
    seed: int = 20250913
    folds: int = 5
    bootstrap_samples: int = 1000
    quantum_features: int = 4
    quantum_feature_map_reps: int = 2
    quantum_entanglement: str = "linear"
    bagging_estimators: int = 7
    minimum_subgroup_size: int = 25
    cohorts: tuple[str, ...] = (
        "cleveland",
        "hungarian",
        "switzerland",
        "long-beach-va",
    )

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("Only configuration schema version 1 is supported")
        if self.folds < 2:
            raise ValueError("folds must be at least 2")
        if self.bootstrap_samples < 100:
            raise ValueError("bootstrap_samples must be at least 100")
        if self.quantum_features < 2:
            raise ValueError("quantum_features must be at least 2")
        if self.bagging_estimators < 1:
            raise ValueError("bagging_estimators must be positive")
        if self.quantum_entanglement not in {"linear", "full", "circular"}:
            raise ValueError("Unsupported quantum entanglement pattern")

    @classmethod
    def from_json(cls, path: str | Path) -> ExperimentConfig:
        payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        if "cohorts" in payload:
            payload["cohorts"] = tuple(payload["cohorts"])
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["cohorts"] = list(self.cohorts)
        return payload

    @property
    def fingerprint(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
