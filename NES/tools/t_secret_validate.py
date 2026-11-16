# Validate hidden items (type $11): drive Arthur to a trigger, duck or jump there, and check the reveal ($11 -> $12).
# Uses gnav.N: 'mercy' mode while travelling, 'clear' mode (enemies removed, no mercy bit, because the
# touch test ignores Arthur while bit $40 is set) at the trigger.
import sys, csv, numpy as np
from gnav import N
from rec import grid
rom=sys.argv[1]
cases=[tuple(int(v) for v in c.split(':')) for c in sys.argv[2].split(',')]   # section:x:y:duck
P=[]; ok=0
for sec,x,y,duck in cases:
    n=N(rom,sec=sec); n.mode='mercy'
    for _ in range(400):
        if abs((x-40)-n.wx())<3 or n.wx()==0: break
        n.walk_to(x-40,15)
    n.walk_to(x,800,tol=1)
    slot=[k for k in range(1,22) if n.e.peek(0x4F0+k) and n.e.peek(0x631+k)==0x11 and n.e.peek(0x583+k)*256+n.e.peek(0x5AF+k)==x]
    slot=slot[0] if slot else None
    n.mode='clear'; rev=None
    for t in range(15):
        if n.wx()!=x: n.walk_to(x,200,tol=0,jump=False)
        for i in range(40):
            n.step('D' if duck else ('A' if i<8 else ''))
            if slot and n.e.peek(0x631+slot)==0x12 and rev is None:
                rev=(t,i); n.run('',20); P.append(n.shot(f'val_{sec}_{x}'))
        if rev: break
    ok+=bool(rev)
    print(f'section {sec} x {x} y {y} {"duck" if duck else "jump"}: slot {slot} arthur ({n.wx()},{n.y()}) -> {"REVEALED" if rev else "not revealed"}', flush=True)
if P: grid(P,'val.png',len(P))
print(ok,'of',len(cases),'revealed')
