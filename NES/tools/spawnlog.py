# Log every object spawn (slot type 0 -> nonzero, or flags bit $40 newly set) with position vs Arthur.
import numpy as np, sys
from emu import Emu
def log_spawns(rom, frames, fk=None, invuln=True, keys=lambda f:'', state='st_play.npy', emu=None):
    e=emu or Emu(rom)
    if emu is None: e.n.load(np.load(state)); e.run(1)
    prev_t=[e.peek(0x631+s) for s in range(22)]; prev_f=[e.peek(0x4F0+s) for s in range(22)]
    out=[]
    for f in range(frames):
        if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        if invuln: e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x20); e.poke(0x647,0)
        e.run(1,keys(f))
        ax=e.peek(0x5AF); ay=e.peek(0x599)
        for s in range(1,22):
            t=e.peek(0x631+s); fl=e.peek(0x4F0+s)
            new = (t!=prev_t[s] and t!=0) or ((fl&0x40) and not (prev_f[s]&0x40))
            if new:
                out.append(dict(f=f,slot=s,type=t,kind=e.peek(0x61D+s),x=e.peek(0x5AF+s),y=e.peek(0x599+s),xh=e.peek(0x583+s),yh=e.peek(0x56D+s),flags=fl,ax=ax,ay=ay,dx=int(e.peek(0x5AF+s))-int(ax)))
            prev_t[s]=t; prev_f[s]=fl
    return out,e
if __name__=='__main__':
    out,_=log_spawns('gng.nes',int(sys.argv[1]) if len(sys.argv)>1 else 1500)
    import collections
    c=collections.Counter(o['type'] for o in out); print(c)
    for o in out[:60]: print(o)
