"""Command-line interface for data and benchmark workflows."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from qheart.benchmark import generate_public_outputs
from qheart.data import acquire_dataset, load_all_cohorts, public_data_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qheart", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    data = commands.add_parser("data", help="Acquire or profile the licensed UCI data")
    data_commands = data.add_subparsers(dest="data_command", required=True)
    download = data_commands.add_parser("download", help="Download and verify the official archive")
    download.add_argument("--data-dir", default="data")
    profile = data_commands.add_parser("profile", help="Print a public aggregate data profile")
    profile.add_argument("--data-dir", default="data")

    benchmark = commands.add_parser("benchmark", help="Run the versioned reference benchmark")
    benchmark.add_argument("--data-dir", default="data")
    benchmark.add_argument("--config", default="configs/reference.json")
    benchmark.add_argument("--output", default="artifacts/public/results.json")
    benchmark.add_argument("--report", default="reports/results.md")
    benchmark.add_argument(
        "--classical-only",
        action="store_true",
        help="Skip the optional quantum track for a faster local check",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "data" and args.data_command == "download":
        manifest = acquire_dataset(args.data_dir)
        print(json.dumps(manifest.__dict__, indent=2, sort_keys=True))
        return 0
    if args.command == "data" and args.data_command == "profile":
        profile = public_data_profile(load_all_cohorts(args.data_dir))
        print(json.dumps(profile, indent=2, sort_keys=True))
        return 0
    if args.command == "benchmark":
        payload = generate_public_outputs(
            args.data_dir,
            args.config,
            args.output,
            args.report,
            include_quantum=not args.classical_only,
        )
        output = Path(args.output).resolve()
        print(f"Wrote {output} ({payload['artefact_sha256']})")
        return 0
    raise AssertionError("Unhandled command")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

