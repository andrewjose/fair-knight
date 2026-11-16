# Endgame: stage 6 (section 12, $CF=5). Shows the original send-back rule and the ENDGAME AID cross.
import numpy as np, sys
from stagesel import goto
from emu import Emu
from rec import grid
ROM=sys.argv[1]
def run(rom, fk, tag, walk_to_cross=False):
    e=goto(rom,12,700,fk)
    if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    spawned=None; P=[]
    for f in range(400):
        e.poke(0x4F0,e.peek(0x4F0)&~0x20)
        for y in range(1,17):
            if not (e.peek(0x631+y)==0x10 and e.peek(0x61D+y)==9): e.poke(0x4F0+y,0)   # clear enemies, keep crosses
        k=''
        if walk_to_cross and spawned is not None:
            cx=e.peek(0x5AF+spawned[1]); ax=e.peek(0x5AF)
            k='R' if cx>ax+4 else ('L' if cx<ax-4 else '')
        e.run(1,k)
        if spawned is None:
            for y in range(1,17):
                if e.peek(0x4F0+y) and e.peek(0x631+y)==0x10 and e.peek(0x61D+y)==9:
                    spawned=(f,y,e.peek(0x5AF+y),e.peek(0x599+y),e.peek(0x5AF),e.peek(0x599)); e.shot(f'eg_{tag}.png')
    w=e.peek(0x53A)
    # finish the stage now (Action Replay code $BF=1) and see where the game goes
    e.poke(0xBF,1); sec=[]
    for f in range(900):
        e.run(1); 
        if e.peek(0xBF): e.poke(0xBF,1)
        s=e.peek(0xAC)
        if not sec or sec[-1]!=s: sec.append(s)
        if len(sec)>1: e.poke(0xBF,0)
    e.shot(f'eg_{tag}_after.png')
    return spawned,hex(w),sec,e.peek(0xCF)
for tag,rom,fk,walk in [('clean','gng.nes',None,False),('orig',ROM,(0xFF,0x82),False),('knight',ROM,(0,0),True)]:
    sp,w,sec,cf=run(rom,fk,tag,walk)
    print(f'{tag:7s} cross spawned (frame,slot,itemX,itemY,arthurX,arthurY)={sp} weapon at clear={w} section path {sec} CF after={cf}')
