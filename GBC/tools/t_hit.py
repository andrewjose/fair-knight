"""Idle in stage 1 until a zombie hits Arthur; report knockback distance and mercy length.
usage: t_hit.py ROM [FK_SET hex]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
def to_stage1(g, fkset=None):
    g.run(660)
    if fkset is not None: g.poke(0xDF02, fkset)
    for _ in range(5): g.run(3, 'start'); g.run(110)
    return g
def trace(g, n=900):
    rows = []
    for f in range(n):
        g.run(0); rows.append((f, g.peek(0xC5AA), g.peek(0xC5AE), g.peek(0xC5BF), g.peek(0xC5C0), g.peek(0xCAFC)))
    return rows
def summary(rows):
    hit = next((r for r in rows if r[3] == 5), None)
    if not hit: return 'no hit'
    f0 = hit[0]; x0 = rows[f0-1][2]
    hop = [r for r in rows[f0:] if r[3] == 5]
    xend = rows[f0 + len(hop)][2]
    merc = [r for r in rows[f0:] if r[4] & 0x20]
    return f'hit@{f0} screenX {x0:#x}->{xend:#x} (hop {len(hop)}f) mercy flag {len(merc)}f'
if __name__ == '__main__':
    fk = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
    g = to_stage1(G(sys.argv[1]), fk)
    print(sys.argv[1], sys.argv[2:] , summary(trace(g)))
