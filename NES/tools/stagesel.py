# Reach any stage via the game's own stage-select (Action Replay code $A7=$0F at the title).
from emu import Emu
import numpy as np
def tap(e,k,n=1,gap=8):
    for _ in range(n): e.run(3,k); e.run(gap)
def to_select(rom):
    e=Emu(rom); e.run(120); e.poke(0xA7,0x0F); e.run(2); e.run(5,'ST'); e.run(200); return e
def goto(rom, ac, settle=900, fk=None):
    """Start play at stage-select section $AC=ac (0=1A,1=1B,2=1C,3=2A,...). Returns Emu in play.
    fk=(FK_SET, FK_PRESET) is poked every frame of the settle period."""
    e=to_select(rom)
    tap(e,'A',ac)
    tap(e,'ST')
    for f in range(settle):
        if fk is not None: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.run(1)
    return e
