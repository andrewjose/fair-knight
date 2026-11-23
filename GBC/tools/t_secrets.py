"""SECRETS test: start a stage with FK_SET2 forced, walk/teleport, check sparkle sprites in OAM and the found bitmap.
usage: t_secrets.py ROM stage(1-6) fkset2 [out.png]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G, grid
from t_stage import start_stage
def oam(g): 
    m = g.p.memory; return [(m[0xFE00+i], m[0xFE01+i], m[0xFE02+i], m[0xFE03+i]) for i in range(0, 160, 4) if m[0xFE00+i]]
def found(g): return [g.peek(0xDF10 + i) for i in range(8)]
def sparkles(g): return [o for o in oam(g) if o[2] in (0x74, 0x75)]
if __name__ == '__main__':
    g = G(sys.argv[1]); st = int(sys.argv[2]); s2 = int(sys.argv[3], 0)
    g.run(10); g.poke(0xDF03, s2)
    start_stage(g, st - 1); g.poke(0xDF03, s2); g.run(60)
    print('sparkles', sparkles(g), 'found', found(g))
    if len(sys.argv) > 4: g.shot(sys.argv[4])
