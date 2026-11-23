"""v0.10 CAMERA: walk right then left in a stage, log Arthur's screen X and the camera per frame.
usage: t_cam.py ROM STAGE [set2] [outprefix]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
def cam(g): return g.peek(0xC249) | g.peek(0xC24A) << 8
def sx(g): return g.peek(0xC5AE)
def hold(g, k, n, log, tag):
    p = g.p
    for x in k: p.button_press(x)
    for _ in range(n):
        p.tick(1, False); log.append((tag, sx(g), cam(g), g.peek(0xC5BF), g.peek(0xC24B)))
    for x in k: p.button_release(x)
def walk(rom, stage, set2=0, out=None, rn=200, ln=160):
    g = start_stage(G(rom), stage)
    g.poke(0xDF03, set2); g.poke(0xDF02, 0x00)
    log = []
    hold(g, [], 30, log, 'idle')
    hold(g, ['right'], rn, log, 'R')
    g.p.tick(1, True)
    if out: g.shot(out + '_right.png')
    hold(g, ['left'], ln, log, 'L')
    g.p.tick(1, True)
    if out: g.shot(out + '_left.png')
    return g, log
if __name__ == '__main__':
    rom, st = sys.argv[1], int(sys.argv[2]); s2 = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
    g, log = walk(rom, st, s2, sys.argv[4] if len(sys.argv) > 4 else None)
    prev = None
    for i, (t, x, c, s, cy) in enumerate(log):
        if i % 10 == 0 or (prev and abs(c - prev) > 3): print(i, t, 'scrX', x, 'cam', c, 'state', s, 'camY', cy)
        prev = c
    print('max per-frame camera step', max(abs(log[i][2] - log[i-1][2]) for i in range(1, len(log))))
