from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from utils import append_log


@dataclass
class HermesResult:
    stdout: str
    stderr: str
    exit_code: int


def run_hermes(
    command_template: str,
    hermes_command: str,
    prompt_file: Path,
    logs_dir: Path,
) -> HermesResult:
    cmd = command_template.format(
        hermes_command=hermes_command,
        prompt_file=str(prompt_file).replace('\\', '/'),
    )
    append_log(logs_dir / "hermes_runner.log", f"cmd={cmd}")

    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        append_log(logs_dir / "hermes_runner.log", f"ERROR exit={proc.returncode} stderr={proc.stderr.strip()}")

    return HermesResult(
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        exit_code=proc.returncode,
    )
