# Hermes Standalone vs Hermes + Fabric Bridge Orchestration

## 1) Executive summary
The integration of Fabric through an external bridge changed Hermes behavior from mostly single-pass synthesis to staged semantic orchestration. The material shift is not “better prompting,” but architectural: chunking, multi-pattern semantic projection, structured aggregation, then downstream synthesis. In observed runs, this improved long-document handling, risk extraction consistency, and evidence/inference separation for investor-style diligence outputs.

The gains came with non-trivial operational costs: extra configuration surface, dependency brittleness (Fabric command/path/provider setup), longer runtime, and additional failure points. Presentation quality also remained a separate bottleneck; analytical quality improved faster than slide-native design quality.

## 2) Original Hermes-only workflow
Baseline Hermes workflow (without bridge) is effectively:
1. Collect source material.
2. Build one large prompt (or a lightly structured prompt).
3. Run Hermes once (or small number of passes).
4. Use output directly for memo/deck drafting.

Strengths:
- Low orchestration overhead.
- Fast iteration for short/medium context tasks.
- Good direct synthesis when context is already curated.

Structural constraint:
- Hermes is asked to do ingestion, prioritization, compression, contradiction detection, and narrative synthesis in one cognitive pass.

## 3) Problems/limitations observed in standalone Hermes
Observed/documented Hermes-only long-context failure modes (from `docs/BRIDGE_INTERNAL_ARCHITECTURE_DEEP_DIVE.md`):
- Context overload from unstructured raw text.
- Reasoning dilution (signal buried in transport text).
- Prompt-budget inefficiency.
- No explicit intermediate representation between extraction and synthesis.

Practical implication:
- In DD-style workloads, key risks can surface inconsistently and contradiction tracking becomes less auditable.

## 4) Motivation for Fabric integration
Fabric was introduced as a semantic preprocessing layer, not only as a summarizer. The goal was to transform evidence before Hermes synthesis, using multiple pattern lenses per chunk (`summarize`, `extract_wisdom`, `analyze_claims`, `create_5_sentence_summary`).

Strategic motivation:
- Separate “semantic digestion” from “final reasoning composition.”
- Improve traceability and reproducibility through materialized intermediates.
- Keep Fabric and Hermes repos unmodified via subprocess boundaries.

## 5) Bridge architecture overview
Implemented bridge stack (`bridge/README.md`, `bridge/config.yaml`, `bridge/*.py`):
- `chunker.py`: paragraph-first chunking, sentence fallback, overlap tagging.
- `fabric_runner.py`: pattern fan-out per chunk via subprocess, output capture.
- `run_pipeline.py`: orchestration spine + aggregation into combined context.
- `hermes_runner.py`: final Hermes call on aggregated semantic context.
- `utils.py`: config/path/log utilities.

Key contract:
- CLI-level composition through stdin/stdout/files/logs; no internal API coupling.

## 6) End-to-end workflow comparison
Hermes standalone:
- Raw corpus -> large prompt -> Hermes synthesis.

Hermes + Fabric bridge:
- Raw corpus -> chunking -> per-chunk multi-pattern Fabric runs -> combined semantic context -> Hermes synthesis.

Observed DD run evidence (`hermes_investor_dd_tonbo/bridge_inputs/out/logs/pipeline.log`):
- Chunking: 2 chunks.
- Fabric: 8/8 successful runs (4 patterns × 2 chunks).
- Hermes synthesis executed after aggregation.

## 7) Cognitive architecture differences
Before integration:
- Single-agent overloaded cognition.
- One model stage handles extraction + prioritization + synthesis together.

After integration:
- Division of cognitive labor:
  - Fabric map-stage: local semantic projections.
  - Bridge: structural control + provenance scaffolding.
  - Hermes reduce-stage: cross-chunk synthesis and decision framing.

Net effect:
- Lower final-stage cognitive entropy for Hermes.
- Better use of Hermes for judgment composition rather than raw digestion.

## 8) Semantic preprocessing effects
Fabric multi-pattern preprocessing introduced representation diversity:
- `summarize`: broad compression.
- `analyze_claims`: claim/evidence tension extraction.
- `extract_wisdom`: implication-level abstraction.
- `create_5_sentence_summary`: strict brevity normalization.

This creates multiple semantic “views” per chunk before synthesis, reducing dependence on a single compression bias.

## 9) Reasoning-quality changes
In the DD output (`hermes_investor_dd_tonbo/bridge_inputs/out/hermes_final_output.md`), synthesis shows:
- explicit evidence-first framing,
- quantified risk bullets,
- clear underwriting implications,
- unresolved diligence asks.

The resulting structure is materially closer to investment committee reasoning than generic summary output.

## 10) Context management improvements
Bridge aggregation (`combined_context.md`) preserves:
- chunk order,
- pattern identity,
- per-stage materialization.

This improves auditability versus a monolithic prompt because provenance survives compression (chunk/pattern lineage is retained in artifacts).

