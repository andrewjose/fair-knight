"""Air control test: standing jump, then hold Right from frame 6; and running-right jump reversed to Left.
Reports X travel, peak Y and airtime.  usage: t_air.py ROM [FK_SET hex]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_wdrop import start
def X(g): return g.peek(0xC5AA) * 16 + g.peek(0xC5AC) / 16
def Y(g): return g.peek(0xC5AB) * 16 + g.peek(0xC5AD) / 16
def jump(g, pre, mid):
    if pre: g.run(20, pre)
    x0, y0 = X(g), Y(g); ys = []; f = 0
    g.p.button_press('a')
    if pre: g.p.button_press(pre)
    g.p.tick(1, False)
    if pre: g.p.button_release(pre)
    if mid: g.p.button_press(mid)
    while True:
        g.p.tick(1, False); f += 1; ys.append(Y(g))
        if f == 3: g.p.button_release('a')
        if (g.peek(0xC5BF) == 1 and f > 4) or f > 120: break
    if mid: g.p.button_release(mid)
    g.p.button_release('a')
    return f'dx {X(g) - x0:+.0f}px  peak {y0 - min(ys):.0f}px  air {f}f'
if __name__ == '__main__':
    fk = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
    g = start(G(sys.argv[1]), fk); s = g.save()
    print(sys.argv[1:], 'standing+Right:', jump(g, '', 'right'))
    g.load(s); print(sys.argv[1:], 'run right, Left mid:', jump(g, 'right', 'left'))
    g.load(s); print(sys.argv[1:], 'run right, no input:', jump(g, 'right', ''))
