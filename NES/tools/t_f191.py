# Inspect the single frame-191 'flags' difference: full-RAM diff at frames 189-193, and where the CPU was at the frame cut.
import numpy as np
from emu import Emu
def go(rom,fk,upto):
    rng=np.random.default_rng(0); e=Emu(rom); e.n.load(np.load('st_play.npy'))
    if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    e.run(1); snaps={}
    for f in range(upto):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.poke(0x4F0,e.peek(0x4F0)&~0x20)
        k=['R'] if rng.random()<0.8 else ['L']
        if f%8<3: k.append('B')
        if rng.random()<0.03: k.append('A')
        e.run(1,'+'.join(k))
        if f>=188:
            s=np.array(e.n.save()); snaps[f]=(s[25570:25570+0x800].copy(), s[6]|s[7]<<8)
    return snaps
A=go('gng.nes',None,194); B=go('v05c.nes',(0xFF,0xC2),194)
for f in range(188,194):
    ra,pa=A[f]; rb,pb=B[f]
    d=[a for a in range(0x800) if ra[a]!=rb[a] and not (0x100<=a<0x200) and a not in (0x7FA,0x7FB)]
    print(f,'PC clean %04X v05 %04X'%(pa,pb),'RAM diffs (excl stack, FK regs, FK ages):',[(hex(a),int(ra[a]),int(rb[a])) for a in d if not (0x4C9<=a<=0x4D1)][:12])
