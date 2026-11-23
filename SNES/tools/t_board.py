"""Leaderboard board type after a game over: ORIGINAL base settings with knockback ON (expect
CLEAN) and OFF (expect OTHER). usage: t_board.py ROM out.png"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
P=[]
for kb in (1,0):
    c=Core(sys.argv[1]); c.run(300)
    for i in range(7): c.poke(0x7E1FF0+i,0)
    c.poke_sram(0x1F02,kb)
    c.run(340); tap(c,'START',6,150); tap(c,'START',6,200); tap(c,'START',2,10)
    c.poke(0x7E02A4,0); c.run(1400+600)
    fn=f'/tmp/board{kb}.png'; c.shot(fn,1); P.append(fn); print('knockback', 'ON' if kb else 'OFF', 'board index $7EAF90 =', c.ram()[0xAF90])
sheet(P,sys.argv[2],2)
