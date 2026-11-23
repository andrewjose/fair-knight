"""WEAPON DROP from a clean-ROM state ~96 frames before a stage-1 weapon pickup (st_wd.bin, made by the
stage-1 bot from st_play.bin). Arthur stands still after the pickup.
usage: t_wdrop2.py ROM FKSET GRID.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core; from util import grid
c=Core(sys.argv[1]); c.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'st_wd.bin'),'rb').read())
fk=int(sys.argv[2],16); c.poke(0xFF5A06,0);c.poke(0xFF5A07,0);c.poke(0xFF5A08,0);c.poke(0xFF5A09,0)
P=[]; got=None; trace=[]
for f in range(8700,8700+300):
    k='RIGHT+B' if (f//6)%2 else 'RIGHT'
    if (f//40)%5==4: k+='+A'
    if f>=8797: k=''
    c.poke(0xFF5A00,fk); c.run(1,k); c.poke(0xFFB318,0); c.poke(0xFFB319,100)
    r=c.ram(); o=r[0x9400:0x9460]
    if got is None and r[0xB22C]!=0: got=f
    if got is not None:
        trace.append((f-got,int(o[0])*256+int(o[1]),int(o[4])*256+int(o[5]),o[0x40:0x43].tobytes().hex(),int(o[0xb])))
        if (f-got)%12==0 and len(P)<8: fn=f'/tmp/wd{len(P)}.png'; c.shot(fn,1); P.append(fn)
ax=int(r[0xB200])*256+int(r[0xB201])
for t in trace[::10]: print(*t)
print('final item x',trace[-1][1],'arthur x',ax,'arthur weapon',r[0xB22C],'item weapon',trace[-1][4],'state',trace[-1][3])
grid(P,cols=4,out=sys.argv[3],w=320,h=224)
