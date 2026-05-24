# Autonomous Investor DD Presentation System - Technical Documentation

## 1) Purpose and scope

This document describes the current autonomous investor due diligence (DD) presentation system in:

- `C:\Users\gagan\Desktop\hermes-exp\PPT_creation`

It documents architecture, workflow lifecycle, subsystem boundaries, skill orchestration, artifacts, quality gates, and environment requirements for repeatable extension.

This is not a generic README. It is intended as internal platform documentation for engineering, analytics, and investment diligence workflows.

---

## 2) System overview

The system is a workbook-driven, evidence-first DD pipeline that transforms a diligence workbook into investor-grade PowerPoint outputs through iterative analytics and refinement.

Primary evidence source:

- `DD_Metrics_Comprehensive_Workbook.xlsx`

Primary execution tracks present in this repo:

1. Baseline build track (`hermes_investor_dd_tonbo`)
2. Upgrade/refinement track (`hermes_investor_dd_tonbo_upgrade`)

Core philosophy:

- Grounding before retrieval
- Metrics before narrative
- Narrative before design polish
- QA/refinement before finalization

---

## 3) Workflow philosophy and SOUL.md influence

`SOUL.md` defines the reasoning contract: skeptical underwriting posture, evidence traceability, explicit uncertainty, and anti-hype communication.

Observed behavioral implications in this project:

- Focus on fragility signals (concentration, QoE deltas, working-capital stress, governance gaps)
- Distinction between reported and restated economics
- Explicit diligence gaps as first-class findings
- Iterative pass structure (`v1 -> v2 -> v3/v4 -> v5 -> v6 -> v6_final`)
- High preference for investor utility over decorative output

SOUL-driven quality constraints:

- No unsupported certainty
- No decorative chart spam
- No "presentation polish equals diligence quality" shortcut

---

## 4) Architectural design decisions

### 4.1 Evidence-first workbook architecture

The workbook is treated as the primary analytical substrate. Scripts explicitly exclude tabs `00` and `21`, and process all other tabs into structured CSV and notes artifacts.

### 4.2 Scripted deterministic transformation

Pipeline uses Python scripts for repeatable extraction, charting, deck build, and refinement instead of manual editing.

### 4.3 Iterative deck hardening

Decks are produced in versions with QA metadata at each stage, rather than single-shot generation.

### 4.4 Proxy QA fallback + visual anchor enforcement

Where true render inspection is constrained, proxy audits (text density + visual-anchor checks) are used, then corrected through rebalancing and final polish.

---

## 5) End-to-end lifecycle (research to final PPT)

1. Prompting and control
   - `prompt.txt` encodes operating requirements (grounding-first, no synthetic images, investor framing, slide constraints, QA loop).

2. Workbook ingestion and tab coverage
   - Read workbook
   - Exclude tabs `00`, `21`
   - Export cleaned tab CSVs
   - Generate per-tab notes/artifacts

3. DD metric extraction and transformation
   - Parse key tables (revenue, profitability, QoE, WC, tax, cap table, etc.)
   - Convert raw metrics into investor-relevant indicators

4. Chart generation
   - Create reusable PNG chart assets in `analytics/charts/`

5. Narrative synthesis + PPT generation
   - Build workbook-driven slides using python-pptx
   - Apply underwriting-oriented storyline and IC framing

6. QA and iterative refinement
   - Density and visual-anchor checks
   - Rebalance layouts, add KPI cards/matrices, inject missing anchors

7. Final deliverables
   - Polished PPT
   - QA reports and workflow summaries
   - Coverage and grounding artifacts

---

## 6) Component responsibility map

### Hermes orchestration layer

Responsible for:

- Interpreting workflow intent from prompt/skills
- Sequencing phases (grounding, analytics, storytelling, design, QA)
- Enforcing evidence/QA discipline
- Producing and managing artifacts

### Codex reasoning layer

Responsible for:

