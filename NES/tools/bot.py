import numpy as np, sys
from emu import Emu
def bot(rom, fk=None, frames=6000, seed=0, stop_on_pick=True, cb=None, start='st_play.npy'):
    rng=np.random.default_rng(seed)
    e=Emu(rom); e.n.load(np.load(start)); e.run(1)
    w0=e.peek(0x53A); events=[]
    for f in range(frames):
        if fk is not None: e.poke(0x7FA,fk)
        if e.peek(0x4F0)&0x20: e.poke(0x4F0,e.peek(0x4F0)&~0x20)   # keep armor (test harness only)
        k=['R'] if rng.random()<0.8 else ['L']
        if f%8<3: k.append('B')
        if rng.random()<0.03: k.append('A')
        e.run(1,'+'.join(k))
        if cb: cb(e,f)
        w=e.peek(0x53A)
        if w!=w0:
            events.append((f,hex(w0),hex(w))); w0=w
            if stop_on_pick: return e,events
    return e,events
if __name__=='__main__':
    for s in range(int(sys.argv[1]) if len(sys.argv)>1 else 4):
        e,ev=bot('gng.nes',seed=s,frames=4000); print(s,ev, e.peek(0x64),e.peek(0x65))
