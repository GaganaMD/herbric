from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from utils import append_log, ensure_dir


@dataclass
class FabricResult:
    chunk_id: int
    pattern: str
    stdout: str
    stderr: str
    exit_code: int
    output_file: Path


def run_fabric_on_chunk(
    chunk_id: int,
    chunk_text: str,
    patterns: List[str],
    fabric_command: str,
    command_template: str,
    outputs_dir: Path,
    logs_dir: Path,
    continue_on_error: bool = True,
) -> List[FabricResult]:
    ensure_dir(outputs_dir)
    ensure_dir(logs_dir)

    results: List[FabricResult] = []

    for pattern in patterns:
        cmd = command_template.format(
            fabric_command=fabric_command,
            pattern=shlex.quote(pattern),
        )
        append_log(logs_dir / "fabric_runner.log", f"chunk={chunk_id} pattern={pattern} cmd={cmd}")

        proc = subprocess.run(
            cmd,
            input=chunk_text,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            capture_output=True,
        )

        out_file = outputs_dir / f"chunk_{chunk_id:04d}__{pattern}.md"
        out_file.write_text(proc.stdout or "", encoding="utf-8")

        result = FabricResult(
            chunk_id=chunk_id,
            pattern=pattern,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            exit_code=proc.returncode,
            output_file=out_file,
        )
        results.append(result)

        if proc.returncode != 0:
            append_log(
                logs_dir / "fabric_runner.log",
                f"ERROR chunk={chunk_id} pattern={pattern} exit={proc.returncode} stderr={proc.stderr.strip()}",
            )
            if not continue_on_error:
                raise RuntimeError(f"Fabric failed on chunk {chunk_id}, pattern {pattern}: {proc.stderr}")

    return results


def summarize_fabric_results(results: List[FabricResult]) -> Dict[str, int]:
    total = len(results)
    failed = sum(1 for r in results if r.exit_code != 0)
    return {"total_runs": total, "failed_runs": failed, "successful_runs": total - failed}
