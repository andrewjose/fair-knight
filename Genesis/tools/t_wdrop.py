"""WEAPON DROP: bot through stage 1 until the first weapon pickup; save a state just before it,
then show where the old weapon goes. usage: t_wdrop.py ROM FKSET OUTSTATE"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); fk=int(sys.argv[2],16)
to_stage1(c, fk)
hist=[]; prev=c.ram()[0xB22C]
for f in range(int(sys.argv[4]) if len(sys.argv)>4 else 14000):
    k='RIGHT+B' if (f//6)%2 else 'RIGHT'
    if (f//40)%5==4: k+='+A'
    hist.append(c.save()) ; hist=hist[-120:]
    c.run(1,k); c.poke(0xFFB318,0); c.poke(0xFFB319,100); c.poke(0xFF5A00,fk)
    r=c.ram()
    if f%1000==0: print(f,int(r[0xB200])*256+int(r[0xB201]),r[0xB22C])
    if r[0xB22C]!=prev:
        print('pickup frame',f,'weapon',prev,'->',r[0xB22C],'arthur x',int(r[0xB200])*256+int(r[0xB201]))
        open(sys.argv[3],'wb').write(hist[0]); break
