"""ORIGINAL preset vs the unpatched base: same boot, same inputs, compare every frame.
The FK ROM gets ORIGINAL settings poked after boot (base settings all 0, FK_SET = $01).
usage: t_orig.py BASE FK [frames]"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
import numpy as np
N=int(sys.argv[3]) if len(sys.argv)>3 else 4000
def run(rom,fk):
    c=Core(rom); c.run(300)
    if fk:
        for i in range(7): c.poke(0x7E1FF0+i,0)
        c.poke_sram(0x1F02,1)
    c.run(340); tap(c,'START',6,150); tap(c,'START',6,200); tap(c,'START',2,10)
    F=[]
    for f in range(N):
        k='RIGHT' if (f//200)%3==0 else ('LEFT' if (f//200)%3==1 else '')
        if f%37==0: k=(k+'+B') if k else 'B'
        if f%53==0: k=(k+'+A') if k else 'A'
        c.run(1,k); F.append(c.frame.copy())
    return F
A=run(sys.argv[1],False); B=run(sys.argv[2],True)
d=[i for i in range(N) if not np.array_equal(A[i],B[i])]
print('frames',N,'differing',len(d),'first',d[:5])
from PIL import Image
for i in d[:4]:
    m=(A[i]!=B[i]).any(2); ys,xs=np.where(m); print(i,'pixels',m.sum(),'bbox',xs.min(),ys.min(),xs.max(),ys.max())
    Image.fromarray(np.concatenate([A[i],B[i]],1)).save(f'/tmp/od{i}.png')
