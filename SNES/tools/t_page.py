"""FAIR KNIGHT page: boot defaults, open with X, navigate, change values, presets, exit.
usage: t_page.py ROM [out.png]"""
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); P=[]
def s(t):
    fn=f'/tmp/pg{len(P)}.png'; c.shot(fn,1); P.append(fn)
    r=c.ram(); sr=c.sram()
    print(f'{t:22s} base1FF0={bytes(r[0x1FF0:0x1FF7]).hex()} FKSET={sr[0x1F02]:02X} PRE={sr[0x1F03]} CUR={sr[0x1F04]} sig={bytes(sr[0x1F00:0x1F02])} sramSG={bytes(sr[0:10]).hex()}')
to_options(c); c.run(20); s('option mode')
tap(c,'X',6,40); s('X -> page')
tap(c,'DOWN',6,30); s('down (knockback)')
tap(c,'RIGHT',6,30); s('knockback toggled')
tap(c,'UP',6,30); s('up (preset)')
tap(c,'RIGHT',6,30); s('preset right')
tap(c,'RIGHT',6,30); s('preset right')
tap(c,'RIGHT',6,30); s('preset right wrap')
for i in range(5): tap(c,'DOWN',6,30)
s('weapon row'); tap(c,'RIGHT',6,30); s('weapon right')
tap(c,'A',6,30); s('A reset preset')
tap(c,'DOWN',6,30); s('exit row')
tap(c,'START',6,60); s('START -> option mode')
tap(c,'DOWN',6,30); s('option down still works')
from nav import sheet
sheet(P,sys.argv[2] if len(sys.argv)>2 else '/tmp/t_page.png',4)
