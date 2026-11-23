"""Start at any stage: poke the stage index $C0AD during the intro scene.  start_stage(g, idx, fkset)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
def start_stage(g, idx, fkset=None, weapon=None):
    g.run(660)
    if fkset is not None: g.poke(0xDF02, fkset)
    for _ in range(5):
        g.run(3, 'start'); g.run(110)
        if g.peek(0xC5A6) == 0x01 and g.peek(0xC5A7) == 0x42: break
    g.poke(0xC0AD, idx)
    if weapon is not None: g.poke(0xC0B6, weapon)
    for _ in range(900):
        g.run(0)
        if g.peek(0xC5BF) == 1 and g.peek(0xC5A6) == 0xEB and g.peek(0xC5A7) == 0x2F: break
    return g
if __name__ == '__main__':
    g = start_stage(G(sys.argv[1]), int(sys.argv[2])); g.run(30); g.shot(sys.argv[3]); print('stage', g.peek(0xC0AD))
