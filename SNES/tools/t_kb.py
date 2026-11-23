"""Knockback: start stage 1, stand still until a zombie hits; log Arthur's X before/after the
hit hop. usage: t_kb.py ROM [knock_on 0/1]   (Arthur's object: DP $043C; X px at $045B, state $0478)"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); c.run(300)
if len(sys.argv)>2:
    s=c.sram();
    if s[0x1F00]==0x46: c.poke_sram(0x1F02,int(sys.argv[2]))
to_game(c) if False else None
c.run(340); tap(c,'START',6,150); tap(c,'START',6,200)
for i in range(30): tap(c,'START',2,10) if i==0 else None
def X(): r=c.ram(); return r[0x45B]|r[0x45C]<<8
st=None; P=[]
for f in range(1500):
    c.run(1); r=c.ram()
    if r[0x478]==9 and st is None: st=f; x0=X(); print('hit at',f,'X',x0,'armor',r[0x44A])
    if st is not None and f-st in (0,10,20,30,40,60):
        fn=f'/tmp/kb{len(P)}.png'; c.shot(fn,1); P.append(fn)
    if st is not None and f-st<60 and (f-st)%6==0: print(f-st, X(), c.ram()[0x478])
    if st is not None and f-st==60: print('X after 60f',X(),'moved',X()-x0,'mercy $046A',c.ram()[0x46A],'state',c.ram()[0x478]); break
sheet(P,'/tmp/kb_'+os.path.basename(sys.argv[1])+'.png',6)
