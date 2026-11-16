# Trace helper: replay frames on py65 from the nearest cynes NMI-boundary state; validates against cynes.
import numpy as np
from emu import Emu
from trace import run_frames
def states_until(rom, n, prep=None, state='st_play.npy', keys=lambda f:''):
    e=Emu(rom); e.n.load(np.load(state)); e.run(1); S=[]
    for f in range(n):
        if prep: prep(e)
        S.append(np.array(e.n.save())); e.run(1,keys(f))
    return S,e
def trace_at(rom, S, f, nframes=3, bankaddr=0xC7):
    # find NMI-boundary state at or before f
    k=f
    while not (S[k][6]==0xF0 and S[k][7]==0xC0): k-=1
    s=S[k]; ram=bytes(s[25570:25570+0x800])
    for bank in (ram[bankaddr]&7, ram[0xC8]&7):
        m,cpu=run_frames(s, nframes+(f-k), bank=bank)
        e=Emu(rom); e.n.load(s); e.run(nframes+(f-k)); ok=bytes(m.ram)==bytes(e.ram())
        if ok: return m,k
    return m,k
