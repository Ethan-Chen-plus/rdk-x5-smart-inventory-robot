from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if not files:
        raise FileNotFoundError(f"checkpoint contains no files: {root}")
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def command_output(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture auditable SmolVLA deployment metadata.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--dataset-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.dataset_report.read_text(encoding="utf-8"))
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "nvidia_smi": command_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ]
        ),
        "checkpoint": str(args.checkpoint.resolve()),
        "checkpoint_sha256_tree": sha256_tree(args.checkpoint),
        "dataset_repo_id": report["repo_id"],
        "dataset_episode_count": len(report["episodes"]),
        "dataset_frame_count": sum(row["frames"] for row in report["episodes"]),
        "dataset_task_counts": report["task_counts"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
