# bridge

Minimal standalone Fabric ↔ Hermes integration layer for long-context research workflows.

## Design goals
- No source modifications in `./Fabric` or `./hermes-agent`
- Integration only through `./bridge`
- Plain Python + subprocess orchestration
- Config-first path and command control
- Clear logs and reproducible flow

## Architecture
1. `run_pipeline.py`
   - Orchestrates end-to-end flow.
   - Loads `config.yaml`, resolves paths, logs execution.
2. `chunker.py`
   - Splits large input into semantic-ish chunks (paragraph-first, sentence fallback).
   - Configurable `max_chars`, `overlap_chars`, and paragraph preservation.
3. `fabric_runner.py`
   - Executes Fabric patterns chunk-by-chunk via subprocess.
   - Writes per-chunk/per-pattern outputs to `out/fabric_outputs/`.
4. Aggregation (inside `run_pipeline.py`)
   - Builds `combined_context.md` from all Fabric outputs.
5. `hermes_runner.py`
   - Sends aggregated context into Hermes via subprocess oneshot mode.
   - Stores final output in `out/hermes_final_output.md`.
6. `utils.py`
   - Shared utilities for config loading, path resolution, logging, and file writes.

## Execution flow
`input.txt` -> chunking -> Fabric pattern runs -> aggregation -> `combined_context.md` -> Hermes run

## Files produced
- `bridge/out/fabric_outputs/*.md` (chunk/pattern outputs)
- `bridge/out/combined_context.md`
- `bridge/out/hermes_prompt.txt`
- `bridge/out/hermes_final_output.md`
- `bridge/out/logs/*.log`

## Setup
From workspace root:

```bash
python -m pip install -r ./bridge/requirements.txt
```

## Configure paths/commands
Edit `./bridge/config.yaml`:
- `paths.input_file`: source document
- `fabric.command`: fabric executable/entry command
- `fabric.command_template`: how to invoke pattern runs
- `hermes.command`: hermes executable
- `hermes.command_template`: how to inject prompt file into hermes

If Fabric is not globally installed, set a repo-local command, e.g.:

```yaml
fabric:
  command: "cd ./Fabric && go run ."
```

## Run

```bash
python ./bridge/run_pipeline.py --config ./bridge/config.yaml
```

## Notes
- This bridge is intentionally lightweight and extensible.
- It avoids vector DBs, web services, and framework-heavy orchestration.
- On Windows Git-Bash, command templates use POSIX shell syntax.
