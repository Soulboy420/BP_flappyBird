from pathlib import Path
exec(Path(__file__).with_name('route.py').read_text().split('# Deliberately planned')[0])
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):obsitems.append((t.GetNetname(),(0,1),'circle',(*xy(t.GetPosition()),mm(t.GetWidth())/2)))
 else:obsitems.append((t.GetNetname(),(0 if t.GetLayer()==F else 1,),'seg',(*xy(t.GetStart()),*xy(t.GetEnd()),mm(t.GetWidth()))))
for n,pt in [('NTC',(20.6625,22.25)),('USB_CONN_D+', (81.62,12.25)),('USB_500',(22.75,25.3375)),('VBAT',(20.6625,22.75)),('ISET',(22.25,20.6625))]:
 print('\nBLOCK',n,pt)
 i,j=map(lambda x:int(round(x/G)),pt)
 for nn,ls,kind,data in obsitems:
  if nn==n or 0 not in ls:continue
  a=np.zeros((NY,NX),bool);geom_fill(a,kind,data,.075+.15)
  if a[j,i]:print(nn,kind,data)
