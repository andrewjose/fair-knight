# FAIR SPAWNS telegraph mechanism test: a walking (already harmful) zombie is teleported onto Arthur and,
# in the Fair Knight runs, its age nibble is reset to "new", i.e. it looks exactly like an enemy that
# has just appeared on top of him. Count frames until Arthur is hit.
import numpy as np, sys
from emu import Emu
def run(rom, fk, mark_new, warm=150, frames=200, stick=False):
    e=Emu(rom); e.n.load(np.load('st_play.npy'))
    if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    for f in range(warm):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x21); e.poke(0x647,0)   # safe while we wait for a walker
        e.run(1)
    e.poke(0x4F0,e.peek(0x4F0)&~0x48); e.poke(0x647,0)              # Arthur back to normal
    walk=[s for s in range(1,17) if e.peek(0x631+s)==0 and e.peek(0x4F0+s)&0x80]
    s=walk[0]
    e.poke(0x5AF+s,e.peek(0x5AF)); e.poke(0x583+s,e.peek(0x583))
    if mark_new:
        n=s&15; b=0x4C9+(n>>1); v=e.peek(b)
        e.poke(b, v&0xF0 if n%2==0 else v&0x0F)
    for f in range(frames):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        if stick: e.poke(0x5AF+s,e.peek(0x5AF)); e.poke(0x583+s,e.peek(0x583))   # keep it on Arthur
        e.run(1)
        if f==8: e.shot(f'tel2_{"fk" if fk==(0,0) else "orig"}_{mark_new}.png')
        if e.peek(0x4F0)&0x08: return s,f
    return s,None
if __name__=='__main__':
    rom=sys.argv[1]
    from t_fs_tel4 import variant
    import shutil
    d=bytearray(open(rom,'rb').read())
    OFF=lambda b,a: 16+b*0x4000+a-0x8000
    bank2=bytes(d[OFF(2,0x8000):OFF(2,0xC000)]); i=bank2.find(bytes([0x00,0x03,0x04,0x06,0x07,0x14]),0xBB67-0x8000)
    for k in range(6): d[OFF(2,0x8000)+i+k]=0xFE
    open('tst_nonudge.nes','wb').write(d)
    for name,r,fk,mn in [('clean ROM','gng.nes',None,False),('v0.5 ORIGINAL',rom,(0xFF,0xC2),True),
                         ('v0.5 KNIGHT, push disabled',"tst_nonudge.nes",(0,0),True),('v0.5 KNIGHT, zombie already settled',rom,(0,0),False)]:
        for stick in (False,True):
            s,hit=run(r,fk,mn,stick=stick)
            print(f'{name:38} zombie slot {s} placed on Arthur{" and held there" if stick else " (walks on)   "} -> hit after {hit} frames')
