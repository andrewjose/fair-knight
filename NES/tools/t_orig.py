# ORIGINAL preset must play exactly like the clean ROM: 600 idle frames + 2600-frame bot run.
import numpy as np, sys
from emu import Emu
KEYS={'X':0x5AF,'Y':0x599,'flags':0x4F0,'lives':0x715,'weapon':0x53A,'mercy':0x647,
      'timer':0x6FC,'timer10':0x6FA,'score':0x4E8,'scroll':0x64,'scrollhi':0x65,'arc':0x607}
def run(rom, fk, n, seed=None):
    rng=np.random.default_rng(seed) if seed is not None else None
    e=Emu(rom); e.n.load(np.load('st_play.npy'))
    if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    e.run(1); out=[]
    for f in range(n):
        if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        k=''
        if rng is not None:
            e.poke(0x4F0,e.peek(0x4F0)&~0x20)
            k=['R'] if rng.random()<0.8 else ['L']
            if f%8<3: k.append('B')
            if rng.random()<0.03: k.append('A')
            k='+'.join(k)
        e.run(1,k); out.append([e.peek(a) for a in KEYS.values()])
    return np.array(out)
if __name__=="__main__":
  rom=sys.argv[1] if len(sys.argv)>1 else 'v03a.nes'
  for name,n,seed in [('idle',600,None),('bot',2600,0)]:
    a=run('gng.nes',None,n,seed); b=run(rom,(0xFF,0xC2),n,seed)
    diff=np.argwhere(a!=b)
    print(name, 'frames',n,'mismatching (frame,field):', len(diff), [(int(f),list(KEYS)[c]) for f,c in diff[:5]])
