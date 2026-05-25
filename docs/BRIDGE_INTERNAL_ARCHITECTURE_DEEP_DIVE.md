# BRIDGE INTERNAL ARCHITECTURE DEEP DIVE

## Scope and boundary
This document explains the implemented bridge in this workspace as an orchestration system, not as a product README. It focuses on:
- `bridge/run_pipeline.py`
- `bridge/chunker.py`
- `bridge/fabric_runner.py`
- `bridge/hermes_runner.py`
- `bridge/utils.py`
- `bridge/config.yaml`
- runtime artifacts under `bridge/out/` and DD-specific bridge runs under `hermes_investor_dd_tonbo/bridge_inputs/out/`

It does not describe Hermes internals or Fabric internals beyond their invocation contract at the bridge boundary.

---

## 1) Why the bridge exists

### Problem in Hermes-only long-context DD workflows
For large diligence workflows (workbook-derived evidence, transcript/log corpora, multi-page technical notes), direct single-pass Hermes prompting creates four failure modes:
1. Context overload: too much unstructured raw text in one prompt.
2. Reasoning dilution: important signals buried in low-value text.
3. Prompt bloat: prompt budget consumed by transport, not insight.
4. Compression ambiguity: no explicit intermediate representation that separates evidence extraction from synthesis.

In practice, this leads to unstable quality in investor-grade outputs: key risks surface inconsistently, contradictions go undetected, and underwriting logic is harder to trace.

### Why Fabric was introduced
Fabric is used as a semantic preprocessing layer, not only summarization. The bridge uses multiple Fabric patterns to create different semantic views over each chunk:
- concise summary view,
- claim-analysis view,
- abstraction/wisdom view,
- forced-short synthesis view.

This creates representation transformation before Hermes synthesis.

### Why a dedicated bridge instead of larger prompts or direct repo modifications
A dedicated orchestration layer was needed because:
- Larger prompts do not solve decomposition quality.
- Tight coupling Hermes↔Fabric inside either upstream repo would violate update independence.
- Modifying `./Fabric` or `./hermes-agent` would convert upstream dependencies into forks.
- Operational concerns (chunking, retries, logging, command portability, path resolution) belong in orchestration, not model runtimes.

The bridge therefore acts as an external control plane.

---

## 2) System-level architecture

### Role separation
- Fabric: semantic preprocessing (map stage over chunks/patterns)
- Bridge: orchestration, routing, aggregation, observability
- Hermes: final synthesis/reasoning/generation (reduce stage over aggregated context)

This separation matters because it decouples:
- semantic digestion (high fan-out, pattern-diverse)
from
- reasoning synthesis (single final pass with structured context).

### Component diagram
```text
+--------------------+        +---------------------+        +------------------+
| Raw Evidence Files | -----> | Bridge Orchestrator | -----> | Hermes Synthesis |
| (txt/md/logs/etc.) |        | (run_pipeline.py)   |        | (hermes_runner)  |
+--------------------+        +---------------------+        +------------------+
                                     |        ^
                                     v        |
                              +---------------------+
                              | Fabric Runner        |
                              | (pattern fan-out)    |
                              +---------------------+
                                     |
                                     v
                              +---------------------+
                              | Fabric Pattern       |
                              | Outputs (*.md)       |
                              +---------------------+
```

### Dataflow diagram (implemented)
```text
input_file
  -> chunk_text()
    -> [chunk_1..chunk_n]
      -> for each chunk: for each pattern: subprocess Fabric
        -> out/fabric_outputs/chunk_XXXX__pattern.md
  -> build_combined_context()
    -> out/combined_context.md
  -> construct hermes_prompt.txt (header + combined context)
  -> subprocess Hermes
    -> out/hermes_final_output.md
```

### Pipeline state transitions
```text
INIT
 -> CONFIG_LOADED
 -> PATHS_RESOLVED
 -> INPUT_READ
 -> CHUNKED
 -> FABRIC_RUNNING
 -> FABRIC_AGGREGATED
 -> HERMES_PROMPT_BUILT
 -> HERMES_RUNNING
 -> COMPLETE
```

Failure states are logged, not hidden:
- Fabric command not found/path/provider issues are captured per chunk-pattern.
- If `continue_on_error=true`, pipeline still reaches aggregation and Hermes with partial context.

---

## 3) Directory and pipeline structure

### Workspace topology
- `hermes-agent/` (upstream dependency; untouched)
- `Fabric/` (upstream dependency; untouched)
- `bridge/` (new standalone orchestration layer)

