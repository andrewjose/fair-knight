from emu import Emu
from rec import grid
import numpy as np, sys
ROM=sys.argv[1] if len(sys.argv)>1 else 'fk_v02a.nes'
def to_options(e):
    e.run(120)
    for i in range(4):               # v0.5.3: CONTINUE row is skipped until a game over
        if e.peek(0xA3)==3: break
        e.run(4,'SEL'); e.run(14)
    assert e.peek(0xA3)==3, e.peek(0xA3)
    e.run(3,'ST'); e.run(6)
    for i in range(40):
        e.run(2)
        if e.peek(0x7FF)&0x80: break
    return e
def tap(e,k,wait=8): e.run(3,k); e.run(wait)
if __name__=='__main__':
    e=to_options(Emu(ROM)); P=[]
    e.shot('o0.png'); P.append('o0.png'); print('job',hex(e.peek(0x7FF)),'set',hex(e.peek(0x7FA)),'pre',e.peek(0x7FB))
    np.save('st_opt.npy',e.n.save())
    grid(P,cols=1)
