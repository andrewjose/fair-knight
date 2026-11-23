"""End-to-end: pick a preset on the FAIR KNIGHT page, return to the title, start a 1-player game,
walk right until Arthur is first hit, and report mercy timer + horizontal hop speed at the hit.
usage: t_play.py ROM PRESET_RIGHT_PRESSES(0 KNIGHT,1 LEGEND,2 ORIGINAL) [grid.png]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); n=int(sys.argv[2])
to_fk_page(c)
for i in range(n): tap(c,'RIGHT')
tap(c,'START',60)            # page -> OPTION screen
tap(c,'START',60)            # OPTION -> title (intro replays)
c.run(400); c.run(2,'START'); c.run(40)   # PUSH START -> menu (cursor on 1 PLAYER)
assert c.ram()[0xF77C]==0
c.run(2,'START'); c.run(300)
s=c.ram()[0x5A00]
hit=None
for f in range(3000):
    c.run(1,'RIGHT' if (f//90)%4!=3 else 'RIGHT+A')
    r=c.ram(); m=int(r[0xB318])*256+int(r[0xB319])
    if m>0: hit=f; break
if hit is None: print(f'preset {n}: FK_SET={s:02X} no hit in 3000 frames'); sys.exit(1)
tr=[]
for f in range(400):
    r=c.ram(); tr.append((int(r[0xB200])*256+int(r[0xB201]), int(r[0xB20C])>>7)); c.run(1)
vx=int(c.ram()[0xB214])
blink=[i for i in range(1,len(tr)) if tr[i][1]!=tr[i-1][1]]
span=blink[-1]-blink[0]+1 if blink else 0
print(f'preset {n}: FK_SET={s:02X} hit@{hit} dx_first20={tr[20][0]-tr[0][0]} blink_span={span}')