### Bridge runtime paths
- `bridge/out/fabric_outputs/` per-chunk per-pattern markdown outputs
- `bridge/out/combined_context.md` aggregated semantic context
- `bridge/out/hermes_prompt.txt` final Hermes prompt payload
- `bridge/out/hermes_final_output.md` Hermes result
- `bridge/out/logs/{pipeline.log,fabric_runner.log,hermes_runner.log}`

### DD-specific orchestration outputs
For diligence runs in this workspace, a task-scoped mirror config/output path was used:
- `hermes_investor_dd_tonbo/bridge_inputs/bridge_config_dd.yaml`
- `hermes_investor_dd_tonbo/bridge_inputs/out/...`

Adjacent DD workflow folders used by downstream analytics/deck generation:
- `hermes_investor_dd_tonbo/analytics/` (workbook extracts, metrics lines, derived tables)
- `hermes_investor_dd_tonbo/research/` (summaries, evidence packs)
- `hermes_investor_dd_tonbo/output/` (presentation outputs)

This keeps reusable bridge code static and run artifacts externalized by task.

### Why this structure
- Isolation boundaries: upstream repos preserved.
- Reproducibility: config + logs + materialized intermediates.
- Modularity: chunking, Fabric invocation, Hermes invocation are independent modules.
- Auditable workflows: every transformation emits disk artifacts.

---

## 4) Full bridge pipeline execution flow

### Stage 0: ingest raw evidence
`run_pipeline.py` reads `paths.input_file` as UTF-8 text.
- hard fail if file missing.
- no implicit network fetch; deterministic local ingestion.

### Stage 1: chunking
`chunker.chunk_text()` emits ordered `Chunk(chunk_id, text)`.
- paragraph-first splitting (`\n\s*\n`)
- sentence fallback when a unit exceeds `max_chars`
- optional overlap tagging:
  - `[OVERLAP_CONTEXT]...[/OVERLAP_CONTEXT]`

### Stage 2: Fabric fan-out execution
For each chunk and each configured pattern:
- `fabric_runner.run_fabric_on_chunk()` formats command from template.
- passes chunk text via `stdin`.
- captures `stdout/stderr/exit_code`.
- writes output file: `chunk_{id:04d}__{pattern}.md`.
- logs command and errors into `fabric_runner.log`.

### Stage 3: aggregation
`build_combined_context()` in `run_pipeline.py`:
- groups `FabricResult` by `chunk_id`.
- writes ordered sections:
  - `## Chunk N`
  - optional source excerpt
  - optional `### Pattern: <name>`
  - pattern output or failure marker/stderr snippet
- outputs `combined_context.md`.

### Stage 4: Hermes prompt materialization
- creates `hermes_prompt.txt` as:
  - configured `final_prompt_header`
  - literal `combined_context.md` payload

### Stage 5: Hermes synthesis
`hermes_runner.run_hermes()` invokes Hermes via command template, captures output, and writes `hermes_final_output.md`.

### Generated artifacts per stage
- chunking: in-memory chunk objects
- Fabric stage: `fabric_outputs/*.md`
- aggregation: `combined_context.md`
- synthesis setup: `hermes_prompt.txt`
- final: `hermes_final_output.md`
- observability: three log files

---

## 5) `run_pipeline.py` deep dive (orchestration spine)

### Why it is the orchestration spine
`run_pipeline.py` centralizes lifecycle control and dependency ordering:
1. load config,
2. resolve paths,
3. enforce directories,
4. execute chunking,
5. execute Fabric map-stage,
6. aggregate semantic outputs,
7. invoke Hermes reduce-stage,
8. finalize logs.

This centralization avoids fragmented control logic across modules and keeps state transitions explicit.

### Control flow summary
```python
cfg = load_config(...)
resolve all paths
ensure output dirs
read source text
chunks = chunk_text(...)
if fabric enabled:
    for chunk in chunks:
        run all patterns via Fabric subprocess
combined = build_combined_context(chunks, fabric_results, ...)
write combined_context.md
if hermes enabled:
    write hermes_prompt.txt
    run_hermes(...)
    write hermes_final_output.md
log complete
```

### Operational behavior
- deterministic sequence (no async or queue)
- failure-tolerant Fabric stage when configured
- explicit artifact writes after each major stage
- no hidden in-memory-only conclusions

---

