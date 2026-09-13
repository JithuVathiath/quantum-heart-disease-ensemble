from __future__ import annotations

import json
import zipfile

import pytest

from qheart.data import (
    COHORT_FILES,
    _safe_extract,
    acquire_dataset,
    load_cohort,
    profile_cohort,
    public_data_profile,
    sha256_file,
)


def sample_row(target: object = 0) -> list[object]:
    return [63, 1, 1, 145, 233, 1, 2, 150, 0, 2.3, 3, 0, 6, target]


def test_load_cohort_parses_missing_values_and_binary_target(tmp_path, cohort_writer) -> None:
    cohort_writer(
        COHORT_FILES["cleveland"],
        [sample_row(0), sample_row(2), [41, 0, 2, 130, "?", 0, 0, 180, 0, 0, 1, 0, 3, 1]],
    )
    frame = load_cohort(tmp_path, "cleveland")
    assert frame["target"].tolist() == [0, 1, 1]
    assert frame["chol"].isna().sum() == 1
    assert frame["row_id"].is_unique
    profile = profile_cohort(frame)
    assert profile["rows"] == 3
    assert profile["missing_cells"] == 1


def test_profile_is_aggregate_and_serialisable(tmp_path, cohort_writer) -> None:
    cohort_writer(COHORT_FILES["cleveland"], [sample_row(0), sample_row(1)])
    frame = load_cohort(tmp_path, "cleveland")
    payload = public_data_profile({"cleveland": frame})
    assert payload["total_rows"] == 2
    assert "row_id" not in json.dumps(payload)


def test_unknown_or_missing_cohort_is_clear(tmp_path) -> None:
    with pytest.raises(ValueError, match="Unknown cohort"):
        load_cohort(tmp_path, "moon")
    with pytest.raises(FileNotFoundError, match="Run `qheart data download"):
        load_cohort(tmp_path, "cleveland")


def test_hash_is_stable(tmp_path) -> None:
    path = tmp_path / "value.txt"
    path.write_text("heart\n", encoding="utf-8")
    assert sha256_file(path) == sha256_file(path)
    assert len(sha256_file(path)) == 64


def test_safe_extract_rejects_path_traversal(tmp_path) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape.txt", "unsafe")
    with pytest.raises(ValueError, match="Unsafe archive member"):
        _safe_extract(archive, tmp_path / "destination")


def test_acquire_dataset_from_archive_records_hashes(tmp_path) -> None:
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as bundle:
        for filename in COHORT_FILES.values():
            bundle.writestr(filename, ",".join(str(value) for value in sample_row(0)) + "\n")
    destination = tmp_path / "dataset"
    manifest = acquire_dataset(destination, url=source.as_uri())
    assert set(manifest.files) == set(COHORT_FILES)
    assert len(manifest.archive_sha256) == 64
    assert (destination / "manifest.json").exists()


def test_acquire_uses_existing_archive(tmp_path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    archive = raw / "heart-disease.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for filename in COHORT_FILES.values():
            bundle.writestr(filename, ",".join(str(value) for value in sample_row(0)) + "\n")
    manifest = acquire_dataset(tmp_path, url="https://invalid.example/not-used.zip")
    assert manifest.source_url.endswith("not-used.zip")
