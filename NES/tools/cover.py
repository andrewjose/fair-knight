import numpy as np, random, sys
from emu import Emu, B
from trace import run_frames
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 2)
e=Emu(); W=np.zeros(0x800,int)
keys=['','R','L','A','B','R+A','R+B','U','D','L+A','ST','R+U','R+D']
segs=0
for blk in range(250):
    k=random.choice(keys) if blk%25 else 'ST'
    n=random.randint(20,80)
    # sync to NMI-entry state
    s=np.array(e.n.save())
    if s[6]==0xf0 and s[7]==0xc0:
        pad=0
        for kk in k.split('+'):
            if kk: pad|=B[kk]
        m,_=run_frames(s,min(n,30),pad=pad)
        for _,a,_,_ in m.writes: W[a]+=1
        segs+=1
    e.run(n,k)
np.save(f'W{sys.argv[1] if len(sys.argv)>1 else 2}.npy',W)
print('segs',segs)
