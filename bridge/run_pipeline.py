from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from chunker import chunk_text
from fabric_runner import run_fabric_on_chunk, summarize_fabric_results, FabricResult
from hermes_runner import run_hermes
from utils import append_log, ensure_dir, load_config, resolve_path, write_text


def build_combined_context(
    chunks,
    fabric_results: List[FabricResult],
    include_raw_chunk_text: bool,
    include_pattern_headers: bool,
) -> str:
    by_chunk = {}
    for r in fabric_results:
        by_chunk.setdefault(r.chunk_id, []).append(r)

    lines: List[str] = ["# Combined Research Context", ""]

    for c in chunks:
        lines.append(f"## Chunk {c.chunk_id}")
        lines.append("")
        if include_raw_chunk_text:
            lines.append("### Source Excerpt")
            lines.append(c.text)
            lines.append("")

        for r in by_chunk.get(c.chunk_id, []):
            if include_pattern_headers:
                lines.append(f"### Pattern: {r.pattern}")
            if r.exit_code == 0 and r.stdout.strip():
                lines.append(r.stdout.strip())
            else:
                lines.append(f"[Pattern failed or empty output | exit_code={r.exit_code}]")
                if r.stderr.strip():
                    lines.append(f"stderr: {r.stderr.strip()}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fabric <-> Hermes bridge pipeline")
    parser.add_argument("--config", default="./bridge/config.yaml", help="Path to config YAML")
    args = parser.parse_args()

    cfg = load_config(args.config)
    base = Path(__file__).resolve().parent.parent

    input_file = resolve_path(cfg["paths"]["input_file"], base)
    output_dir = resolve_path(cfg["paths"]["output_dir"], base)
    combined_context_file = resolve_path(cfg["paths"]["combined_context_file"], base)
    fabric_outputs_dir = resolve_path(cfg["paths"]["fabric_outputs_dir"], base)
    logs_dir = resolve_path(cfg["paths"]["logs_dir"], base)

    ensure_dir(output_dir)
    ensure_dir(fabric_outputs_dir)
    ensure_dir(logs_dir)

    append_log(logs_dir / "pipeline.log", f"Starting pipeline with config={args.config}")
    append_log(logs_dir / "pipeline.log", f"Resolved input_file={input_file}")

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    source_text = input_file.read_text(encoding="utf-8")

    chunks = chunk_text(
        source_text,
        max_chars=int(cfg["chunking"]["max_chars"]),
        overlap_chars=int(cfg["chunking"].get("overlap_chars", 0)),
        preserve_paragraphs=bool(cfg["chunking"].get("preserve_paragraphs", True)),
    )
    append_log(logs_dir / "pipeline.log", f"Chunking complete: {len(chunks)} chunks")

    fabric_results: List[FabricResult] = []
    if cfg["fabric"].get("enabled", True):
        for c in chunks:
            results = run_fabric_on_chunk(
                chunk_id=c.chunk_id,
                chunk_text=c.text,
                patterns=cfg["fabric"]["patterns"],
                fabric_command=cfg["fabric"]["command"],
                command_template=cfg["fabric"]["command_template"],
                outputs_dir=fabric_outputs_dir,
                logs_dir=logs_dir,
                continue_on_error=bool(cfg["fabric"].get("continue_on_error", True)),
            )
            fabric_results.extend(results)

        summary = summarize_fabric_results(fabric_results)
        append_log(logs_dir / "pipeline.log", f"Fabric summary: {summary}")

    combined = build_combined_context(
        chunks=chunks,
        fabric_results=fabric_results,
        include_raw_chunk_text=bool(cfg["aggregation"].get("include_raw_chunk_text", False)),
        include_pattern_headers=bool(cfg["aggregation"].get("include_pattern_headers", True)),
    )
    write_text(combined_context_file, combined)
    append_log(logs_dir / "pipeline.log", f"Wrote combined context: {combined_context_file}")

    if cfg["hermes"].get("enabled", True):
        header = cfg["hermes"].get("final_prompt_header", "")
        prompt_file = output_dir / "hermes_prompt.txt"
        prompt_text = f"{header}\n\nUse this context:\n\n{combined}"
        write_text(prompt_file, prompt_text)

        hres = run_hermes(
            command_template=cfg["hermes"]["command_template"],
            hermes_command=cfg["hermes"]["command"],
            prompt_file=prompt_file,
            logs_dir=logs_dir,
        )

        final_file = output_dir / "hermes_final_output.md"
        write_text(final_file, hres.stdout)
        append_log(logs_dir / "pipeline.log", f"Hermes exit={hres.exit_code} output={final_file}")
        if hres.stderr.strip():
            append_log(logs_dir / "pipeline.log", f"Hermes stderr: {hres.stderr.strip()}")

    append_log(logs_dir / "pipeline.log", "Pipeline complete")


if __name__ == "__main__":
    main()
