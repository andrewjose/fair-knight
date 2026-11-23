"""One emulator run (GPGX allows one core per process). usage:
run1.py ROM STATE FKSET|none FRAMES SCRIPT OUT.npy
SCRIPT: idle | bot (random walk/jump/attack, seed 7) | file:<path> (one button string per line)"""
import sys, random, numpy as np, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core
rom, state, fks, frames, script, out = sys.argv[1:7]
frames = int(frames); fks = None if fks == 'none' else int(fks, 0)
c = Core(rom); c.load(open(state, 'rb').read())
keys = ['', 'RIGHT', 'LEFT', 'A', 'B', 'RIGHT+A', 'LEFT+A', 'RIGHT+B']
lines = open(script[5:]).read().split('\n') if script.startswith('file:') else None
random.seed(7); k = ''; R = []
for f in range(frames):
    if fks is not None: c.poke(0xFF5A00, fks)
    if script == 'bot' and f % 20 == 0: k = random.choice(keys)
    if lines is not None: k = lines[f] if f < len(lines) else ''
    c.run(1, k if script != 'idle' else '')
    R.append(c.ram())
np.save(out, np.array(R))