## 11) Long-document handling improvements
Bridge supports controlled long-context scaling via config:
- `max_chars`, `overlap_chars`, paragraph preservation.
- overlap tagging (`[OVERLAP_CONTEXT]`) for continuity.

Observed behavior:
- multi-chunk DD evidence processed without collapsing to one unstable mega-prompt.

Residual issue:
- chunk boundaries remain heuristic; cross-boundary dependencies can still fragment meaning.

## 12) DD/investor workflow improvements
Integration contributed to stronger diligence framing in outputs:
- better QoE bridge articulation,
- concentration-risk stacking (customer + SKU + supplier),
- WC mechanics interpretation (DPO dependence),
- governance/control risk extraction,
- clearer underwriting asks.

These are decision-useful transformations, not just textual compression.

## 13) Presentation-generation effects
Integration improved analytical substrate for deck generation, but did not automatically solve design quality. Deck scripts still required separate QA/refinement passes (`build_dd_deck.py`, `refine_deck.py`, `qa_deck.py`, visual-upgrade scripts).

Interpretation:
- reasoning quality and presentation-native quality are separate system layers.

## 14) Image/context integration effects
Visual pipeline artifacts indicate image anchoring exists, but chart-native analytical visuals remained weak in later visual deck outputs:
- `layout_safety_qa_v4.json` shows per-slide images present.
- `charts` count is 0 across slides in that final safe deck QA output.

Implication:
- system improved visual anchoring and safe bounds, but still tends toward image-backed narrative slides rather than quantitatively chart-dense analytical pages.

## 15) New emergent capabilities after integration
Capabilities that became practical only after integration:
- reusable semantic preprocessing pipeline (chunk-map-reduce style),
- per-pattern transformed artifacts reusable across downstream tasks,
- explicit intermediate intelligence layer before final synthesis,
- multi-pass cognition with separation of local extraction vs global reasoning,
- higher reproducibility through saved logs/config/intermediates.

## 16) Operational tradeoffs introduced
Costs introduced by integration:
- more moving parts (Fabric runtime, provider env, shell/path correctness),
- longer runtime from pattern fan-out,
- larger failure surface across stages,
- higher prompt/config complexity,
- orchestration maintenance burden.

Observed setup friction (`bridge/out/logs/fabric_runner.log`):
- command not found,
- path resolution failures,
- missing Fabric provider env file,
- then eventual successful execution after fixes.

## 17) Failure modes still remaining
Even post-integration:
- aggregation is mostly linear concatenation (limited dedup/conflict graphing),
- no native confidence weighting across pattern outputs,
- partial failure tolerance (`continue_on_error`) can propagate incomplete context,
- no built-in experiment registry beyond logs/artifacts,
- sequential execution limits throughput for larger corpora.

## 18) Visual/design limitations still remaining
Remaining presentation-engine weaknesses (despite progress):
- slide quality requires separate deterministic QA loops,
- layout safety and typography are not guaranteed by reasoning pipeline alone,
- tendency toward memo-like text blocks unless explicit slide engineering is applied,
- chart reasoning and chart rendering are not yet tightly coupled in the visual pipeline.

## 19) Observed qualitative improvements
From observed artifacts and outputs:
- stronger underwriting framing,
- improved evidence-vs-inference separation,
- better risk extraction consistency,
- better long-context coherence in DD synthesis,
- improved operational traceability (logs + staged outputs),
- clearer unresolved-asks generation for diligence planning.

## 20) Why Fabric changed behavior materially
Fabric changed Hermes behavior because it altered the input representation, not just the instruction phrasing. Hermes received transformed, semantically structured context with chunk/pattern scaffolding, shifting its role from low-level parsing to high-level synthesis.

This is a cognitive architecture shift:
- from monolithic cognition,
- to staged semantic orchestration with explicit handoff contracts.

## 21) Future architecture directions
Highest-value next steps:
1. Smarter aggregation: dedup, contradiction indexing, confidence tags, evidence linking.
2. Adaptive pattern routing by chunk type (financial/legal/ops text classes).
3. Parallel map-stage execution with retry policy controls.
4. Run manifests (config hash, command hash, artifact lineage) for experiment governance.
5. Better coupling between analytical outputs and slide-native visual grammar.
6. Explicit multimodal integration (figures/tables/images) upstream of synthesis.

## 22) Key conclusions
- The integration is materially architectural, not cosmetic.
- It improves decision quality by decomposing cognition into inspectable stages.
- It increases operational overhead and introduces new failure points.
- It substantially helps long-context DD synthesis, risk framing, and evidence transformation.
- It does not automatically resolve visual design quality; that remains a distinct engineering layer.

Overall, Hermes + Fabric + bridge is best understood as a controllable multi-stage cognition pipeline with stronger institutional utility than Hermes standalone for complex diligence workflows, provided the orchestration and QA overhead is accepted and actively managed.
