from __future__ import annotations

from qheart import cli
from qheart.data import DataManifest


def test_data_download_command(monkeypatch, capsys) -> None:
    manifest = DataManifest("doi", "licence", "url", "hash", {"cleveland": "file-hash"})
    monkeypatch.setattr(cli, "acquire_dataset", lambda path: manifest)
    assert cli.main(["data", "download", "--data-dir", "ignored"]) == 0
    assert '"archive_sha256": "hash"' in capsys.readouterr().out


def test_data_profile_command(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "load_all_cohorts", lambda path: {"cohort": object()})
    monkeypatch.setattr(cli, "public_data_profile", lambda cohorts: {"total_rows": 10})
    assert cli.main(["data", "profile", "--data-dir", "ignored"]) == 0
    assert '"total_rows": 10' in capsys.readouterr().out


def test_benchmark_command(monkeypatch, capsys, tmp_path) -> None:
    output = tmp_path / "result.json"

    def generate(*args, **kwargs):
        return {"artefact_sha256": "abc123"}

    monkeypatch.setattr(cli, "generate_public_outputs", generate)
    result = cli.main(
        [
            "benchmark",
            "--output",
            str(output),
            "--classical-only",
        ]
    )
    assert result == 0
    assert "abc123" in capsys.readouterr().out
