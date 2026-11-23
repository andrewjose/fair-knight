"""FAIR KNIGHT page: navigate every row, change every value, presets, reset, wrap, flicker. usage: t_menu.py ROM"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import *
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import grid
c=Core(sys.argv[1]); to_fk_page(c)
P=[]; log=[]
def snap(t):
    fn=f'/tmp/m{len(P)}.png'; c.shot(fn,1); P.append(fn); r=c.ram()
    log.append(f'{t:22s} set={r[0x5A00]:02X} set2={r[0x5A02]:02X} preset={r[0x5A01]:02X} cur={r[0x5A03]}')
snap('open')
for k,t in [('RIGHT','preset R'),('RIGHT','preset R'),('RIGHT','preset R wrap'),('LEFT','preset L wrap')]: tap(c,k); snap(t)
tap(c,'DOWN'); tap(c,'LEFT'); snap('knockback toggled')
tap(c,'DOWN'); tap(c,'RIGHT'); snap('mercy toggled')
tap(c,'DOWN'); tap(c,'RIGHT'); snap('weapon drop toggled')
tap(c,'Y'); snap('A = reset preset')
tap(c,'DOWN'); tap(c,'RIGHT'); snap('EXIT row, Right ignored')
tap(c,'DOWN'); snap('Down wraps to PRESET')
tap(c,'UP'); snap('Up wraps to EXIT')
F=[]
for i in range(60): c.run(1); F.append(c.frame.copy())
print('idle frames changed:', sum(int((F[i]!=F[i-1]).any()) for i in range(1,60)), '/59')
tap(c,'START',60); snap('START back to OPTION')
print('\n'.join(log)); grid(P,cols=4,out=sys.argv[2] if len(sys.argv)>2 else '/tmp/t_menu.png',w=320,h=224)
