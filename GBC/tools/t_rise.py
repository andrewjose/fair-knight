"""Rising zombie moved onto Arthur: is Arthur hit while it rises?  usage: t_rise.py ROM FK_SET"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_wdrop import start
rom, fk = sys.argv[1], int(sys.argv[2], 16)
g = start(G(rom), fk)
res = None
for f in range(3000):
    g.p.tick(1, False)
    z = [s for s in range(1, 32) if g.peek(0xC5A4 + s * 32) == 8 and g.peek(0xC5A5 + s * 32) & 1 and g.peek(0xC5A4 + s * 32 + 0x1B) < 2]
    for s in z:
        b = 0xC5A4 + s * 32
        g.poke(b + 6, g.peek(0xC5AA)); g.poke(b + 8, g.peek(0xC5AC)); g.poke(b + 7, g.peek(0xC5AB))
    if g.peek(0xC5BF) in (5, 6):
        res = (f, 'rising zombie' if z else 'other'); break
print(rom, hex(fk), 'Arthur hit at (frame, by):', res)