- Metric interpretation and underwriting logic
- Risk framing and hypothesis formation
- Slide-level message compression and narrative hierarchy

### Firecrawl / web extraction layer

Intended responsibility (as per prompt philosophy):

- External research ingestion
- Source-grounded retrieval for company/domain context and image sourcing

Current repo evidence status:

- No explicit Firecrawl call logs/artifacts found in this project directory.
- Therefore web-extraction behavior should be treated as design intent, not fully evidenced runtime behavior in this snapshot.

### Python automation layer

Responsible for:

- Workbook extraction/cleanup
- Feature heuristics and risk flags
- Chart construction
- Deck generation and iterative modification
- QA metadata generation

### LibreOffice / render tooling layer

Intended responsibility:

- Render PPT to PDF/images for visual QA loops

Current environment evidence:

- `pdftoppm` available
- `markitdown` available
- `libreoffice/soffice` not detected in path during verification
- System compensates with proxy QA artifacts when full render tooling is absent

---

## 7) ASCII architecture diagram

```text
                    +---------------------------+
                    |        prompt.txt         |
                    |   SOUL.md + skills set    |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |  Workflow Orchestrator    |
                    |   (Hermes + Codex logic)  |
                    +-------------+-------------+
                                  |
            +---------------------+----------------------+
            |                                            |
            v                                            v
+----------------------------+               +----------------------------+
| Workbook Ingestion Layer   |               | External Grounding Layer   |
| DD_Metrics...xlsx          |               | (Web/Firecrawl design path)|
| exclude tabs 00,21         |               | company/domain context     |
+-------------+--------------+               +--------------+-------------+
              |                                             |
              v                                             v
+----------------------------+               +----------------------------+
| Tab Normalization          |               | Grounding Brief Artifacts  |
| cleaned CSV per tab        |               | grounding_brief.md/.pdf    |
| notes.md per tab           |               +--------------+-------------+
+-------------+--------------+                              |
              |                                             |
              +--------------------+------------------------+
                                   v
                    +---------------------------+
                    |  DD Analytics Engine      |
                    | metric extraction         |
                    | risk heuristics           |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Chart Generation Layer    |
                    | PNGs in analytics/charts  |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Story Synthesis Layer     |
                    | investor narrative / IC   |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | PPT Build Layer           |
                    | python-pptx deck versions |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | QA + Refinement Loop      |
                    | proxy audit + rebalance   |
                    | visual anchor enforcement |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Final Deliverables        |
                    | v6_final_polished.pptx    |
                    | JSON QA reports           |
                    +---------------------------+
```

---

## 8) Directory structure and artifact semantics

Top-level observed:

- `prompt.txt` - workflow contract and constraints
- `SOUL.md` - reasoning philosophy
- `DD_Metrics_Comprehensive_Workbook.xlsx` - primary evidence workbook
- `hermes_investor_dd_tonbo/` - baseline DD build pipeline
- `hermes_investor_dd_tonbo_upgrade/` - upgraded/refined pipeline

### 8.1 `hermes_investor_dd_tonbo/`

- `analytics/scripts/analyze_workbook.py`
  - cleans workbook tabs and generates baseline analytical outputs
- `analytics/scripts/build_investor_dd_deck.py`
  - extracts metrics, creates charts, generates v1/v2 decks
- `analytics/scripts/generate_tabwise_artifacts.py`
  - creates per-tab markdown extraction artifacts
- `analytics/processed_tables/*.csv`
  - cleaned tab-level workbook derivatives
- `analytics/charts/*.png`
  - generated chart assets
- `analytics/outputs/workbook_analysis_summary.json`
  - tab stats and risk flags
- `analytics/outputs/workbook_coverage.md`
  - workbook coverage summary
- `analytics/outputs/tab_artifacts/*.md`
  - extracted high-signal lines by tab
- `output/Tonbo_Investor_DD_WorkbookDriven_v1.pptx`
- `output/Tonbo_Investor_DD_WorkbookDriven_v2.pptx`
- `output/deck_build_qa.json`
- `output/metrics_extracted.json`

