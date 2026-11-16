# Navigation on the no-damage exploration ROM (god.nes: $E014 contact check -> CLC/RTS).
import numpy as np
from stagesel import goto
from emu import Emu
from rec import grid
class N:
    def __init__(s,rom='gng.nes',sec=12,state=None,safe=True):
        s.safe=safe
        if state is None: s.e=goto(rom,sec,0); s.run('',700)
        else: s.e=Emu(rom); s.e.n.load(state); s.e.run(1)
        s.shots=[]
    def wx(s): return s.e.peek(0x583)*256+s.e.peek(0x5AF)
    def y(s): return s.e.peek(0x56D)*256+s.e.peek(0x599)
    def st(s): return dict(wx=s.wx(),y=s.y(),sx=s.e.peek(0x64)+256*s.e.peek(0x65),f=hex(s.e.peek(0x4F0)),ac=s.e.peek(0xAC))
    KEEP=(0x10,0x11,0x12,0x20)
    mode='mercy'
    def clean(s):
        if not getattr(s,'safe',False): return
        if s.mode=='clear':
            for y in range(1,17):
                if s.e.peek(0x4F0+y) and s.e.peek(0x631+y) not in s.KEEP: s.e.poke(0x4F0+y,0)
            s.e.poke(0x4F0,s.e.peek(0x4F0)&~0x60); return
        f=s.e.peek(0x4F0)
        s.e.poke(0x4F0,(f|0x40)&~0x20)      # mercy invincibility, keep armor
        if s.e.peek(0x647)>8: s.e.poke(0x647,0)
    def step(s,k):
        s.clean(); s.e.run(1,k)
    def run(s,k,n):
        for _ in range(n): s.step(k)
        return s
    def walk_to(s,tx,maxf=3000,tol=2,jump=True):
        last=None; same=0
        for i in range(maxf):
            d=tx-s.wx()
            if abs(d)<=tol: break
            k='R' if d>0 else 'L'
            x=s.wx(); same=same+1 if x==last else 0; last=x
            if jump and same>10:
                s.run(k+'+A',15); same=0; continue
            s.step(k)
        s.run('',4); return s.wx()
    def climb(s,k='U',maxf=600):
        last=None; same=0
        for i in range(maxf):
            s.step(k); y=s.y()
            same=same+1 if y==last else 0; last=y
            if same>40: break
        return s.y()
    def shot(s,tag):
        p=f'{tag}.png'; s.e.shot(p); s.shots.append(p); return p
    def save(s): return np.array(s.e.n.save())
