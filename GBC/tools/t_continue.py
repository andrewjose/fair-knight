"""Game over -> title: cursor row (3 = CONTINUE) and what START does.  usage: t_continue.py ROM [FK_SET]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
fk = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
g = start_stage(G(sys.argv[1]), 1, fk); g.poke(0xC0AC, 1)          # stage 2, last life
f = 0
def title(g):
    m = bytes(g.peek(a) for a in range(0x9800, 0x9C00))
    return bytes([0x0C, 0x18, 0x17, 0x1D, 0x12, 0x17, 0x1E, 0x0E]) in m   # "CONTINUE" in the BG map
while not g.peek(0xC0A4) and f < 8000: g.run(9); f += 10
g.run(300); g.shot('/tmp/cont.png'); print(sys.argv[1:], 'title cursor row', g.peek(0xC1E9))
g.run(3, 'start')
for i in range(1500):
    g.run(0)
    if g.peek(0xC5A6) == 0xEB and g.peek(0xC5A7) == 0x2F and g.peek(0xC5BF) == 1: break
print('  after START:', 'lives', g.peek(0xC0AC), 'stage index', g.peek(0xC0AD), '(1 = stage 2 continued)')
