from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.dml.color import RGBColor
import matplotlib.pyplot as plt

BASE = Path(r"C:/Users/gagan/Desktop/hermes+fabric/hermes_tonbo_visual_upgrade")
OUT = BASE / "output"
SEL = BASE / "assets_selected"
CH = BASE / "output" / "charts"
CH.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# metrics
rev = [22.84, 26.75, 65.25]
rep_ebitda = [None, 0.07, 3.74]
adj_ebitda = [None, None, -3.82]
qoe_labels = ["Reported EBITDA", "Capex rev", "ESOP", "Inventory", "Provision", "Other", "Adjusted"]
qoe_vals = [3.74, -2.90, -2.18, -1.87, -0.34, -0.17, -3.82]
conc = {"ALT revenue share":49, "MN105-AL SKU":68}
wc = {"DSO":51, "DIO":137, "DPO":162, "CCC":26}

# chart assets
plt.figure(figsize=(8,4.2)); plt.plot(["FY23","FY24","FY25"], rev, marker='o', linewidth=3,color='#1f4e79'); plt.title('Revenue trajectory (₹ Cr)'); plt.grid(alpha=0.25); plt.tight_layout(); plt.savefig(CH/'rev.png',dpi=220); plt.close()
plt.figure(figsize=(9,4.6)); colors=['#1f4e79']+['#b85450']*5+['#6aa84f']; plt.bar(qoe_labels,qoe_vals,color=colors); plt.axhline(0,color='black',lw=0.8); plt.xticks(rotation=18,ha='right'); plt.title('QoE bridge FY25 (₹ Cr)'); plt.tight_layout(); plt.savefig(CH/'qoe.png',dpi=220); plt.close()
plt.figure(figsize=(7.8,4.3)); plt.bar(list(conc.keys()),list(conc.values()),color=['#c00000','#f39c12']); plt.ylim(0,80); plt.title('Concentration stack (%)'); plt.tight_layout(); plt.savefig(CH/'conc.png',dpi=220); plt.close()
plt.figure(figsize=(8,4.2)); plt.bar(list(wc.keys()),list(wc.values()),color=['#2e75b6','#5b9bd5','#1f4e79','#70ad47']); plt.title('Working-capital mechanics (days)'); plt.tight_layout(); plt.savefig(CH/'wc.png',dpi=220); plt.close()

imgs = sorted([p for p in SEL.glob('anchor_*')])

def pic(i):
    if not imgs:
        return None
    return str(imgs[i % len(imgs)])

prs = Presentation()
W,H = prs.slide_width, prs.slide_height
C_TITLE = RGBColor(16,33,62)
C_BODY = RGBColor(40,40,40)

def add_title(slide,text,top=0.2,left=0.4,width=12.5):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(0.8))
    p = tb.text_frame.paragraphs[0]
    p.text = text; p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = C_TITLE

