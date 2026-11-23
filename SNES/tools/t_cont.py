"""Continues: force a game over (lives $02A4 = 0), check the CONTINUE screen and the credit
counter $0290 (BCD) across several continues. usage: t_cont.py ROM [n]"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); n=int(sys.argv[2]) if len(sys.argv)>2 else 3
c.run(640); tap(c,'START',6,150); tap(c,'START',6,200); tap(c,'START',2,10)
P=[]
for k in range(n):
    c.poke(0x7E02A4,0)
    for f in range(3000):
        c.run(1)
        if c.ram()[0x279]!=c.ram()[0x279]: pass
    fn=f'/tmp/co{k}.png'; c.shot(fn,1); P.append(fn)
    print('game over screen; credits',hex(c.ram()[0x290]))
    tap(c,'START',6,400)
    print(' after START: credits',hex(c.ram()[0x290]), 'lives', c.ram()[0x2A4])
    c.run(600)
sheet(P,'/tmp/t_cont_'+os.path.basename(sys.argv[1])+'.png',3)
