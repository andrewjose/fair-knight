# Free-RAM survey across every stage section (via the game's stage select) with random play.
import numpy as np, random
from stagesel import goto
random.seed(2)
keys=['','R','L','A','B','R+A','R+B','U','D','L+A','D+B','U+R']
chg=np.zeros(0x800,int); nz=np.zeros(0x800,int)
for ac in range(14):
    e=goto('gng.nes',ac,400); prev=e.ram().astype(int)
    for blk in range(60):
        k=random.choice(keys)
        for f in range(random.randint(10,40)):
            e.run(1,k); r=e.ram().astype(int); chg+=(r!=prev); nz+=(r!=0); prev=r
np.save('chg2.npy',chg); np.save('nz2.npy',nz)
runs=[];s=None
for a in range(0x800):
    if chg[a]==0 and nz[a]==0:
        if s is None: s=a
    elif s is not None: runs.append((s,a-s)); s=None
if s is not None: runs.append((s,0x800-s))
print([(hex(a),n) for a,n in runs if n>=2])
