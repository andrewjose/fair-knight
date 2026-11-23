# Classic edition checks: no sparkle markers in any preset, READY list with MAP/absent with OFF,
# SECRETS row cycles MAP/OFF only, menu flicker.
import sys, csv, numpy as np
from gnav import N
from rec import grid
from emu import Emu
from t_opt import to_options, tap
ROM=sys.argv[1]
P=[]
def setfk(n,s,p=0): n.e.poke(0x7FA,s); n.e.poke(0x7FB,p)
def travel(n,x):
    n.mode='mercy'
    for _ in range(400):
        if abs(x-n.wx())<3 or n.wx()==0: break
        n.walk_to(x,15)
# 1) sparkle spots (same as t_secrets.py), every preset: count visible hidden-item objects
for sec,x,tag in [(10,1264,'duck'),(10,2160,'norm'),(1,2000,'red')]:
    for pname,sv,pv in [('KNIGHT',0x00,0x00),('LEGEND',0xD3,0x81),('ORIGINAL',0xFF,0x82),('MAP01',0x01,0x04)]:
        n=N(ROM,sec=sec); setfk(n,sv,pv); travel(n,x-70); n.mode='clear'; vis=0
        for i in range(40):
            n.step('')
            vis+=sum(1 for k in range(1,22) if n.e.peek(0x4F0+k)&0x80 and n.e.peek(0x631+k)==0x11)
        print(f'sparkle spot {tag:5s} {pname:8s}: visible hidden-item object-frames = {vis}')
        if pname=='KNIGHT': P.append(n.shot(f'cl_{tag}'))
# 2) READY list after a death: MAP (KNIGHT, $00) vs OFF ($03)
def ready_shot(sv,tag):
    n=N(ROM,sec=10); setfk(n,sv); n.mode='clear'
    for a in (0x6F6,0x6F8,0x6FA): n.e.poke(a,0)
    n.e.poke(0x6FC,1)
    for i in range(900):
        n.e.run(1)
        if i%15==0 and n.e.peek(0x4F1)==0x80 and n.e.peek(0x523)==0x1D:
            n.e.run(20); P.append(n.shot(tag)); return True
    return False
print('READY reached MAP', ready_shot(0x00,'cl_ready_map'), 'OFF', ready_shot(0x03,'cl_ready_off'))
# 3) menu: SECRETS row values, flicker
e=to_options(Emu(ROM)); e.run(30)
for i in range(7): tap(e,'D')
vals=[e.peek(0x7FA)&3]
for i in range(4): tap(e,'R'); e.run(10); vals.append(e.peek(0x7FA)&3)
fn='cl_menu.png'; e.shot(fn); P.append(fn)
for i in range(3): tap(e,'L'); e.run(10); vals.append(e.peek(0x7FA)&3)
print('SECRETS row values while cycling R x4 then L x3:', [hex(v) for v in vals], 'preset byte', hex(e.peek(0x7FB)))
fr=[]
for i in range(60): e.run(1); fr.append(np.asarray(e.frame).copy())
print('menu frames differing from previous (60 consecutive):', sum(int((fr[i]!=fr[i-1]).any()) for i in range(1,60)))
grid(P,'classic_test.png',4)
