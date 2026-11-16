# v0.5: set FAIR SPAWNS through the real menu, start a 1-player game, and check the zombie cap in play
# (Arthur kept alive with a mercy poke so zombies pile up; count zombies on screen).
from emu import Emu
from t_opt import to_options, tap
import numpy as np, sys
ROM=sys.argv[1]
def play_from_menu(keys):
    e=to_options(Emu(ROM))
    for k in keys: tap(e,k)
    s=(e.peek(0x7FA),e.peek(0x7FB))
    tap(e,'ST',4)
    for i in range(120):
        e.run(2)
        if e.peek(0x509)==0x92 and e.peek(0xA3)==0: break
    e.run(40); tap(e,'ST',4)
    for i in range(3000):
        e.run(1)
        if e.peek(0x599)==184 and e.peek(0x6FC)!=0 and i>600: break
    return e,s
def zombies(e,frames=2400):
    mx=0; hist=[]
    for f in range(frames):
        e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x21); e.poke(0x647,0)
        e.run(1)
        z=sum(1 for s in range(1,17) if e.peek(0x4F0+s) and e.peek(0x631+s)==0)
        mx=max(mx,z); hist.append(z)
    return mx, np.mean(hist)
for tag,keys in [('KNIGHT (fair spawns on)',[]),('fair spawns turned OFF',['U','U','R']),('ORIGINAL preset',['R','R'])]:
    e,s=play_from_menu(keys)
    mx,avg=zombies(e)
    print(f'{tag:26s} FK_SET={s[0]:02X} FK_PRESET={s[1]:02X}  max zombies out {mx}  average {avg:.1f}')
