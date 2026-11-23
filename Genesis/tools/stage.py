"""Start a given stage (0-5) from power-on with the Action Replay style poke FFB22E = stage. Returns Core."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import *
def start_stage(rom, stage, fk=None, settle=400):
    c=Core(rom); to_title_menu(c)
    for i in range(60):
        c.poke(0xFFB22E,0); c.poke(0xFFB22F,stage); c.run(1, 'START' if i<2 else '')
    for i in range(settle):
        c.poke(0xFFB22F,stage) if i<200 else None
        if fk is not None: c.poke(0xFF5A00,fk)
        c.run(1)
    return c
