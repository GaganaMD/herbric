# Bridge: Fabric ↔ Hermes Long-Context Research Pipeline

`bridge` is a lightweight Python integration layer that connects **Fabric** and **Hermes** for long-context research workflows. It is designed as a standalone orchestration module: it does not modify the Fabric source code, does not modify the Hermes agent source code, and does not require a heavy framework, vector database, or web service.

The bridge reads an input document, splits it into manageable chunks, runs selected Fabric patterns on each chunk, combines the Fabric outputs into one structured context file, and then sends that context into Hermes for final synthesis.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [High-Level Architecture](#high-level-architecture)
3. [Execution Flow](#execution-flow)
4. [Repository Structure](#repository-structure)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [How to Run the Pipeline](#how-to-run-the-pipeline)
9. [Generated Output Files](#generated-output-files)
10. [File-by-File Implementation Details](#file-by-file-implementation-details)
11. [Detailed Pipeline Walkthrough](#detailed-pipeline-walkthrough)
12. [Error Handling and Logging](#error-handling-and-logging)
13. [Customization Guide](#customization-guide)
14. [Troubleshooting](#troubleshooting)
15. [Known Limitations](#known-limitations)
16. [Extension Ideas](#extension-ideas)

---

## What This Project Does

The bridge converts a normal text document into a structured research workflow:

```text
Input document
   ↓
Chunk into smaller sections
   ↓
Run Fabric patterns on each chunk
   ↓
Save per-chunk Fabric outputs
   ↓
Aggregate all Fabric outputs into one combined context
   ↓
Build a final Hermes prompt
   ↓
Run Hermes
   ↓
Save final Hermes output
```

In simple terms:

- **Fabric** performs repeated chunk-level analysis.
- **Hermes** performs final synthesis over the combined Fabric analysis.
- **Python bridge code** coordinates the process using files, config, logs, and subprocess calls.

The bridge is intentionally small and easy to inspect. The implementation favors clarity over abstraction.

---

## High-Level Architecture

The project has five main layers:

```text
+-------------------+
|   Input Document  |
| small_input.txt   |
+---------+---------+
          |
          v
+-------------------+
|     chunker.py    |
| Splits text into  |
| overlapping chunks|
+---------+---------+
          |
          v
+-------------------+
| fabric_runner.py  |
| Runs Fabric       |
| patterns per chunk|
+---------+---------+
          |
          v
+-------------------+
| run_pipeline.py   |
| Aggregates Fabric |
| outputs into one  |
| context file      |
+---------+---------+
          |
          v
+-------------------+
| hermes_runner.py  |
| Sends final prompt|
| to Hermes         |
+---------+---------+
          |
          v
+-------------------+
| Final Markdown    |
| Hermes response   |
+-------------------+
```

The central idea is that the bridge does not need internal APIs from Fabric or Hermes. It treats them as external command-line tools and communicates through:

- standard input,
- standard output,
- command templates,
- Markdown files,
- log files.

---

## Execution Flow

The intended flow is:

```text
bridge/small_input.txt
   ↓
bridge/chunker.py
   ↓
Fabric runs selected patterns:
   - extract_wisdom
   - summarize
   - analyze_claims
   - create_5_sentence_summary
   ↓
bridge/out/fabric_outputs/*.md
   ↓
bridge/out/combined_context.md
   ↓
bridge/out/hermes_prompt.txt
   ↓
Hermes oneshot execution
   ↓
bridge/out/hermes_final_output.md
```

---

## Repository Structure

Expected structure:

```text
workspace-root/
├── Fabric/
│   └── ...
├── hermes-agent/
│   └── ...
└── bridge/
    ├── README.md
    ├── config.yaml
    ├── requirements.txt
    ├── small_input.txt
    ├── run_pipeline.py
    ├── chunker.py
    ├── fabric_runner.py
    ├── hermes_runner.py
    └── utils.py
```

Generated files are written under:

```text
bridge/out/
├── combined_context.md
├── hermes_prompt.txt
├── hermes_final_output.md
├── fabric_outputs/
│   ├── chunk_0001__extract_wisdom.md
│   ├── chunk_0001__summarize.md
│   ├── chunk_0001__analyze_claims.md
│   └── chunk_0001__create_5_sentence_summary.md
└── logs/
    ├── pipeline.log
    ├── fabric_runner.log
    └── hermes_runner.log
```

---

## Prerequisites

You need:

1. **Python 3.10+** recommended.
2. **PyYAML**, installed from `requirements.txt`.
3. **Fabric** available either globally or through a repo-local command.
4. **Go**, if Fabric is being run from source using `go run`.
5. **Hermes** available as a command-line executable, currently configured as `hermes`.
6. A shell environment compatible with the command templates in `config.yaml`.

The current configuration uses a command style suitable for Windows with Git-Bash-style shell execution.

---

## Installation

From the workspace root, install the bridge dependency:

```bash
python -m pip install -r ./bridge/requirements.txt
```

The only Python package required by the current bridge code is:

```text
PyYAML>=6.0
```

`PyYAML` is used to load `config.yaml`.

---

## Configuration

All important runtime behavior is controlled from:

```text
bridge/config.yaml
```

The pipeline is intentionally config-first. Most changes should be made in this YAML file instead of editing Python code.

### Path Configuration

```yaml
paths:
  input_file: "./bridge/small_input.txt"
  output_dir: "./bridge/out"
  combined_context_file: "./bridge/out/combined_context.md"
  fabric_outputs_dir: "./bridge/out/fabric_outputs"
  logs_dir: "./bridge/out/logs"
```

These paths define:

| Key | Purpose |
|---|---|
| `input_file` | Text file that will be analyzed. |
| `output_dir` | Main directory where pipeline output is written. |
| `combined_context_file` | Aggregated Fabric result file. |
| `fabric_outputs_dir` | Directory for per-chunk, per-pattern Fabric outputs. |
| `logs_dir` | Directory for pipeline, Fabric, and Hermes logs. |

Relative paths are resolved against the workspace root.

---

### Chunking Configuration

```yaml
chunking:
  max_chars: 5000
  overlap_chars: 500
  preserve_paragraphs: true
```

| Key | Purpose |
|---|---|
| `max_chars` | Maximum approximate character count per chunk. |
| `overlap_chars` | Number of characters copied from the previous chunk into the next chunk. |
| `preserve_paragraphs` | When `true`, splitting is paragraph-first. When `false`, splitting is sentence-first. |

The overlap is inserted into later chunks as:

```text
[OVERLAP_CONTEXT]
previous chunk tail
[/OVERLAP_CONTEXT]

current chunk text
```

This helps Fabric preserve continuity when the source document is split across multiple chunks.

---

### Fabric Configuration

```yaml
fabric:
  enabled: true
  command: "cd Fabric && \"C:\\Program Files\\Go\\bin\\go.exe\" run ./cmd/fabric"
  patterns:
    - extract_wisdom
    - summarize
    - analyze_claims
    - create_5_sentence_summary
  command_template: "{fabric_command} --pattern {pattern}"
  continue_on_error: true
```

| Key | Purpose |
|---|---|
| `enabled` | Turns Fabric processing on or off. |
| `command` | Base command used to run Fabric. |
| `patterns` | Fabric patterns to run on each chunk. |
| `command_template` | Shell command template. `{fabric_command}` and `{pattern}` are replaced at runtime. |
| `continue_on_error` | If `true`, the pipeline continues even when one Fabric run fails. |

The current Fabric command is repo-local and runs Fabric through Go:

```bash
cd Fabric && "C:\Program Files\Go\bin\go.exe" run ./cmd/fabric
```

Then each pattern is injected into the template:

```bash
{fabric_command} --pattern {pattern}
```

For example, one generated command may become:

```bash
cd Fabric && "C:\Program Files\Go\bin\go.exe" run ./cmd/fabric --pattern summarize
```

The chunk text is not placed directly into the command string. It is passed to Fabric through `stdin`.

---

### Aggregation Configuration

```yaml
aggregation:
  include_raw_chunk_text: false
  include_pattern_headers: true
```

| Key | Purpose |
|---|---|
| `include_raw_chunk_text` | If `true`, the original chunk text is included in `combined_context.md`. |
| `include_pattern_headers` | If `true`, each Fabric result is labeled with its pattern name. |

With `include_pattern_headers: true`, the combined file contains sections like:

```markdown
## Chunk 1

### Pattern: summarize
...

### Pattern: analyze_claims
...
```

---

### Hermes Configuration

```yaml
hermes:
  enabled: true
  command: "hermes"
  command_template: "{hermes_command} -z \"$(cat {prompt_file})\""
  final_prompt_header: |
    You are given structured research context produced from chunk-level Fabric analysis.
    Produce:
    1) key findings
    2) unresolved risks/unknowns
    3) contradictions across chunks
    4) prioritized follow-up questions
    Keep evidence vs inference clearly separated.
```

| Key | Purpose |
|---|---|
| `enabled` | Turns Hermes processing on or off. |
| `command` | Hermes executable command. |
| `command_template` | Shell command template for passing the prompt file into Hermes. |
| `final_prompt_header` | Instruction block prepended before the combined Fabric context. |

The current Hermes command template is:

```bash
hermes -z "$(cat bridge/out/hermes_prompt.txt)"
```

This means the bridge writes the final prompt to a file first, then injects the prompt file contents into Hermes oneshot mode.

---

## How to Run the Pipeline

From the workspace root:

```bash
python ./bridge/run_pipeline.py --config ./bridge/config.yaml
```

If no `--config` argument is provided, the script defaults to:

```bash
./bridge/config.yaml
```

Equivalent command:

```bash
python ./bridge/run_pipeline.py
```

---

## Generated Output Files

After a successful run, the bridge writes several outputs.

### 1. Per-Pattern Fabric Outputs

```text
bridge/out/fabric_outputs/chunk_0001__summarize.md
bridge/out/fabric_outputs/chunk_0001__analyze_claims.md
...
```

Each file contains the output from one Fabric pattern applied to one chunk.

Naming format:

```text
chunk_<chunk_id>__<pattern>.md
```

Example:

```text
chunk_0001__extract_wisdom.md
```

---

### 2. Combined Context

```text
bridge/out/combined_context.md
```

This file aggregates all Fabric outputs into one structured Markdown document.

It is the main intermediate file passed to Hermes.

---

### 3. Hermes Prompt

```text
bridge/out/hermes_prompt.txt
```

This file contains:

1. the configured `final_prompt_header`,
2. the phrase `Use this context:`,
3. the full `combined_context.md` content.

---

### 4. Final Hermes Output

```text
bridge/out/hermes_final_output.md
```

This is the final synthesized answer produced by Hermes.

---

### 5. Logs

```text
bridge/out/logs/pipeline.log
bridge/out/logs/fabric_runner.log
bridge/out/logs/hermes_runner.log
```

These help debug command execution, failed subprocesses, missing files, and stderr messages.

---

## File-by-File Implementation Details

### `run_pipeline.py`

`run_pipeline.py` is the main orchestrator.

Its responsibilities are:

1. Parse the `--config` command-line argument.
2. Load `config.yaml`.
3. Resolve relative paths into absolute paths.
4. Create output directories.
5. Read the input text file.
6. Call `chunk_text()` from `chunker.py`.
7. Run configured Fabric patterns on each chunk.
8. Summarize Fabric run counts.
9. Build `combined_context.md`.
10. Build `hermes_prompt.txt`.
11. Run Hermes.
12. Save `hermes_final_output.md`.
13. Write pipeline logs.

Important imports:

```python
from chunker import chunk_text
from fabric_runner import run_fabric_on_chunk, summarize_fabric_results, FabricResult
from hermes_runner import run_hermes
from utils import append_log, ensure_dir, load_config, resolve_path, write_text
```

The file has two major functions:

```python
def build_combined_context(...):
    ...


def main() -> None:
    ...
```

#### `build_combined_context()`

This function takes:

- the list of chunks,
- all Fabric results,
- whether raw chunk text should be included,
- whether pattern headers should be included.

It groups Fabric results by chunk ID and builds a Markdown document:

```markdown
# Combined Research Context

## Chunk 1

### Pattern: summarize
...

### Pattern: analyze_claims
...
```

If a Fabric run failed or returned empty output, the combined context includes a marker:

```markdown
[Pattern failed or empty output | exit_code=1]
```

If stderr exists, it is also included.

#### `main()`

`main()` performs the full pipeline sequence. It is protected by:

```python
if __name__ == "__main__":
    main()
```

This allows the script to be run directly from the command line.

---

### `chunker.py`

`chunker.py` is responsible for splitting source text into smaller pieces.

It defines a small dataclass:

```python
@dataclass
class Chunk:
    chunk_id: int
    text: str
```

Each chunk has:

| Field | Meaning |
|---|---|
| `chunk_id` | 1-based chunk number. |
| `text` | Text content for that chunk. |

#### Paragraph splitting

The helper function:

```python
def _split_paragraphs(text: str) -> List[str]:
```

splits text wherever there are blank lines.

It uses this regex:

```python
r"\n\s*\n"
```

This means paragraphs are separated by one or more blank lines, optionally containing whitespace.

#### Sentence splitting

The helper function:

```python
def _split_sentences(text: str) -> List[str]:
```

uses a lightweight regex:

```python
r"(?<=[.!?])\s+"
```

This splits after `.`, `!`, or `?` followed by whitespace.

This is a heuristic splitter, not a full natural-language parser.

#### Main chunking logic

The main function is:

```python
def chunk_text(
    text: str,
    max_chars: int = 5000,
    overlap_chars: int = 500,
    preserve_paragraphs: bool = True,
) -> List[Chunk]:
```

Behavior:

1. Empty input returns an empty list.
2. If `preserve_paragraphs` is `true`, it starts with paragraph splitting.
3. Otherwise, it starts with sentence splitting.
4. It keeps appending units into the current chunk until `max_chars` would be exceeded.
5. When a chunk becomes too large, it flushes the current chunk and starts another.
6. If one paragraph is itself larger than `max_chars`, the paragraph is split into sentences.
7. If `overlap_chars > 0`, later chunks receive a tail from the previous chunk.
8. The final output is a list of `Chunk` objects.

The overlap is intentionally marked in the chunk text:

```text
[OVERLAP_CONTEXT]
...
[/OVERLAP_CONTEXT]
```

That makes the carried-over text visible to Fabric and easier to distinguish from the current chunk.

---

### `fabric_runner.py`

`fabric_runner.py` is responsible for invoking Fabric through the shell.

It defines:

```python
@dataclass
class FabricResult:
    chunk_id: int
    pattern: str
    stdout: str
    stderr: str
    exit_code: int
    output_file: Path
```

Each `FabricResult` records:

| Field | Meaning |
|---|---|
| `chunk_id` | Which chunk was processed. |
| `pattern` | Which Fabric pattern was used. |
| `stdout` | Fabric output. |
| `stderr` | Fabric error output. |
| `exit_code` | Process return code. |
| `output_file` | Markdown file where stdout was saved. |

#### `run_fabric_on_chunk()`

This function runs every configured Fabric pattern against one chunk.

Simplified behavior:

```python
for pattern in patterns:
    cmd = command_template.format(
        fabric_command=fabric_command,
        pattern=shlex.quote(pattern),
    )

    proc = subprocess.run(
        cmd,
        input=chunk_text,
        shell=True,
        capture_output=True,
    )
```

Important details:

- `pattern` is shell-quoted using `shlex.quote()`.
- The chunk text is passed through `stdin` using `input=chunk_text`.
- Fabric output is captured from `stdout`.
- Fabric errors are captured from `stderr`.
- Each result is written to a Markdown file.
- Errors are logged.
- If `continue_on_error` is `true`, the pipeline continues after failed Fabric runs.

#### Output file naming

```python
out_file = outputs_dir / f"chunk_{chunk_id:04d}__{pattern}.md"
```

Examples:

```text
chunk_0001__summarize.md
chunk_0002__analyze_claims.md
```

#### `summarize_fabric_results()`

This helper returns a dictionary like:

```python
{
    "total_runs": 4,
    "failed_runs": 0,
    "successful_runs": 4,
}
```

That summary is written to `pipeline.log`.

---

### `hermes_runner.py`

`hermes_runner.py` invokes Hermes as a subprocess.

It defines:

```python
@dataclass
class HermesResult:
    stdout: str
    stderr: str
    exit_code: int
```

#### `run_hermes()`

This function:

1. Builds the Hermes shell command from the configured template.
2. Logs the command.
3. Runs Hermes using `subprocess.run()`.
4. Captures stdout, stderr, and exit code.
5. Logs stderr if Hermes fails.
6. Returns a `HermesResult`.

The prompt file path is normalized for shell compatibility:

```python
prompt_file=str(prompt_file).replace('\\', '/')
```

This is useful on Windows because it converts backslashes into forward slashes before the path is inserted into a shell command.

---

### `utils.py`

`utils.py` contains shared helper functions.

| Function | Purpose |
|---|---|
| `project_root()` | Returns the workspace root, assuming `bridge` is one level below it. |
| `resolve_path()` | Converts relative paths to absolute paths. |
| `ensure_dir()` | Creates a directory if it does not exist. |
| `load_config()` | Loads YAML config using PyYAML. |
| `now_ts()` | Returns a UTC timestamp string. |
| `write_text()` | Writes text to a file, creating the parent directory first. |
| `append_log()` | Appends timestamped messages to a log file. |

The timestamp format is UTC:

```text
YYYY-MM-DDTHH:MM:SSZ
```

Example log line:

```text
[2026-05-25T10:20:30Z] Pipeline complete
```

---

### `config.yaml`

`config.yaml` is the control plane of the bridge.

It controls:

- input file path,
- output directories,
- chunk size,
- overlap size,
- Fabric command,
- Fabric patterns,
- Fabric failure behavior,
- aggregation options,
- Hermes command,
- Hermes final prompt instructions.

This design keeps the Python files stable while allowing the user to change behavior from YAML.

---

### `small_input.txt`

`small_input.txt` is a sample input document. It describes a case where Acme Robotics reduced assembly defects using machine-vision checkpoints, while still facing risks around calibration drift, ignored alerts, and inconsistent maintenance staffing.

This file is useful for testing the pipeline before replacing it with a larger real document.

---

### `requirements.txt`

The requirements file contains:

```text
PyYAML>=6.0
```

That dependency is required for:

```python
import yaml
```

inside `utils.py`.

---

## Detailed Pipeline Walkthrough

This section explains what happens when you run:

```bash
python ./bridge/run_pipeline.py --config ./bridge/config.yaml
```

### Step 1: Parse command-line arguments

`run_pipeline.py` uses `argparse` to read the config path:

```bash
--config ./bridge/config.yaml
```

If omitted, it uses:

```text
./bridge/config.yaml
```

---

### Step 2: Load YAML config

The script calls:

```python
cfg = load_config(args.config)
```

`load_config()` is defined in `utils.py` and uses `yaml.safe_load()`.

---

### Step 3: Resolve paths

The script sets:

```python
base = Path(__file__).resolve().parent.parent
```

Since `run_pipeline.py` is inside `bridge`, `parent.parent` points to the workspace root.

Then paths like:

```text
./bridge/small_input.txt
```

are converted into absolute paths.

---

### Step 4: Create output directories

The pipeline ensures these directories exist:

```text
bridge/out
bridge/out/fabric_outputs
bridge/out/logs
```

It uses:

```python
ensure_dir(...)
```

which calls:

```python
path.mkdir(parents=True, exist_ok=True)
```

---

### Step 5: Validate and read input file

The pipeline checks whether the input file exists:

```python
if not input_file.exists():
    raise FileNotFoundError(...)
```

Then it reads the input as UTF-8 text:

```python
source_text = input_file.read_text(encoding="utf-8")
```

---

### Step 6: Chunk the input text

The script calls:

```python
chunks = chunk_text(
    source_text,
    max_chars=int(cfg["chunking"]["max_chars"]),
    overlap_chars=int(cfg["chunking"].get("overlap_chars", 0)),
    preserve_paragraphs=bool(cfg["chunking"].get("preserve_paragraphs", True)),
)
```

This produces a list of `Chunk` objects.

For the current sample input, the text is small enough to fit into one chunk.

---

### Step 7: Run Fabric on each chunk

If Fabric is enabled:

```yaml
fabric:
  enabled: true
```

then the pipeline loops through every chunk and sends it to `run_fabric_on_chunk()`.

For each chunk, Fabric runs the configured patterns:

```yaml
patterns:
  - extract_wisdom
  - summarize
  - analyze_claims
  - create_5_sentence_summary
```

So if there are 3 chunks and 4 patterns, the bridge performs:

```text
3 × 4 = 12 Fabric runs
```

Each run gets its own output file.

---

### Step 8: Summarize Fabric results

After Fabric runs, the pipeline counts:

- total Fabric runs,
- failed Fabric runs,
- successful Fabric runs.

That summary is written to:

```text
bridge/out/logs/pipeline.log
```

---

### Step 9: Build combined context

The pipeline calls:

```python
combined = build_combined_context(...)
```

This produces a single Markdown file containing all Fabric outputs grouped by chunk.

The file is written to:

```text
bridge/out/combined_context.md
```

---

### Step 10: Build Hermes prompt

If Hermes is enabled:

```yaml
hermes:
  enabled: true
```

then the pipeline creates:

```text
bridge/out/hermes_prompt.txt
```

The prompt is built like this:

```python
prompt_text = f"{header}\n\nUse this context:\n\n{combined}"
```

So Hermes receives both:

1. the final instruction header from config,
2. the combined Fabric context.

---

### Step 11: Run Hermes

The pipeline calls:

```python
hres = run_hermes(...)
```

Hermes is invoked using the configured command template:

```bash
{hermes_command} -z "$(cat {prompt_file})"
```

The result is captured from stdout.

---

### Step 12: Write final output

Hermes stdout is saved to:

```text
bridge/out/hermes_final_output.md
```

The pipeline then logs:

```text
Pipeline complete
```

---

## Error Handling and Logging

The bridge records runtime events in log files.

### Pipeline Log

```text
bridge/out/logs/pipeline.log
```

Contains high-level events:

- pipeline start,
- resolved input path,
- number of chunks,
- Fabric summary,
- combined context path,
- Hermes exit code,
- pipeline completion.

### Fabric Runner Log

```text
bridge/out/logs/fabric_runner.log
```

Contains:

- Fabric command used for each chunk and pattern,
- chunk ID,
- pattern name,
- exit code for failed commands,
- Fabric stderr for failed commands.

### Hermes Runner Log

```text
bridge/out/logs/hermes_runner.log
```

Contains:

- Hermes command used,
- exit code for failed Hermes execution,
- Hermes stderr if available.

---

## Customization Guide

### Use a different input file

Edit:

```yaml
paths:
  input_file: "./bridge/my_document.txt"
```

Then run:

```bash
python ./bridge/run_pipeline.py --config ./bridge/config.yaml
```

---

### Change chunk size

For larger chunks:

```yaml
chunking:
  max_chars: 10000
```

For smaller chunks:

```yaml
chunking:
  max_chars: 2500
```

Smaller chunks may be easier for Fabric to process, but they can create more total Fabric runs.

---

### Change overlap

To increase continuity between chunks:

```yaml
chunking:
  overlap_chars: 1000
```

To disable overlap:

```yaml
chunking:
  overlap_chars: 0
```

---

### Add or remove Fabric patterns

Edit:

```yaml
fabric:
  patterns:
    - summarize
    - analyze_claims
```

The pipeline automatically runs every listed pattern for every chunk.

---

### Disable Fabric temporarily

```yaml
fabric:
  enabled: false
```

This skips Fabric processing. The combined context may contain only chunk headings unless raw chunk text is enabled.

---

### Include raw source text in combined context

```yaml
aggregation:
  include_raw_chunk_text: true
```

This is useful when Hermes needs direct access to source excerpts, not only Fabric summaries.

---

### Disable Hermes temporarily

```yaml
hermes:
  enabled: false
```

This lets you stop after generating `combined_context.md`.

---

### Change the Hermes final task

Edit:

```yaml
hermes:
  final_prompt_header: |
    Your custom instruction here.
```

For example:

```yaml
hermes:
  final_prompt_header: |
    You are given chunk-level research notes.
    Produce an executive summary, list all risks, and recommend next actions.
```

---

## Troubleshooting

### `FileNotFoundError: Input file not found`

Check:

```yaml
paths:
  input_file: "./bridge/small_input.txt"
```

Make sure the file exists relative to the workspace root.

---

### Fabric command fails

Check:

```text
bridge/out/logs/fabric_runner.log
```

Common causes:

- Go is not installed or not on the expected path.
- `Fabric` folder is not located at the expected path.
- Fabric command syntax is wrong for the current shell.
- Fabric pattern name is invalid.
- Fabric requires environment variables or model configuration not yet set.

You can test the configured command manually from the workspace root:

```bash
cd Fabric && "C:\Program Files\Go\bin\go.exe" run ./cmd/fabric --pattern summarize
```

Then type or pipe sample text into it.

---

### Hermes command fails

Check:

```text
bridge/out/logs/hermes_runner.log
```

Common causes:

- `hermes` is not installed or not on PATH.
- Hermes does not support the configured `-z` argument.
- The shell cannot evaluate `$(cat {prompt_file})`.
- The prompt is too large for command-line injection.

For very large prompts, consider changing the Hermes command template to a mode that reads from a file or stdin, if Hermes supports that.

---

### Output files are empty

Check:

1. `fabric_runner.log` for Fabric failures.
2. `hermes_runner.log` for Hermes failures.
3. Whether the configured Fabric patterns return output.
4. Whether `continue_on_error` allowed failures to pass silently into the combined context.

---

### Paths behave strangely on Windows

`hermes_runner.py` converts backslashes to forward slashes for the prompt file path before inserting it into the command template.

Still, shell quoting can differ between:

- PowerShell,
- CMD,
- Git Bash,
- WSL,
- MSYS2.

The current config is most aligned with Git-Bash-style command substitution:

```bash
$(cat file)
```

PowerShell does not use that syntax.

---

## Known Limitations

1. **Chunking is character-based**, not token-based. It does not know the exact token limits of downstream models.
2. **Sentence splitting is heuristic** and may split incorrectly on abbreviations or unusual punctuation.
3. **Subprocess calls use `shell=True`**, so command templates should be treated carefully and should not include untrusted user input.
4. **Hermes prompt injection uses shell command substitution**, which may hit command-line length limits for very large documents.
5. **No retry logic** is implemented for failed Fabric or Hermes calls.
6. **No parallel execution** is implemented; Fabric patterns are run sequentially.
7. **No structured JSON output contract** is enforced; outputs are plain Markdown/text.
8. **No caching** is implemented; rerunning the pipeline reruns Fabric and Hermes.

---

## Extension Ideas

Possible future improvements:

1. **Token-aware chunking**
   - Replace character counting with model-token counting.

2. **Parallel Fabric runs**
   - Run chunk-pattern combinations concurrently for faster processing.

3. **Retry support**
   - Retry failed Fabric or Hermes calls with backoff.

4. **Better prompt passing**
   - Avoid `$(cat prompt_file)` for very large prompts by using stdin or file-based Hermes input if supported.

5. **Run manifest**
   - Save a JSON file recording config, timestamps, chunks, patterns, exit codes, and output paths.

6. **Caching**
   - Skip Fabric runs when the same chunk and pattern output already exists.

7. **Validation**
   - Validate `config.yaml` before execution and produce clearer error messages.

8. **Pluggable backends**
   - Support other tools besides Fabric and Hermes using the same command-template approach.

9. **Structured output mode**
   - Ask Fabric and Hermes to emit JSON, then validate and aggregate it more reliably.

---

## Quick Start

```bash
# 1. Install dependency
python -m pip install -r ./bridge/requirements.txt

# 2. Check config
cat ./bridge/config.yaml

# 3. Run pipeline
python ./bridge/run_pipeline.py --config ./bridge/config.yaml

# 4. Inspect outputs
ls ./bridge/out
ls ./bridge/out/fabric_outputs
cat ./bridge/out/combined_context.md
cat ./bridge/out/hermes_final_output.md
```

---

## Summary

`bridge` is a minimal orchestration layer between Fabric and Hermes.

It works by:

1. reading a text file,
2. chunking it,
3. running Fabric patterns on each chunk,
4. saving Fabric outputs,
5. combining those outputs into a single research context,
6. building a Hermes prompt,
7. running Hermes,
8. saving the final synthesis.

The main strength of this design is simplicity. The bridge avoids deep integration and instead relies on clear file boundaries, configurable commands, and subprocess execution.
