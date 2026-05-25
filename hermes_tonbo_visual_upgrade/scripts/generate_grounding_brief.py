from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE = Path(r"C:/Users/gagan/Desktop/hermes+fabric/hermes_tonbo_visual_upgrade")
RESEARCH = BASE / "research"
RESEARCH.mkdir(parents=True, exist_ok=True)

md = '''# Tonbo Imaging Contextual Intelligence Brief (for Visual Retrieval + Investor Framing)

Date: 2026-05-25
Scope: 1–2 page grounding brief for image selection and slide storytelling in an investor DD deck.
Confidence: Medium (official-site text and bridge evidence are strong; public web image access is partially constrained in this environment).

## 1) Company/domain grounding
Tonbo Imaging operates in the electro-optical/infrared (EO/IR) and advanced sensing domain, with defense and security relevance. The business context is imaging systems, sensing payloads, thermal/night-vision-adjacent capability, and deployment-grade hardware/software integration.

Why this matters for visual retrieval:
- imagery should prioritize field-deployment realism (platform integration, sensor payload context, monitoring environments),
- product visuals should show device/system context, not isolated glamour shots,
- ecosystem visuals should map defense optics stack (sensor → compute → deployment).

## 2) Business-model and operating-context hypotheses (investor lens)
Evidence from workbook+bridge context indicates a company with rapid commercial growth but material execution and earnings-quality fragility.
Likely operating model includes:
- hardware-heavy productization cycle,
- project/procurement-driven commercial cadence,
- concentration exposure across customer/SKU/vendor vectors,
- working-capital dependence on supplier terms.

Visual implication:
- slides should pair product/deployment imagery with risk dashboards (QoE, concentration, WC mechanics),
- avoid abstract “AI” visuals and generic stock motifs.

## 3) Deployment and application context (image taxonomy)
Priority visual taxonomy for this deck:
1. Official company visuals (homepage/product pages, if retrievable)
2. EO/IR sensor deployment context (field monitoring, platform integration)
3. Thermal-imaging equipment visuals (close + in-use)
4. Defense/security operations context (real-world environment, non-stylized)
5. Manufacturing/process visuals (hardware assembly/test context)

Filter guidance:
- accept only high-resolution, non-watermarked, context-rich visuals,
- reject decorative abstract backgrounds and low-information graphics,
- reject low-trust, unverifiable synthetic-looking imagery.

## 4) Investor-relevant analytical framing (to pair with visuals)
Bridge semantic outputs repeatedly highlight:
- QoE inversion (reported EBITDA positive to adjusted EBITDA negative),
- concentration stack (customer + SKU + vendor),
- WC sensitivity (DPO-dependent liquidity optics),
- control/compliance debt.

Visual architecture implications:
- use asymmetric layouts: large image anchor + underwriting panel,
- use matrix/risk heatmap layouts over bullet-heavy pages,
- use image-led section transitions to prevent memo-like slide rhythm.

## 5) Terms and retrieval keywords (for contextual search)
EO/IR, thermal imaging, infrared sensing, night-vision, surveillance payload, electro-optical systems, defense optics integration, field deployment sensing, sensor platform integration, thermal camera deployment, ISR imaging stack.

## 6) Known constraints in this run
- Search-provider integration for `web_search` is unavailable in this runtime.
- Official-site image extraction yielded limited directly retrievable assets (site structure and asset-delivery behavior constrained extraction).
- Firecrawl API is functional and used, but source-page image density remained limited.

Mitigation used:
- combine official-site captures with ecosystem-context imagery,
- increase analytical visual density (dashboards/heatmaps/matrices) so every substantive slide still has a strong visual anchor.

## 7) How this brief is used operationally
This brief is the retrieval and selection policy for image acquisition and slide composition:
- prioritize operational realism,
- prioritize investor comprehension over decoration,
- ensure each slide combines either chart-driven insight or context-rich imagery.
'''

md_path = RESEARCH / 'contextual_company_intelligence_brief.md'
md_path.write_text(md, encoding='utf-8')

pdf_path = RESEARCH / 'contextual_company_intelligence_brief.pdf'
c = canvas.Canvas(str(pdf_path), pagesize=A4)
width, height = A4
x, y = 40, height - 40
c.setFont('Helvetica-Bold', 13)
c.drawString(x, y, 'Tonbo Imaging Contextual Intelligence Brief')
y -= 24
c.setFont('Helvetica', 9)
for line in md.splitlines():
    if y < 50:
        c.showPage()
        y = height - 40
        c.setFont('Helvetica', 9)
    text = line if len(line) <= 125 else line[:122] + '...'
    c.drawString(x, y, text)
    y -= 12
c.save()

print(md_path)
print(pdf_path)