### 8.2 `hermes_investor_dd_tonbo_upgrade/`

- `analytics/scripts/run_full_workflow.py`
  - full ingestion + charting + v3/v4 generation + basic QA summary
- `analytics/scripts/enhance_v5.py`
  - adds advanced charts, adds slides, creates grounding brief artifacts
- `analytics/scripts/refine_v6_presentation.py`
  - structure rebalance (KPI cards, matrices, anchor band, concise text)
- `analytics/scripts/v6_final_polish.py`
  - inserts concrete visual anchors to anchor-deficient slides
- `analytics/*/analysis.py`
  - per-tab scaffold analysis scripts
- `analytics/*/notes.md`
  - per-tab extracted line summaries
- `analytics/charts/*.png`
  - advanced chart assets
- `analytics/processed_tables/*.csv`
- `analytics/outputs/workbook_coverage.md`
- `grounding_brief.md`, `grounding_brief.pdf`
- `output/workflow_summary.json`
- `output/v5_enhancement_report.json`
- `output/v6_rebalance_report.json`
- `output/v6_final_polish_report.json`
- `output/presentation_cognition_proxy_audit.json`
- `output/Tonbo_Investor_DD_WorkbookDriven_v3.pptx`
- `output/Tonbo_Investor_DD_WorkbookDriven_v4_final.pptx`
- `output/Tonbo_Investor_DD_WorkbookDriven_v5_enhanced.pptx`
- `output/Tonbo_Investor_DD_WorkbookDriven_v6_rebalanced.pptx`
- `output/Tonbo_Investor_DD_WorkbookDriven_v6_final_polished.pptx`

---

## 9) Workbook-driven DD analytics pipeline

### 9.1 Ingestion and normalization

Pattern:

- `pd.ExcelFile(...)`
- include sheets excluding prefixes `00`, `21`
- drop empty rows/columns
- normalize column names
- persist cleaned CSVs

### 9.2 Interpretation heuristics

Observed heuristics include:

- period-column discovery (`year`, `FY`, `month`, etc.)
- numeric field extraction
- volatility/sign-switch flags
- keyword extraction for investor-relevant lines

### 9.3 High-value analytical themes encoded

- Revenue quality and concentration
- Reported vs restated profitability
- Working capital cycle diagnostics
- QoE bridge adjustments
- Unit economics (aftermarket vs OEM)
- Tax/compliance exposures
- Projection evidence-strength screen

### 9.4 Transformation logic (raw metric -> investor meaning)

Implemented pattern aligns with DD principles:

- raw figure extraction
- trend/variance visualization
- operational implication tagging
- underwriting implication statements in slide narrative

---

## 10) Chart generation heuristics

Primary chart families observed:

- Trend lines (revenue, WC movement)
- Comparative bars (reported vs restated, unit economics)
- Concentration visuals
- Heatmaps (margin trajectory)
- Horizontal stress charts (cash flow quality)
- Heuristic scoring bars (projection evidence strength)

Design intent:

- investor interpretability over chart novelty
- avoid dense/low-signal visual artifacts

Known caveat:

- baseline script uses a pie chart for concentration (`customer_concentration.png`) while later philosophy prefers concentration bars; this is a potential future alignment improvement.

---

## 11) Investor storytelling architecture

Narrative structure (as implemented across versions):

1. Grounding/context
2. Revenue and concentration signals
3. Earnings-quality normalization
4. Working-capital and cash conversion stress
5. Unit economics pressure points
6. Governance/tax exposure
7. Diligence gaps
8. IC framing and conditions

Story mechanics:

- Each section links data signal to decision implication
- Unresolved evidence is surfaced explicitly
- Recommendation posture remains conditional where evidence depth is uneven

---

## 12) PowerPoint generation, QA, and refinement loop

### 12.1 Generation stack

- `python-pptx` for slide construction/modification
- charts injected from generated PNGs

