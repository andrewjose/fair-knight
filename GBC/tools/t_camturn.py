"""v0.10 camera: turnaround easing per frame, and a lag check (game frames counted by FK_FC per 600
emulated frames while walking, AHEAD vs CENTER).  usage: t_camturn.py ROM [stage]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
from t_cam import cam, sx
def go(rom, st, set2):
    g = start_stage(G(rom), st); g.poke(0xDF03, set2); p = g.p
    for _ in range(40): p.tick(1, False)
    p.button_press('right'); [p.tick(1, False) for _ in range(60)]; p.button_release('right')
    rows = []
    p.button_press('left')
    for f in range(40):
        p.tick(1, False); rows.append((f, sx(g), cam(g), g.peek(0xDF0D)))
    p.button_release('left')
    p.button_press('right'); fc0 = g.peek(0xDF0C); n = 0
    for f in range(600):
        a = g.peek(0xDF0C); p.tick(1, False)
        if g.peek(0xDF0C) != a: n += 1
        if f % 30 == 0: p.button_press('a')
        if f % 30 == 10: p.button_release('a')
    return rows, n
if __name__ == '__main__':
    st = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rows, n = go(sys.argv[1], st, 0x00)
    print('AHEAD turnaround (frame, Arthur screen X, camera, target):')
    print(' '.join(f'{f}:{x}/{c}/{t}' for f, x, c, t in rows))
    _, n2 = go(sys.argv[1], st, 0x08)
    print(f'game frames in 600 emulated frames: AHEAD {n}, CENTER {n2}')
