from pathlib import Path
from pptx import Presentation
import json

pptx_path = Path(r"C:/Users/gagan/Desktop/hermes+fabric/hermes_tonbo_visual_upgrade/output/Tonbo_Investor_DD_Deck_visual_v4_safe.pptx")
prs = Presentation(str(pptx_path))
W,H = prs.slide_width, prs.slide_height
EMU_PER_IN=914400
safe = {
    'left': int(0.35*EMU_PER_IN),
    'top': int(0.25*EMU_PER_IN),
    'right': W-int(0.35*EMU_PER_IN),
    'bottom': H-int(0.25*EMU_PER_IN)
}
issues=[]
slides=[]
for i,s in enumerate(prs.slides,1):
    si={'slide':i,'shapes':len(s.shapes),'overflow':0,'text_chars':0,'images':0,'charts':0}
    for sh in s.shapes:
        l,t,w,h = sh.left, sh.top, sh.width, sh.height
        r,b = l+w, t+h
        if l<safe['left'] or t<safe['top'] or r>safe['right'] or b>safe['bottom']:
            si['overflow'] += 1
            issues.append({'slide':i,'shape':getattr(sh,'name','shape'),'issue':'outside_safe_bounds'})
        if getattr(sh,'has_text_frame',False) and sh.has_text_frame:
            si['text_chars'] += sum(len(p.text or '') for p in sh.text_frame.paragraphs)
        if sh.shape_type==13: si['images'] += 1
        if getattr(sh,'has_chart',False) and sh.has_chart: si['charts'] += 1
    if si['images']+si['charts']==0:
        issues.append({'slide':i,'issue':'no_visual_anchor'})
    slides.append(si)
out={'deck':str(pptx_path),'safe_margin_inches':0.35,'issues':issues,'slide_stats':slides,'issue_count':len(issues)}
out_path=pptx_path.parent/'layout_safety_qa_v4.json'
out_path.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(out_path)
print('issue_count',len(issues))