## 6) `chunker.py` deep dive

### Strategy
Primary splitter is paragraph boundaries; this preserves discourse units better than fixed-width slicing. If a single paragraph exceeds `max_chars`, sentence-level fallback is used.

### Overlap logic
When `overlap_chars > 0`, chunk N includes a tagged tail from chunk N-1. This provides continuity for pattern runs without rebuilding full prior context.

### Why naive splitting fails
Fixed char slicing can split:
- table descriptions from numeric evidence,
- premise from conclusion,
- claim from caveat.

That degrades claim extraction and contradiction detection. Paragraph-first segmentation is a pragmatic semantic boundary heuristic with low complexity.

### Trade-offs
- Larger chunks: fewer boundary losses, higher token/latency cost.
- Smaller chunks: better localization, but higher fragmentation risk.
- Overlap too low: context discontinuity.
- Overlap too high: redundancy and repeated signal amplification.

---

## 7) `fabric_runner.py` deep dive

### Invocation model
Fabric is called via subprocess command templates, e.g.:
- command: `cd Fabric && "C:\Program Files\Go\bin\go.exe" run ./cmd/fabric`
- template: `{fabric_command} --pattern {pattern}`

Chunk text is passed through stdin (`input=chunk_text`).

### Why subprocesses
- strict non-invasive integration with upstream Fabric repo
- no dependency on Fabric internal Python API contracts
- easy replacement of executable command/provider settings
- clear command-level logs for operations

### Error handling
Each pattern result includes:
- stdout,
- stderr,
- exit code,
- output file path.

With `continue_on_error=true`, pipeline accumulates partial outputs and proceeds. This is critical for long runs where one pattern/provider failure should not discard all previous work.

### UTF-8 fixes
`subprocess.run(..., text=True, encoding="utf-8", errors="replace")` was added to avoid decode failures on Windows default code pages. This is implemented in this file and in `hermes_runner.py`.

### Semantic behavior
Fabric stage acts like a map step:
- map key: `(chunk_id, pattern)`
- map value: semantic projection of the chunk
These projections become inputs to a reduce-style aggregator.

---

## 8) Fabric pattern interaction model

Configured patterns:
- `summarize`
- `extract_wisdom`
- `analyze_claims`
- `create_5_sentence_summary`

### Complementarity by representation type
- summarize: broad coverage compression
- extract_wisdom: higher-level abstraction and implications
- analyze_claims: claim-evidence tension and assertion structure
- create_5_sentence_summary: strict brevity normalization

### Why multiple passes matter
Single-pattern outputs are representation-biased. Multi-pattern outputs create orthogonal semantic slices, improving downstream synthesis robustness.

### Why `extract_wisdom` mattered
In DD workloads, `extract_wisdom` tends to surface investor-relevant implications (e.g., fragility patterns, governance signal) that plain summary often leaves implicit.

---

## 9) Aggregation layer deep dive

### Construction
`build_combined_context()` composes a deterministic markdown scaffold:
- top-level title
- chunk sections in original order
- per-pattern blocks in execution order
- failure markers where missing

### Function of aggregation
Aggregation is not a concatenation afterthought; it is the semantic handoff contract to Hermes:
- preserves provenance (chunk + pattern)
- keeps heterogenous semantic views adjacent
- enables Hermes to reason over both evidence and transformed abstractions

### Why quality here matters
If aggregation is noisy, Hermes receives confused scaffolding and spends reasoning budget reconstructing structure. Better aggregation yields better synthesis efficiency and consistency.

---

## 10) `hermes_runner.py` deep dive

### Invocation model
Hermes command is templated in config. Default template:
`{hermes_command} -z "$(cat {prompt_file})"`

`run_hermes()`:
- resolves command with prompt path (slash-normalized)
- executes subprocess
- captures stdout/stderr/exit
- logs command and errors

### Behavioral effect of Fabric preprocessing
Hermes receives a curated context object (`combined_context.md`) instead of raw corpus. This shifts Hermes from low-level digestion to high-level synthesis and contradiction/risk framing.

### Separation principle
- Fabric: “digest and transform”
- Hermes: “reason and compose”

That division reduces cognitive load in the final synthesis stage.

---

## 11) Logging and observability

### Log files
- `pipeline.log`: lifecycle milestones and high-level outcomes.
- `fabric_runner.log`: per chunk-pattern command lines + errors.
- `hermes_runner.log`: Hermes command line + non-zero exits.