### 12.2 QA controls observed

- Character-count overdensity checks
- Slide-level visual-anchor checks (`pics/charts/tables` proxies)
- Before/after QA reports across versions

### 12.3 Refinement pattern

- v5: expanded analysis and added slides
- v6_rebalanced: structural upgrades (KPI cards, matrix blocks, concise text)
- v6_final_polished: visual anchor closure (all slides anchored)

### 12.4 Render-based QA status

Visual-QA skill expects full render -> inspect -> refine -> re-render loops. In this snapshot:

- Proxy cognition audit is present (`presentation_cognition_proxy_audit.json`)
- No explicit PDF/image render pipeline logs were found in project outputs
- Final status should therefore be interpreted as "proxy-verified, render verification not fully evidenced here"

---

## 13) Skill architecture and orchestration

Skills loaded/used in this workflow model:

1. `company-grounding` (retrieval/semantic)
   - domain understanding before retrieval/synthesis
2. `financial-dd-analysis` (analytical core)
   - workbook-first interpretation and underwriting metrics
3. `investor-storytelling` (narrative layer)
   - IC-grade framing and conviction logic
4. `presentation-design` (presentation architecture)
   - layout hierarchy, readability, varied structures
5. `visual-qa` (quality gate)
   - render/proxy QA and refinement discipline
6. `autonomous-web-to-code-pipeline` (execution governance)
   - artifact discipline, iterative debug/provenance conventions

### Skill interaction model

```text
company-grounding
  -> financial-dd-analysis
      -> investor-storytelling
          -> presentation-design
              -> visual-qa
```

### Analytical vs presentation vs retrieval roles

- Retrieval-oriented: `company-grounding`
- Analytical: `financial-dd-analysis`
- Story/narrative: `investor-storytelling`
- Presentation-oriented: `presentation-design`
- QA/refinement: `visual-qa`
- Workflow-execution discipline: `autonomous-web-to-code-pipeline`

### Investor-DD bundle orchestration note

There is no separate skill file named "investor-dd bundle" in the current skill registry. Practically, the bundle behavior is implemented by orchestrating the five core DD/presentation skills above in sequence.

---

## 14) Environment and dependency requirements

## 14.1 Runtime context (observed)

- OS: Windows host with Git-Bash shell behavior
- Shell for terminal automation: `/usr/bin/bash`
- Working directory: `/c/Users/gagan/Desktop/hermes-exp/PPT_creation`
- Python: `3.11.13`
- Node: `v22.18.0`
- npm: `10.9.3`
- `pdftoppm`: available (`/c/Users/gagan/anaconda3/Library/bin/pdftoppm`)
- `markitdown`: available (`/c/Users/gagan/anaconda3/Scripts/markitdown`)
- `libreoffice/soffice`: not detected in current PATH check

## 14.2 Python package requirements (minimum)

Observed imports require:

- pandas
- numpy
- matplotlib
- seaborn
- python-pptx
- openpyxl
- pillow

Verification command:

```bash
python - <<'PY'
mods=['pandas','numpy','matplotlib','seaborn','pptx','openpyxl','PIL']
import importlib
for m in mods:
    try:
        importlib.import_module(m)
        print(m+':OK')
    except Exception:
        print(m+':MISSING')
PY
```

## 14.3 Node/tooling considerations

This repository snapshot does not include `package.json`, but broader workflow expectations mention:

- `pptxgenjs` for JS-based PPT generation variants

If JS pipeline is added, include explicit lockfile + scripts.

## 14.4 Render stack requirements

Preferred:

- LibreOffice/soffice for PPT->PDF conversion
- pdftoppm for PDF->PNG slide rendering

Example verification:

```bash
which soffice
which libreoffice
which pdftoppm
```

## 14.5 Firecrawl/API keys

Prompt/system philosophy references web extraction (including Firecrawl-style retrieval). For that mode, define keys in shell before run, e.g.:

```bash
export FIRECRAWL_API_KEY='...'
export OPENAI_API_KEY='...'
```

Current repo snapshot does not show persisted Firecrawl API call logs; if enabling this stage, enforce request/response logging under `logs/`.

## 14.6 Cross-shell notes (CMD vs Git-Bash)

- Current automation assumes POSIX shell syntax (`bash`), not PowerShell syntax.
- Prefer absolute POSIX paths in automated runs:
  - `/c/Users/gagan/Desktop/hermes-exp/PPT_creation/...`
- If using CMD/PowerShell manually, translate env/path commands accordingly.

---

## 15) Practical setup and verification sequence

```bash
# 1) Enter project root
cd /c/Users/gagan/Desktop/hermes-exp/PPT_creation

# 2) Verify runtimes
python --version
node --version
npm --version

# 3) Verify Python dependencies
python - <<'PY'
import pandas,numpy,matplotlib,seaborn,pptx,openpyxl,PIL
print('python deps OK')
PY

# 4) Verify render helpers
which pdftoppm
which markitdown
which soffice || true

# 5) Run baseline analytics + deck
python hermes_investor_dd_tonbo/analytics/scripts/analyze_workbook.py
python hermes_investor_dd_tonbo/analytics/scripts/build_investor_dd_deck.py

# 6) Run upgrade workflow
python hermes_investor_dd_tonbo_upgrade/analytics/scripts/run_full_workflow.py
python hermes_investor_dd_tonbo_upgrade/analytics/scripts/enhance_v5.py
python hermes_investor_dd_tonbo_upgrade/analytics/scripts/refine_v6_presentation.py
python hermes_investor_dd_tonbo_upgrade/analytics/scripts/v6_final_polish.py
```

Validation checkpoints:

- final PPT exists at:
  - `C:\Users\gagan\Desktop\hermes-exp\PPT_creation\hermes_investor_dd_tonbo_upgrade\output\Tonbo_Investor_DD_WorkbookDriven_v6_final_polished.pptx`
- QA reports exist and indicate no overdense slides
- proxy audit indicates no no-visual slides in final version

---

## 16) Known gaps and extension recommendations

1. Render hard-gate gap
   - Full render inspection evidence (PDF/image pass logs) is not explicit in current outputs.
   - Recommendation: add deterministic `soffice -> pdftoppm -> visual QA report` stage.

2. Retrieval provenance gap
   - Web/Firecrawl execution artifacts are not explicitly logged in this snapshot.
   - Recommendation: persist retrieval logs and source manifests in `logs/`.

3. Dependency reproducibility gap
   - No `requirements.txt` or environment lockfile present.
   - Recommendation: add pinned env manifest and install script.

4. Chart policy consistency
   - Concentration pie chart exists in baseline while methodology prefers concentration bars.
   - Recommendation: standardize concentration visuals in all scripts.

---

## 17) Output inventory (current terminal state)

Primary final deliverable:

- `C:\Users\gagan\Desktop\hermes-exp\PPT_creation\hermes_investor_dd_tonbo_upgrade\output\Tonbo_Investor_DD_WorkbookDriven_v6_final_polished.pptx`

Primary governance artifacts:

- `...\output\workflow_summary.json`
- `...\output\v5_enhancement_report.json`
- `...\output\v6_rebalance_report.json`
- `...\output\v6_final_polish_report.json`
- `...\output\presentation_cognition_proxy_audit.json`
- `...\grounding_brief.md`
- `...\grounding_brief.pdf`

---

## 18) Summary

This project implements a robust workbook-first autonomous DD presentation platform with strong analytical and narrative iteration discipline. It already demonstrates institutional framing behavior, artifacted QA loops, and modular scripting. The main maturity unlocks from here are:

- render-hard-gated QA with explicit image/PDF evidence
- retrieval provenance logging for web/Firecrawl stages
- dependency lockfiles for reproducibility

With those additions, the system can operate as a fully auditable internal DD presentation engine.