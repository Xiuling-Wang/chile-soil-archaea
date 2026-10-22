"""Recompose PRE-MANUAL vector plots using an explicit author-layout recipe.
Text origins/page sizes are frozen measurements in layout_topcoords.json.
The supplied vector inputs are hash-checked before layout recomposition.
No statistics, taxa, observations, curves, tree branches or bubble sizes recomputed.
"""
from pathlib import Path
import pymupdf as f
import json,hashlib
R=Path(__file__).resolve().parent;Q=R/'inputs';OUT=R/'output';OUT.mkdir(exist_ok=True)
LAY=json.loads((Q/'layout_topcoords.json').read_text());LOG=[]
for n,h in json.loads((R/'INPUT_SHA256.json').read_text()).items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
for name in ['Fig1','Fig2','Fig3','Fig4','FigS1','FigS2','FigS3','FigS4','FigS5']:
 src=f.open(Q/'code_inputs'/f'{name}.pdf');s=src[0];doc=f.open();w,h=LAY[name]['manual']['size'][2:];p=doc.new_page(width=w,height=h);pieces=[];freshdocs=[]
 def piece(box,dx=0,dy=0):
  clip=f.Rect(box);target=clip+f.Rect(dx,dy,dx,dy);p.show_pdf_page(target,src,0,clip=clip,keep_proportion=False);pieces.append({'clip':list(clip),'translate':[dx,dy]})
 def line(text,kind='source',index=0):
  return [l for l in LAY[name][kind]['text'] if l['text']==text][index]
 def box(text,index=0):return f.Rect(line(text,index=index)['bbox'])+(-.4,-.5,.4,.5)
 def label(text,index=0,dx=0,dy=0):
  # A separate PDF instance avoids sharing a Form XObject mutated by redaction.
  clip=box(text,index);fresh=f.open(Q/'code_inputs'/f'{name}.pdf')
  p.show_pdf_page(clip+f.Rect(dx,dy,dx,dy),fresh,0,clip=clip,keep_proportion=False)
  freshdocs.append(fresh)
 def move(text,index=0,target_index=None,base=(0,0)):
  old=line(text,index=index);new=line(text,'manual',index if target_index is None else target_index)
  a=old['spans'][0]['origin'];b=new['spans'][0]['origin'];erase=box(text,index)+f.Rect(base[0],base[1],base[0],base[1]);p.add_redact_annot(erase,fill=False,cross_out=False);p.apply_redactions(images=0,graphics=0,text=0)
  label(text,index,b[0]-a[0],b[1]-a[1])
 def new_manual_label(text):
  l=line(text,'manual');sp=l['spans'][0];font='hebo' if 'Bold' in sp['font'] else 'helv';p.insert_text(sp['origin'],text,fontname=font,fontsize=sp['size'],color=(0,0,0))
 if name=='Fig1':
  piece(s.rect)
  # Fig1's labels are re-set as text instead of re-stamped from a clipped region: a clip re-stamp leaves a
  # sliver of the source page's own white background and a copy of the panel border beside the shifted
  # glyphs (the white strip and short dark bar the author reported next to 'gradient'), and it embeds the
  # map raster once per label. 'Santa Gracia' is re-set because the redaction that clears the old 'Andes'
  # reaches into it; 'Andes' lands at the author position, clear of both site labels. Authority: script/238.
  def pick(t,kind,ny=None):
   c=[l for l in LAY[name][kind]['text'] if l['text']==t]
   return c[0] if ny is None else sorted(c,key=lambda l:abs(l['spans'][0]['origin'][1]-ny))[0]
  JOB=[('Climate',None,None),('gradient',None,None),('B',None,None),('Soil depth (cm)',None,90),
       ('Andes',None,78.0),('Santa Gracia',100.0,None)]
  for t,ny,_ in JOB:p.add_redact_annot(f.Rect(pick(t,'source',ny)['bbox'])+(-.4,-.5,.4,.5),fill=False,cross_out=False)
  p.add_redact_annot((f.Rect(pick('DNA pool','manual')['bbox'])|f.Rect(pick('DNA pools','manual')['bbox']))+(-.6,-.8,.6,.8),fill=False,cross_out=False)
  p.apply_redactions(images=0,graphics=0,text=0)
  for t,ny,rot in JOB+[('DNA pools',None,None)]:
   sp=pick(t,'manual',ny)['spans'][0];c=sp['color'];o=f.Point(*sp['origin'])
   fn='hebi' if ('Bold' in sp['font'] and 'Oblique' in sp['font']) else 'hebo' if 'Bold' in sp['font'] else 'heit' if 'Oblique' in sp['font'] else 'helv'
   p.insert_text(o,t,fontname=fn,fontsize=sp['size'],color=(((c>>16)&255)/255,((c>>8)&255)/255,(c&255)/255),**({'morph':(o,f.Matrix(rot))} if rot else {}))
 elif name=='Fig2':
  piece([0,18,538,180],0,-4.54)
  label('Relative abundance (%)',dx=0,dy=-1.54);label('A',dx=3,dy=-1.54);label('B',dx=4.97,dy=-17.75)
  piece([0,324,538,667],0,-84.54)
  new_manual_label('ASV ID   Class; Order')
  label('Reference source',0,-14.9,-27.42);label('Sites × pools',0,1.79,-52.15)
  label('Samples',0,-.33,-48.94);label('detected',0,-.33,-47.74);label('Functional annotation',0,.64,-27.34)
  piece([289,283,361,320],0,-79.54)
  label('Sites × pools',0,1.79,-52.15)
  piece([199,705,275,798],-8.27,-117.14)
  piece([310,705,361,798],-33.77,-112.72)
  piece([390,697,477,798],-54.32,-115.22)
  piece([48,729,130,758],-26.88,-141.55)
 elif name=='Fig3':
  # The two panels retain unit scale: narrow the canvas by removing margins.
  piece([65,30,270,234],-39.28,-7.36)
  label('Procrustes axis 2',0,-39.28,-19.36);label('Procrustes axis 1',0,-56.28,-7.36)
  piece([307,18,538,249],-56.28,-7.36)
  label('A',0,-2.75,-2.31);label('B',0,-56.28,-2.36)
  piece([200,258,365,281],-152.70,-17.96)
  # Relocate statistics relative to their new panel position.
  move('r = 0.985',base=(-39.28,-7.36));move('p = 0.0001',base=(-39.28,-7.36))
  move('DNA pools',0,0,base=(-56.28,-7.36))
 elif name=='Fig4':
  piece([0,0,538,225])
  piece([100,226,510,243],-41.67,18.64)
  piece([190,243,410,260],-134.12,-15.97)
  piece([0,277,538,495],0,5)
  move('C',base=(0,5));move('D',base=(0,5))
 elif name=='FigS1':
  piece([0,23,522,241],0,-10.51)
  piece([0,275,522,522],0,-10.51)
  label('A',0,0,2.49);label('B',0,0,.49)
  label('Relative abundance (%)',0,0,-7.51);label('Relative abundance (%)',1,0,-6.51)
  piece([0,525,522,567],0,-17.51)
  for t in ['AZ','SG','LC','NA']:
   for idx in [0,1]:move(t,idx,base=(0,-10.51))
 elif name=='FigS2':
  piece([22,0,538,186],0,-6);piece([0,20,22,171],0,-6)
  label('A',0,0,3)
  move('Sequencing depth (reads)',base=(0,-6))
  piece([0,200,538,391],0,22);label('B',0,0,31)
  piece([65,400,290,417],-22.91,-216.73)
  # Compact legend uses the visible corrected keys from the earlier code output.
  piece([66,418,113,432],-25,14)
  piece([130,418,237,432],-36,14)
  piece([0,447,538,494],0,10)
 elif name=='FigS3':
  piece([0,0,538,204]);piece([200,208,370,234],0,-3)
  piece([0,249,538,489],0,8);label('B',0,0,16)
  piece([0,499,538,553])
 elif name=='FigS4':
  piece([0,144,538,674],0,-95.17)
  new_manual_label('ASV ID  Class; Order')
  label('Reference source',0,-18.28,-51.21);label('Sites × pools',0,-9.18,-67.37)
  label('Samples',0,-.81,-57.25);label('detected',0,-.82,-57.25);label('Functional annotation',0,.8,-38.48)
  piece([276,102,350,143],0,-90.16)
  label('Sites × pools',0,-9.18,-67.37)
  piece([199,688,290,808],-18,-108.16)
  piece([325,688,375,766],-54.53,-100.77)
  piece([411,678,495,773],-85.04,-94.04)
  piece([25,704,110,734],-7.39,-118.23)
  piece([0,827,538,879],0,-119.16)
 elif name=='FigS5':
  piece([0,166,538,650],0,-109.88)
  new_manual_label('ASV ID Class; Order')
  label('Reference source',0,-31.61,-56.88);label('Sites × pools',0,-9.7,-74.88)
  label('Samples',0,2.83,-69.43);label('detected',0,2.83,-69.43)
  label('Functional annotation',0,0,-42.8)
  piece([300,125,383,165],0,-106.88)
  piece([199,670,290,737],0,-129.88)
  piece([325,670,375,752],-28.88,-129.57)
  piece([411,660,495,759],-55.46,-121.16)
  piece([25,692,110,717],-2.11,-139.71)
  piece([0,827,538,868],0,-191.88)
 dest=OUT/f'{name}.pdf';doc.save(dest,garbage=4,deflate=True);doc.close();src.close()
 for fresh in freshdocs:fresh.close()
 LOG.append({'figure':name,'input':str(Q/'code_inputs'/f'{name}.pdf'),'output':str(dest),'page_size':[w,h],'pieces':pieces,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(OUT/'layout_receipt.json').write_text(json.dumps({'method':'frozen vector PDF recomposition; no model refit','figures':LOG},indent=2))
print(OUT)
