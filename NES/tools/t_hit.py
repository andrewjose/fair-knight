import numpy as np, sys
from emu import Emu
def run(rom,fk,frames=600,inp=lambda f:''):
    e=Emu(rom); e.n.load(np.load('st_play.npy')); e.run(1)
    if fk is not None: e.poke(0x7FA,fk)
    R=[]
    for f in range(frames): e.run(1,inp(f)); R.append(e.ram())
    return np.array(R),e
if __name__=='__main__':
    O,_=run('gng.nes',None); A,_=run('fk_a.nes',0xC0)
    d=(O!=A); d[:,0x7FA]=False
    print('original-mode vs clean: differing frames',int(d.any(1).sum()))
    K,_=run('fk_a.nes',0x00)
    x=K[:,0x5AF]; print('knight: X changes',[(i,int(x[i])) for i in range(1,len(x)) if x[i]!=x[i-1]][:10])
    c=K[:,0x647]; print('knight: mercy counter max',int(c.max()), 'orig max',int(O[:,0x647].max()))
    print('orig deaths frame', [i for i in range(1,600) if O[i,0x715]!=O[i-1,0x715]], 'knight', [i for i in range(1,600) if K[i,0x715]!=K[i-1,0x715]])
