from pathlib import Path
s=Path(__file__).with_name('finish_route.py').read_text();exec(s.split('errors=json.loads')[0])
for net,pt in [('USB_500',(22.75,24.4375)),('CHG_N',(24.4375,23.75))]:
 a=obstacles(net,.15);vv=obstacles(net,.15,True);i,j=idx(*pt)
 print(net,'source',pt,'block',a[:,j,i],flush=True)
 candidates=[]
 for dx in range(-50,51):
  for dy in range(-50,51):
   if not vv[j+dy,i+dx]:candidates.append((math.hypot(dx,dy)*G,((i+dx)*G,(j+dy)*G)))
 print(sorted(candidates)[:8],flush=True)
 for dist,goal in sorted(candidates)[:4]:
  try:route_one(net,[(*pt,(0,)),(*goal,(0,1))],.15);via(net,goal);print('ESCAPED',goal,flush=True);break
  except Exception as e:print('cannot escape',goal,flush=True)
p.SaveBoard(str(PTH),b)
