# v0.5 equivalence: (1) ORIGINAL preset vs clean ROM, (2) KNIGHT with FAIR SPAWNS OFF vs v0.4 KNIGHT.
import numpy as np, sys
from t_orig import run, KEYS
for label,ra,fa,rb,fb in [('ORIGINAL vs clean','gng.nes',None,'v05c.nes',(0xFF,0xC2)),
                          ('KNIGHT+FS OFF vs v0.4 KNIGHT','v04.nes',(0,0),'v05c.nes',(0,0x40))]:
    for name,n,seed in [('idle',600,None),('bot',2600,0)]:
        a=run(ra,fa,n,seed); b=run(rb,fb,n,seed); d=np.argwhere(a!=b)
        print(label,name,n,'mismatches',len(d),[(int(f),list(KEYS)[c],int(a[f,c]),int(b[f,c])) for f,c in d[:4]])
