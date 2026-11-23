"""ORIGINAL vs clean across the stage-1 weapon pickup (st_wd.bin). usage: t_parity_wd.py FKROM CLEANROM"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core
def go(rom, fk):
    c=Core(rom); c.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'st_wd.bin'),'rb').read()); out=[]
    for f in range(8700,8700+400):
        k='RIGHT+B' if (f//6)%2 else 'RIGHT'
        if (f//40)%5==4: k+='+A'
        if f>=8797 and f<8860: k=''
        if f>=8860: k='LEFT'
        if fk is not None: c.poke(0xFF5A00,fk)
        c.run(1,k); r=c.ram().copy(); r[0xFD00:0xFE00]=0; r[0x5A00:0x5A10]=0; out.append(r)
    return out
a=go(sys.argv[1],0xFF); b=go(sys.argv[2],None)
d=[i for i in range(len(a)) if (a[i]!=b[i]).any()]
print('ORIGINAL vs clean across weapon pickup + walk back, 400 frames:',len(d),'frames differ',d[:5])
