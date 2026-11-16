# Ladder safety: climb the stage-5 ladder (section 11) with enemies off ($EB=1), step off the top.
import numpy as np, sys
from emu import Emu
from rec import grid
def climb(rom, fk, tag, shots=False):
    e=Emu(rom); e.n.load(np.load('st_ladder.npy')); e.run(1)
    log=[];P=[]
    for f in range(200):
        e.poke(0xEB,1)
        for y in range(1,22): e.poke(0x4F0+y,0)
        if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        k='U' if f<100 else ('' if f<106 else ('U' if f<110 else ('R' if f<140 else '')))
        e.run(1,k)
        log.append((f,e.peek(0x599),e.peek(0x4F0)&0x40,e.peek(0x647)))
        if shots and f in (60,100,108,112,120,140): e.shot(f'{tag}{f}.png'); P.append(f'{tag}{f}.png')
    return log,P
for rom,fk,tag in [('gng.nes',None,'c'),(sys.argv[1],(0xFF,0x82),'o'),(sys.argv[1],(0x00,0x00),'k')]:
    log,P=climb(rom,fk,tag,shots=(tag=='k'))
    inv=[f for f,y,b,c in log if b]
    print(tag,'Y path',[y for f,y,b,c in log][::10],'invincible frames',len(inv),inv[:1],inv[-1:])
    if P: grid(P,cols=6)
