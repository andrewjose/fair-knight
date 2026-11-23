"""Endgame aid: stage 6 (index 5), call the boss spawner 6 blocks right of Arthur, report the cross
item, pick it up, kill the boss and read $C0C2 (0 = cross kill -> stage 7).  usage: t_endgame.py ROM FK_SET [weapon]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
from t_wdrop import call, items
from t_run import X
def spawn_boss(g, dx_blocks=6):
    g.poke(0xC5A0, g.peek(0xC5AA) + dx_blocks); g.poke(0xC5A1, g.peek(0xC5AB))
    b = g.peek(0x7FFF)
    stub = [0x3E, 1, 0xEA, 0, 0x21, 0xCD, 0xAA, 0x72, 0x3E, b, 0xEA, 0, 0x21, 0xC9]
    for i, x in enumerate(stub): g.poke(0xDE00 + i, x)
    call(g, 0xDE00, 0)
if __name__ == '__main__':
    fk = int(sys.argv[2], 16); w = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    g = start_stage(G(sys.argv[1]), 5, fk, weapon=w); g.run(20)
    spawn_boss(g); g.run(10); g.shot('/tmp/eg0.png')
    print(sys.argv[1:], 'items after boss spawn:', items(g), 'arthur x', X(g))
    g.p.button_press('right')
    for f in range(150):
        g.poke(0xC0A1, g.peek(0xC0A1) | 2); g.p.tick(1, False)
        if g.peek(0xC0B6) == 4: break
    g.p.button_release('right'); g.run(1, 'left'); g.run(1, 'right')
    print('  weapon now', g.peek(0xC0B6), 'arthur x', X(g))
    for f in range(900):
        g.poke(0xC0A1, g.peek(0xC0A1) | 2)
        if f % 10 == 0: g.p.button_press('b')
        if f % 10 == 4: g.p.button_release('b')
        g.p.tick(1, False)
        if g.peek(0xC0C2) or not any(g.peek(0xC5A4 + s * 32) == 0x20 and g.peek(0xC5A5 + s * 32) & 1 for s in range(32)): break
    g.run(5); g.shot('/tmp/eg1.png')
    print('  boss gone after', f, 'frames; $C0C2 =', g.peek(0xC0C2), '(0 = proceeds to the final stage)')
