"""Simplified SOT-89-5 envelope for visualization only; not a certified supplier model."""
from pathlib import Path
from design import ROOT
out=ROOT/'lib/3dmodels/custom/SOT-89-5-envelope.step';out.parent.mkdir(parents=True,exist_ok=True)
ents=[]
def E(s):
 ents.append(s);return '#'+str(len(ents))
app=E("APPLICATION_CONTEXT('configuration controlled 3d designs of mechanical parts and assemblies')")
ctx=E(f"PRODUCT_CONTEXT('',{app},'mechanical')")
prod=E(f"PRODUCT('SOT-89-5 envelope','SOT-89-5 envelope','Simplified rectangular model; not for mechanical release',({ctx}))")
formation=E(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
dctx=E(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app},'design')")
pdef=E(f"PRODUCT_DEFINITION('design','',{formation},{dctx})")
shape=E(f"PRODUCT_DEFINITION_SHAPE('','',{pdef})")
mm=E('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')
rad=E('(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))')
sr=E('(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())')
unc=E(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),{mm},'distance_accuracy_value','')")
gctx=E(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) GLOBAL_UNIT_ASSIGNED_CONTEXT(({mm},{rad},{sr})) REPRESENTATION_CONTEXT('','3D'))")
solids=[];styles=[]
def box(name,bounds,color):
 x,y,z,X,Y,Z=bounds
 points=[E("CARTESIAN_POINT('',(%s,%s,%s))"%tuple(f'{v:.5f}' for v in pt)) for pt in [(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]]
 coords=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
 vertices=[E(f"VERTEX_POINT('',{point})") for point in points];edges={};faces=[]
 import math
 for idx in [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
  oriented=[]
  for ia,ib in zip(idx,idx[1:]+idx[:1]):
   key=tuple(sorted((ia,ib)))
   if key not in edges:
    pa,pb=coords[ia],coords[ib];delta=[b-a for a,b in zip(pa,pb)];length=math.sqrt(sum(v*v for v in delta));direction=E("DIRECTION('',(%s))"%','.join(str(v/length) for v in delta));vector=E(f"VECTOR('',{direction},{length})");line=E(f"LINE('',{points[ia]},{vector})");edge=E(f"EDGE_CURVE('',{vertices[ia]},{vertices[ib]},{line},.T.)");edges[key]=(ia,edge)
   origin,edge=edges[key];oriented.append(E(f"ORIENTED_EDGE('',*,*,{edge},{'.T.' if origin==ia else '.F.'})"))
  loop=E("EDGE_LOOP('',(%s))"%','.join(oriented));bound=E(f"FACE_OUTER_BOUND('',{loop},.T.)")
  pa,pb,pc=[coords[i] for i in idx[:3]];u=[b-a for a,b in zip(pa,pb)];v=[c-a for a,c in zip(pa,pc)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  def direction(v):
   l=math.sqrt(sum(x*x for x in v));return E("DIRECTION('',(%s))"%','.join(str(x/l) for x in v))
  dn=direction(n);du=direction(u);axis=E(f"AXIS2_PLACEMENT_3D('',{points[idx[0]]},{dn},{du})");plane=E(f"PLANE('',{axis})");faces.append(E(f"ADVANCED_FACE('',({bound}),{plane},.T.)"))
 shell=E("CLOSED_SHELL('',(%s))"%','.join(faces));solid=E(f"MANIFOLD_SOLID_BREP('{name}',{shell})");solids.append(solid)
 rgb=E("COLOUR_RGB('',%s)"%','.join(str(v) for v in color));fill=E(f"FILL_AREA_STYLE_COLOUR('',{rgb})");area=E(f"FILL_AREA_STYLE('',({fill}))");sfill=E(f"SURFACE_STYLE_FILL_AREA({area})");side=E(f"SURFACE_SIDE_STYLE('',({sfill}))");usage=E(f"SURFACE_STYLE_USAGE(.BOTH.,{side})");assign=E(f"PRESENTATION_STYLE_ASSIGNMENT(({usage}))");styles.append(E(f"STYLED_ITEM('',({assign}),{solid})"))
box('body',(-1.25,-2.25,.18,1.25,2.25,1.6),(.12,.12,.12))
for x in [-1,1]:
 for y in [-1.5,1.5]:box('lead',(min(x*1.1,x*2.25),y-.22,.02,max(x*1.1,x*2.25),y+.22,.18),(.7,.7,.72))
box('ground tab',(-2.25,-.7,.02,1.1,.7,.18),(.7,.7,.72))
rep=E("ADVANCED_BREP_SHAPE_REPRESENTATION('',(%s),%s)"%(','.join(solids),gctx));E(f'SHAPE_DEFINITION_REPRESENTATION({shape},{rep})');E("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(%s),%s)"%(','.join(styles),gctx))
out.write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Simplified SOT89-5 envelope'),'2;1');\nFILE_NAME('SOT-89-5-envelope.step','2026-09-06T00:00:00',('Rev B project'),('HAW project'),'','','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"+'\n'.join(f'#{i+1} = {v};' for i,v in enumerate(ents))+"\nENDSEC;\nEND-ISO-10303-21;\n")
print(out)
