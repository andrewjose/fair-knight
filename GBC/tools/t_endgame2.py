"""Endgame torch/cross kill: stage 6 boss spawned 6 blocks ahead, Arthur fires the held weapon (no pickup).
Reports $C0C2 after the boss dies (0 = proceeds to the final stage, 1 = stage 6 is replayed).
usage: t_endgame2.py ROM FK_SET weapon(2 torch / 4 cross)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
from t_endgame import spawn_boss
def boss_alive(g):
    return any(g.peek(0xC5A4 + s * 32) == 0x20 and g.peek(0xC5A5 + s * 32) & 1 for s in range(32))
def run(rom, fk, w):
    g = start_stage(G(rom), 5, fk, weapon=w); g.run(20)
    spawn_boss(g, 4); g.run(3, 'right'); g.run(10)
    hp0 = None
    for f in range(1500):
        g.poke(0xC0A1, g.peek(0xC0A1) | 2)           # debug invincibility, so Arthur survives
        g.poke(0xC0B6, w)                            # never pick anything up
        if f % 10 == 0: g.p.button_press('b')
        if f % 10 == 4: g.p.button_release('b')
        g.p.tick(1, False)
        if not boss_alive(g): break
    g.run(5)
    return f, g.peek(0xC0C2), boss_alive(g)
if __name__ == '__main__':
    print(sys.argv[1:], 'frames, $C0C2, boss still alive =', run(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3])))
