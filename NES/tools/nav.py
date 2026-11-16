# Step-by-step navigation helper with enemy clearing. Usage in python: from nav import *
import numpy as np
from stagesel import goto
from emu import Emu
from rec import grid
def clear(e, keep_items=True):
    for y in range(1,17):
        if not (keep_items and e.peek(0x631+y)==0x10): e.poke(0x4F0+y,0)
    e.poke(0x4F0,e.peek(0x4F0)&~0x20)
    e.poke(0xBD,0)
def go(e,k,n,clr=True):
    for _ in range(n):
        if clr: clear(e)
        e.run(1,k)
    return e
def st(e): return dict(pg=e.peek(0x583),x=e.peek(0x5AF),y=e.peek(0x599),yh=e.peek(0x56D),sx=e.peek(0x3D),sy=e.peek(0x64),f=hex(e.peek(0x4F0)),ac=e.peek(0xAC),cf=e.peek(0xCF))
def save(e): return np.array(e.n.save())
def load(rom,s):
    e=Emu(rom); e.n.load(s); e.run(1); return e
def inv(e):
    e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x20); e.poke(0x647,0); e.poke(0xBD,0)
def go2(e,k,n,shots=None,every=30):
    out=[]
    for i in range(n):
        inv(e); e.run(1,k)
        if shots is not None and i%every==every-1:
            p=f'{shots}_{i:04d}.png'; e.shot(p); out.append(p)
    return out
