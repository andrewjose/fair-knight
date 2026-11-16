# Air control: running jump, then hold Left mid-air; and a standing jump while holding Right.
import numpy as np, sys
from emu import Emu
ROM=sys.argv[1]
def jump(rom, fk, script, n=60):
    e=Emu(rom); e.n.load(np.load('st_play.npy')); e.run(1)
    for f in range(30): e.poke(0x4F0,e.peek(0x4F0)&~0x20); e.run(1,'R')   # get moving (walk right)
    xs=[]; ys=[]
    for f in range(n):
        if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        for y in range(1,17): e.poke(0x4F0+y,0)        # no enemies in the way
        e.run(1,script(f)); xs.append(e.peek(0x5AF)+256*e.peek(0x583)+e.peek(0x64)+256*e.peek(0x65)); ys.append(e.peek(0x599))
    return xs,ys
run_back=lambda f: 'R+A' if f<4 else ('R' if f<10 else 'L')
stand_r =lambda f: 'A' if f<4 else 'R'
for name,script,pre in [('running jump, then Left',run_back,None),('standing jump, then Right',stand_r,'stand')]:
    print('==',name)
    for tag,rom,fk in [('clean','gng.nes',None),('OFF',ROM,(0x0C,0x80)),('FULL',ROM,(0x00,0x00)),('ASSIST',ROM,(0x04,0x00))]:
        if pre=='stand':
            # stop first: let the walk settle
            pass
        xs,ys=jump(rom,fk,script)
        land=next((i for i in range(8,len(ys)) if ys[i]==184 and ys[i-1]!=184),None)
        print(f'{tag:7s} worldX start {xs[0]} at landing {xs[land] if land else None} (landed f{land})  dX per 6f',[xs[i+6]-xs[i] for i in range(0,48,6)])