def add_panel(slide,left,top,w,h,title,items):
    shp=slide.shapes.add_shape(1,Inches(left),Inches(top),Inches(w),Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb=RGBColor(245,247,250); shp.line.color.rgb=RGBColor(220,225,232)
    tf=shp.text_frame; tf.clear(); p=tf.paragraphs[0]; p.text=title; p.font.bold=True; p.font.size=Pt(16); p.font.color.rgb=C_TITLE
    for it in items:
        q=tf.add_paragraph(); q.text=f"• {it}"; q.font.size=Pt(13); q.font.color.rgb=C_BODY

# 1 cover full bleed image
s=prs.slides.add_slide(prs.slide_layouts[6])
if pic(0): s.shapes.add_picture(pic(0),0,0,width=W,height=H)
overlay=s.shapes.add_shape(1,Inches(0),Inches(0),Inches(13.33),Inches(1.6)); overlay.fill.solid(); overlay.fill.fore_color.rgb=RGBColor(8,17,35); overlay.fill.transparency=20; overlay.line.fill.background()
add_title(s,'Tonbo Imaging | Investor Diligence Underwriting Deck',top=0.35,left=0.5,width=12.4)

# 2 exec dashboard
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Executive underwriting dashboard')
s.shapes.add_picture(str(CH/'rev.png'),Inches(0.4),Inches(1.2),width=Inches(5.9))
s.shapes.add_picture(str(CH/'conc.png'),Inches(6.6),Inches(1.2),width=Inches(6.2))
add_panel(s,0.4,4.2,12.4,2.9,'IC bottom line',[
 'Growth is real; adjusted earnings remain negative after normalization.',
 'Concentration stack is too high for clean underwriting sign-off.',
 'Proceed only with milestone-gated capital and control remediation.'
])

# 3 image-led business context
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Operational context: sensing systems in deployment reality')
if pic(1): s.shapes.add_picture(pic(1),Inches(0.3),Inches(1.0),width=Inches(8.2),height=Inches(5.9))
add_panel(s,8.8,1.2,4.2,5.4,'Visual interpretation',[
 'Business should be read as deployment system provider, not pure software.',
 'Execution risk is tied to hardware lifecycle, procurement cadence, and field reliability.',
 'Use operational realism in all valuation and growth assumptions.'
])

# 4 QoE bridge feature
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Quality of earnings bridge: reported vs investable economics')
s.shapes.add_picture(str(CH/'qoe.png'),Inches(0.4),Inches(1.25),width=Inches(8.0))
add_panel(s,8.6,1.2,4.2,5.5,'Underwriting consequence',[
 'FY25 EBITDA sign flips after normalization.',
 'Multiple on reported EBITDA is analytically unsafe.',
 'Path-to-profitability must be evidenced quarter-by-quarter.'
])

# 5 concentration matrix visual
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Concentration risk matrix (customer + SKU + vendor)')
# draw 2x2 matrix
box=s.shapes.add_shape(1,Inches(0.6),Inches(1.4),Inches(7.2),Inches(4.9)); box.fill.solid(); box.fill.fore_color.rgb=RGBColor(252,252,252); box.line.color.rgb=RGBColor(210,210,210)
vline=s.shapes.add_shape(1,Inches(4.15),Inches(1.4),Inches(0.02),Inches(4.9)); vline.fill.solid(); vline.fill.fore_color.rgb=RGBColor(190,190,190); vline.line.fill.background()
hline=s.shapes.add_shape(1,Inches(0.6),Inches(3.85),Inches(7.2),Inches(0.02)); hline.fill.solid(); hline.fill.fore_color.rgb=RGBColor(190,190,190); hline.line.fill.background()
for (x,y,t,c) in [(1.0,1.8,'ALT Group\n49% rev',RGBColor(192,0,0)),(4.5,1.8,'MN105-AL\n68% SKU',RGBColor(237,125,49)),(1.0,4.2,'Branch/Vendor\ndependency',RGBColor(255,192,0)),(4.5,4.2,'Correlated\ndownside risk',RGBColor(112,173,71))]:
    tbox=s.shapes.add_textbox(Inches(x),Inches(y),Inches(2.8),Inches(1.5)); p=tbox.text_frame.paragraphs[0]; p.text=t; p.font.bold=True; p.font.size=Pt(16); p.font.color.rgb=c
if pic(2): s.shapes.add_picture(pic(2),Inches(8.2),Inches(1.4),width=Inches(4.6),height=Inches(3.0))
add_panel(s,8.2,4.5,4.6,1.8,'Risk stance',['Treat concentration as structural, not temporary noise.'])

# 6 working-capital dashboard
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Working-capital mechanics and liquidity fragility')
s.shapes.add_picture(str(CH/'wc.png'),Inches(0.6),Inches(1.3),width=Inches(6.5))
if pic(3): s.shapes.add_picture(pic(3),Inches(7.4),Inches(1.3),width=Inches(5.4),height=Inches(2.8))
add_panel(s,7.4,4.3,5.4,2.0,'Interpretation',[
 'Current CCC is DPO-supported; normalize payables in downside case.',
 'Liquidity runway can compress quickly under vendor-term reset.'
])

# 7 governance heatmap
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Governance/control heatmap')
labels=[('Accounting policy', 'High'),('Inventory control','High'),('Tax/GST hygiene','High'),('Close discipline','Medium'),('Forecast reliability','Medium')]
for i,(a,b) in enumerate(labels):
    y=1.4+i*0.95
    sh=s.shapes.add_shape(1,Inches(0.8),Inches(y),Inches(5.8),Inches(0.75)); sh.fill.solid(); sh.fill.fore_color.rgb=RGBColor(245,247,250); sh.line.color.rgb=RGBColor(220,220,220)
    t=sh.text_frame; t.text=f'{a}'; t.paragraphs[0].font.size=Pt(14)
    risk=RGBColor(192,0,0) if b=='High' else RGBColor(237,125,49)
    tag=s.shapes.add_shape(1,Inches(5.2),Inches(y+0.08),Inches(1.2),Inches(0.55)); tag.fill.solid(); tag.fill.fore_color.rgb=risk; tag.line.fill.background(); tag.text_frame.text=b; tag.text_frame.paragraphs[0].font.color.rgb=RGBColor(255,255,255); tag.text_frame.paragraphs[0].font.bold=True; tag.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
if pic(4): s.shapes.add_picture(pic(4),Inches(7.1),Inches(1.3),width=Inches(5.5),height=Inches(4.9))

# 8 scenario panels
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Scenario underwriting: base / downside / severe')
for i,(name,color,txt) in enumerate([
 ('Base',RGBColor(112,173,71),'Moderate growth with partial control fixes'),
 ('Downside',RGBColor(237,125,49),'DPO normalization + slower collections'),
 ('Severe',RGBColor(192,0,0),'Concentration shock + compliance cash outflow')]):
    x=0.6+i*4.25
    sh=s.shapes.add_shape(1,Inches(x),Inches(1.7),Inches(4.0),Inches(4.6)); sh.fill.solid(); sh.fill.fore_color.rgb=RGBColor(250,250,250); sh.line.color.rgb=color
    tf=sh.text_frame; tf.text=name; tf.paragraphs[0].font.bold=True; tf.paragraphs[0].font.size=Pt(22); tf.paragraphs[0].font.color.rgb=color
    p=tf.add_paragraph(); p.text=txt; p.font.size=Pt(13)
if pic(5): s.shapes.add_picture(pic(5),Inches(0.6),Inches(6.0),width=Inches(12.2),height=Inches(1.0))

# 9 capability/ecosystem map
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Capability stack and ecosystem positioning')
for i,(t,x) in enumerate([('Sensor Hardware',0.8),('Embedded Compute',3.3),('Analytics/Control',5.8),('Deployment Platform',8.3)]):
    sh=s.shapes.add_shape(1,Inches(x),Inches(2.6),Inches(2.1),Inches(1.5)); sh.fill.solid(); sh.fill.fore_color.rgb=RGBColor(31,78,121); sh.line.fill.background();
    tf=sh.text_frame; tf.text=t; tf.paragraphs[0].font.color.rgb=RGBColor(255,255,255); tf.paragraphs[0].font.bold=True; tf.paragraphs[0].font.alignment=PP_ALIGN.CENTER
if pic(6): s.shapes.add_picture(pic(6),Inches(0.8),Inches(1.2),width=Inches(3.0),height=Inches(1.2))
if pic(7): s.shapes.add_picture(pic(7),Inches(9.8),Inches(4.4),width=Inches(2.9),height=Inches(1.8))
add_panel(s,0.8,4.5,8.7,1.8,'Strategic read',['Differentiation must convert into diversified revenue, not concentrated growth.'])

# 10 IC decision panel
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'IC decision panel and conditions precedent')
add_panel(s,0.6,1.5,6.2,4.8,'Go / no-go logic',[
 'GO only with milestone-gated deployment.',
 'Hard CPs: QoE closure, control remediation, compliance tracker.',
 'Valuation anchored to scenario-weighted outcomes, not headline EBITDA.'
])
if pic(8): s.shapes.add_picture(pic(8),Inches(7.1),Inches(1.5),width=Inches(5.7),height=Inches(4.8))

