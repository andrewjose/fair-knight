import numpy as np, random
from emu import Emu
random.seed(1)
e=Emu(); first=None
mn=np.full(0x800,255); mx=np.zeros(0x800,int); chg=np.zeros(0x800,int); prev=None
keys=['','R','L','A','B','R+A','R+B','U','D','L+A','ST']
for blk in range(500):
    k=random.choice(keys) if blk%40 else 'ST'
    for f in range(random.randint(10,60)):
        e.run(1,k if f<30 or k!='ST' else '')
        r=e.ram().astype(int)
        if prev is not None: chg+= (r!=prev)
        prev=r; mn=np.minimum(mn,r); mx=np.maximum(mx,r)
np.save('chg.npy',chg); np.save('mx.npy',mx)
never=[a for a in range(0x800) if chg[a]==0]
print('frames done; never-changed count',len(never))
# group runs
runs=[];s=None
for a in range(0x800):
    if chg[a]==0:
        if s is None: s=a
    elif s is not None: runs.append((s,a-s)); s=None
if s is not None: runs.append((s,0x800-s))
print([(hex(a),n,int(mx[a])) for a,n in runs if n>=3])
e.shot('survey_end.png')
