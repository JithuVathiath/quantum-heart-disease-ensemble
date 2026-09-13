"""Licensed UCI Heart Disease acquisition, parsing, and profiling."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

DATASET_URL = "https://archive.ics.uci.edu/static/public/45/heart+disease.zip"
DATASET_DOI = "10.24432/C52P4X"
DATASET_LICENSE = "CC BY 4.0"

FEATURES = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
)
TARGET = "num"
COLUMNS = (*FEATURES, TARGET)

COHORT_FILES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "long-beach-va": "processed.va.data",
}

CATEGORICAL_FEATURES = ("sex", "cp", "fbs", "restecg", "exang", "slope", "thal")
NUMERIC_FEATURES = tuple(name for name in FEATURES if name not in CATEGORICAL_FEATURES)
CROSS_COHORT_FEATURES = tuple(name for name in FEATURES if name not in {"ca", "thal"})


@dataclass(frozen=True)
class DataManifest:
    dataset_doi: str
    licence: str
    source_url: str
    archive_sha256: str
    files: dict[str, str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_extract(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            member_path = (destination / member.filename).resolve()
            if destination not in member_path.parents and member_path != destination:
                raise ValueError(f"Unsafe archive member: {member.filename}")
        bundle.extractall(destination)


def acquire_dataset(data_root: str | Path, *, url: str = DATASET_URL) -> DataManifest:
    """Download and extract the official archive, then record exact file hashes."""

    root = Path(data_root)
    raw_dir = root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / "heart-disease.zip"
    if not archive.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "qheart-research/0.1"})
        with urllib.request.urlopen(request, timeout=60) as response:
            archive.write_bytes(response.read())
    extracted = raw_dir / "uci-heart-disease"
    extracted.mkdir(exist_ok=True)
    _safe_extract(archive, extracted)

    hashes: dict[str, str] = {}
    for cohort, filename in COHORT_FILES.items():
        matches = list(extracted.rglob(filename))
        if len(matches) != 1:
            raise FileNotFoundError(f"Expected exactly one {filename}, found {len(matches)}")
        hashes[cohort] = sha256_file(matches[0])

    manifest = DataManifest(
        dataset_doi=DATASET_DOI,
        licence=DATASET_LICENSE,
        source_url=url,
        archive_sha256=sha256_file(archive),
        files=hashes,
    )
    (root / "manifest.json").write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def _find_cohort_file(data_root: Path, cohort: str) -> Path:
    try:
        filename = COHORT_FILES[cohort]
    except KeyError as exc:
        raise ValueError(f"Unknown cohort: {cohort}") from exc
    matches = list((data_root / "raw" / "uci-heart-disease").rglob(filename))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Could not locate {filename}. Run `qheart data download --data-dir {data_root}` first."
        )
    return matches[0]


def load_cohort(data_root: str | Path, cohort: str) -> pd.DataFrame:
    """Load one processed UCI cohort and derive a binary target."""

    path = _find_cohort_file(Path(data_root), cohort)
    frame = pd.read_csv(path, names=COLUMNS, na_values="?", dtype=str)
    if frame.shape[1] != len(COLUMNS):
        raise ValueError(f"Unexpected column count for {cohort}: {frame.shape[1]}")
    for column in COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=[TARGET]).copy()
    frame["target"] = (frame[TARGET] > 0).astype(int)
    frame["cohort"] = cohort
    frame["row_id"] = [f"{cohort}-{index:04d}" for index in range(len(frame))]
    if frame["target"].nunique() != 2:
        raise ValueError(f"Expected a binary target after transformation for {cohort}")
    return frame


def load_all_cohorts(data_root: str | Path) -> dict[str, pd.DataFrame]:
    return {cohort: load_cohort(data_root, cohort) for cohort in COHORT_FILES}


def profile_cohort(frame: pd.DataFrame) -> dict[str, Any]:
    feature_frame = frame.loc[:, FEATURES]
    missing = feature_frame.isna().sum().sort_values(ascending=False)
    duplicated_features = int(frame.duplicated(subset=[*FEATURES, TARGET]).sum())
    return {
        "cohort": str(frame["cohort"].iloc[0]),
        "rows": len(frame),
        "positive_rows": int(frame["target"].sum()),
        "positive_rate": round(float(frame["target"].mean()), 6),
        "duplicate_rows": duplicated_features,
        "missing_cells": int(feature_frame.isna().sum().sum()),
        "missing_by_feature": {key: int(value) for key, value in missing.items()},
    }


def public_data_profile(cohorts: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Create aggregate, non-row-level data evidence safe for publication."""

    profiles = [profile_cohort(frame) for frame in cohorts.values()]
    return {
        "dataset_doi": DATASET_DOI,
        "licence": DATASET_LICENSE,
        "cohorts": profiles,
        "total_rows": sum(item["rows"] for item in profiles),
        "feature_count": len(FEATURES),
    }

