"""Ladder safety: run to the first stage 1 ladder (X 728), climb to the top, count mercy frames after
stepping off.  usage: t_ladder.py ROM [FK_SET hex]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_wdrop import start
from t_run import autorun, X
if __name__ == '__main__':
    fk = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
    g = start(G(sys.argv[1]), fk)
    autorun(g, 1500, lambda g, f: g.peek(0xC5BF) == 4, up=True)
    g.p.button_press('up'); f = 0
    while g.peek(0xC5BF) == 4 and f < 300: g.poke(0xC0A1, g.peek(0xC0A1) | 2); g.p.tick(1, False); f += 1
    off = f; merc = 0; shots = []
    for i in range(80):
        g.poke(0xC0A1, g.peek(0xC0A1) | 2); g.p.tick(1, True)
        if g.peek(0xC5C0) & 0x20: merc += 1
        if i in (2, 6): g.shot(f'/tmp/ltop{i}.png')
    g.p.button_release('up')
    print(sys.argv[1:], f'climb {off}f, top at y {g.peek(0xC5AB)}, mercy after step-off {merc} frames, $CAFC {g.peek(0xCAFC)}')
