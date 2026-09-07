import sys
from pathlib import Path
from sexpr import *
root=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
for libid in sys.argv[1:]:
 lib,name=libid.split(':'); n=parse((root/'symbols'/(lib+'.kicad_sym')).read_text()); s=next(x for x in allof(n,'symbol') if x[1]==name)
 print(libid,'extends',get(s,'extends'),'fp',next((x[2] for x in allof(s,'property') if x[1]=='Footprint'),''))
 for p in walk(s,'pin'):print(get(p,'number')[1],get(p,'name')[1],p[1],get(p,'at')[1:])