# 11 100-day plan workflow visual
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Post-close 100-day value-protection workflow')
steps=['Monthly close hardening','Concentration PMO','Cash cockpit','Compliance closure office']
for i,st in enumerate(steps):
    x=0.8+i*3.0
    sh=s.shapes.add_shape(1,Inches(x),Inches(3.0),Inches(2.6),Inches(1.2)); sh.fill.solid(); sh.fill.fore_color.rgb=RGBColor(242,242,242); sh.line.color.rgb=RGBColor(160,160,160)
    sh.text_frame.text=st; sh.text_frame.paragraphs[0].font.size=Pt(12); sh.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
    if i<3:
        ar=s.shapes.add_shape(1,Inches(x+2.6),Inches(3.52),Inches(0.35),Inches(0.05)); ar.fill.solid(); ar.fill.fore_color.rgb=RGBColor(100,100,100); ar.line.fill.background()
if pic(9): s.shapes.add_picture(pic(9),Inches(0.8),Inches(1.1),width=Inches(12.0),height=Inches(1.5))

# 12 sources + evidence
s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,'Evidence boundaries and source traceability')
if pic(0): s.shapes.add_picture(pic(0),Inches(8.3),Inches(1.5),width=Inches(4.5),height=Inches(4.8))
add_panel(s,0.8,1.5,7.2,4.8,'Primary evidence',[
 'Workbook metrics + bridge combined context + Hermes synthesis output.',
 'Firecrawl-based page retrieval and contextual image acquisition logs retained.',
 'Visuals are context-grounding aids; core underwriting rests on numeric evidence.',
 'Where imagery provenance is non-official, source URL is retained in image manifest.'
])

out = OUT / 'Tonbo_Investor_DD_Deck_visual_v3.pptx'
prs.save(out)
print(out)
