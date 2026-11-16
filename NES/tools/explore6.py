# Walk through stage 6 (section 12) with enemies cleared; screenshot periodically.
import sys, numpy as np
from stagesel import goto
from rec import grid
rom=sys.argv[1] if len(sys.argv)>1 else 'gng.nes'
sec=int(sys.argv[2]) if len(sys.argv)>2 else 12
N=int(sys.argv[3]) if len(sys.argv)>3 else 6000
e=goto(rom,sec,700)
P=[]; last=None; stuck=0; log=[]
for f in range(N):
    for y in range(1,17):
        if not (e.peek(0x631+y)==0x10): e.poke(0x4F0+y,0)
    e.poke(0x4F0,e.peek(0x4F0)&~0x20)   # keep armor
    x=(e.peek(0x583),e.peek(0x5AF),e.peek(0x3D),e.peek(0x64),e.peek(0x65),e.peek(0x599),e.peek(0x56D))
    k='R'
    if last==x[:2]: stuck+=1
    else: stuck=0
    last=x[:2]
    if stuck>20 and stuck%40<6: k='R+A'
    if stuck>200 and stuck%80<10: k='U'
    e.run(1,k)
    if f%300==0:
        p=f'ex_{sec}_{f//300:02d}.png'; e.shot(p); P.append(p); log.append((f,)+x+(e.peek(0xAC),e.peek(0xCF)))
for l in log: print(l)
grid(P,f'ex_{sec}.png',cols=5)
