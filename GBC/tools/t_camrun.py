"""v0.10 camera: run a stage to its end with a bot (hold Right, jump every 24 frames, mercy kept on,
timer refilled) and log camera, limits and Arthur's screen X. usage: t_camrun.py ROM STAGE SET2 [frames] [shotprefix]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
def run(rom, stage, set2, n=6000, shots=None, cp=None):
    g = start_stage(G(rom), stage)
    g.poke(0xDF03, set2); g.poke(0xDF02, 0x00)
    p = g.p; p.button_press('right'); log = []
    if cp is not None: pass
    y0 = (g.peek(0xC5AB), g.peek(0xC5AD)); fly = '--fly' in sys.argv
    for f in range(n):
        if f % 24 == 0: p.button_press('a')
        if f % 24 == 12: p.button_release('a')
        g.poke(0xCAFC, 100); g.poke(0xC5C0, g.peek(0xC5C0) | 0x20); g.poke(0xC0AF, 3)
        if f == 60: y0 = (g.peek(0xC5AB), g.peek(0xC5AD))
        if fly and f > 60 and g.peek(0xC5BF) in (1, 3, 7): g.poke(0xC5AB, y0[0]); g.poke(0xC5AD, y0[1])
        p.tick(1, shots is not None and f % 200 == 0)
        cam = g.peek(0xC249) | g.peek(0xC24A) << 8
        log.append((f, g.peek(0xC5AE), cam, g.peek(0xC241), g.peek(0xC214) | g.peek(0xC215) << 8, g.peek(0xC5BF), g.peek(0xC0AD), g.peek(0xC24B) | g.peek(0xC24C) << 8))
        if shots and f % 200 == 0: g.shot(f'{shots}_{f:05d}.png')
    return g, log
if __name__ == '__main__':
    A = [a for a in sys.argv[1:] if not a.startswith('--')]
    rom, st, s2 = A[0], int(A[1]), int(A[2], 0)
    n = int(A[3]) if len(A) > 3 else 6000
    g, log = run(rom, st, s2, n, A[4] if len(A) > 4 else None)
    last = None
    for r in log:
        key = (r[3], r[4], r[6])
        if key != last or r[0] % 250 == 0: print(r)
        last = key
    print('max cam', max(r[2] for r in log), 'max step', max(abs(log[i][2] - log[i-1][2]) for i in range(1, len(log)) if log[i][6] == log[i-1][6]))