### Debugging history observed in logs
`fabric_runner.log` records concrete failure phases:
1. `fabric` executable not found.
2. path resolution errors (`The system cannot find the path specified`).
3. Fabric provider/.env missing (`C:\Users\gagan\.config\fabric\.env`).
4. eventual successful pattern runs.

This progression shows observability was sufficient to diagnose setup failures without modifying upstream repos.

---

## 12) Configuration system (`config.yaml`)

### Structure
- `paths`: input/output/log locations
- `chunking`: `max_chars`, `overlap_chars`, `preserve_paragraphs`
- `fabric`: enable flag, command, patterns, template, error policy
- `aggregation`: include source text/header toggles
- `hermes`: enable flag, command, template, final header

### Why config-driven orchestration
- separates runtime policy from code
- permits per-workflow overrides (e.g., DD-specific config file)
- supports command portability without code edits
- allows controlled experimentation on chunking/pattern mix

---

## 13) Windows + UTF-8 debugging

### Issue
On Windows, subprocess text decoding can default to cp1252-like behavior depending on shell/runtime context. Model outputs may include characters outside that range, causing decode exceptions.

### Fix implemented
Both subprocess wrappers now force:
- `encoding="utf-8"`
- `errors="replace"`

### Why this is architecturally relevant
Encoding policy belongs at process boundaries. Without explicit decode policy, orchestration stability depends on host locale, which breaks reproducibility.

### Lesson
Cross-platform orchestration must treat text encoding as an explicit contract, not an environment assumption.

---

## 14) PowerPoint + DD workflow integration

In this workspace, the bridge fed DD presentation generation by creating semantically compressed context from workbook-derived evidence lines.

Flow used:
1. workbook extraction scripts produced evidence text slices,
2. bridge chunked and pattern-processed those slices,
3. combined context + Hermes synthesis became an analytical prior,
4. deck generation scripts used this prior to frame underwriting logic.

Observed benefit: stronger risk signal surfacing (QoE adjustments, concentration, WC fragility) versus raw metric narration.

---

## 15) Representation transformation theory (implementation-grounded)

The bridge evolved from “tool chaining” to a staged cognitive pipeline:
1. raw evidence representation,
2. chunk-local semantic projections (multi-pattern),
3. aggregated cross-chunk semantic scaffold,
4. final reasoning synthesis.

This is hierarchical cognition by construction:
- local transformations first,
- global synthesis second.

Implication for institutional analysis systems: separating semantic preprocessing from final reasoning increases controllability, observability, and auditability in long-context workflows.

---

## 16) Current limitations

1. Aggregation is linear markdown concatenation; no weighted ranking, dedup, or contradiction graph.
2. Chunk boundaries are heuristic; cross-chunk dependencies can still fragment.
3. Pattern outputs can be redundant; no automatic cross-pattern reconciliation.
4. No native visual/figure ingestion stage in bridge itself.
5. No slide-native layout reasoning in bridge; downstream deck logic remains separate.
6. No run registry/experiment metadata beyond logs and files.
7. Sequential execution only; no parallel chunk-pattern scheduling.

---

## 17) Future evolution directions

1. Rich aggregation layer
- deduplication,
- confidence tagging,
- contradiction indexing,
- evidence-reference linking.

2. Adaptive pattern routing
- choose pattern set by chunk type (financial table narrative vs legal/compliance text).

3. Multi-document orchestration
- explicit source IDs and provenance graph across files.

4. Retrieval-enhanced reduce stage
- selective context assembly from Fabric outputs before Hermes call.

5. Experiment tracking
- run manifests (config hash, command hash, artifact lineage).

6. Semantic memory (optional)
- reusable transformed artifacts across related DD runs with strict provenance controls.

7. Orchestration graph upgrade
- DAG execution with retry policies and optional parallel map stage.

---

## Appendix A: concrete execution examples from logs

From `bridge/out/logs/fabric_runner.log`:
- command-not-found phase (`'fabric' is not recognized...`)
- path-mismatch phase (`The system cannot find the path specified.`)
- provider setup phase (`...\.config\fabric\.env` missing)
- successful command phase using repo-local Go invocation

From `bridge/out/logs/pipeline.log`:
- chunk counts
- fabric success/failure summaries
- output file materialization
- Hermes exit status

These logs demonstrate the bridge’s operational transparency and explain how architecture-level choices (external orchestration, command templates, explicit logs) enabled iterative stabilization without upstream source edits.
