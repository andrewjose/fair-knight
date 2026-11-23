"""ORIGINAL preset regression: compare a build (FK_SET=$FF) with the clean ROM frame by frame.
usage: t_orig.py CLEAN BUILD [frames]   - idle run, then scripted run (start + walk/jump/fire)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
import numpy as np
def script(f):
    if 660 <= f < 1260 and f % 110 < 3: return 'start'
    if f >= 1300:
        k = (f // 40) % 6
        return ['right', 'right', 'a', 'b', 'left', 'right'][k] if f % 40 < 20 else ''
    return ''
def script2(f):                   # v0.10: crouch / crouch+direction / release patterns
    if 660 <= f < 1260 and f % 110 < 3: return 'start'
    if f >= 1300:
        k = (f // 30) % 8
        return ['down', 'down+right', 'right', 'down+left', 'left', 'down+b', 'a+right', ''][k]
    return ''
def run(clean, build, n, scripted):
    a, b = G(clean), G(build)
    a.run(0); b.run(0)
    first = None; poked = False; held = set(); gp = 0
    for f in range(n):
        if not poked and b.peek(0xDF00) == 0x46:   # v0.10: set ORIGINAL only after h_init has run
            b.poke(0xDF02, 0xFF); b.poke(0xDF03, 0x0F); b.poke(0xDF04, 0x02); poked = f
        k = (script2(f) if scripted == 2 else script(f)) if scripted else ''
        want = set(x for x in k.split('+') if x)
        for e in (a, b):                       # real holds (press/release only on change)
            for x in held - want: e.p.button_release(x)
            for x in want - held: e.p.button_press(x)
            e.p.tick(1, True)
        held = want
        sa = np.asarray(a.p.screen.ndarray)[:, :, :3]; sb = np.asarray(b.p.screen.ndarray)[:, :, :3]
        if b.peek(0xC5BF) in (2, 3) and b.peek(0xC0AD) < 8: gp += 1   # frames Arthur crouched/jumping
        if first is None and not np.array_equal(sa, sb):
            first = f; a.shot('/tmp/orig_a.png'); b.shot('/tmp/orig_b.png')
    assert poked is not False, 'h_init never ran'
    print('   (frames with Arthur crouched or jumping:', gp, ')')
    return first
if __name__ == '__main__':
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
    for s in (False, True, 2):
        r = run(sys.argv[1], sys.argv[2], n, s)
        print({False: 'idle', True: 'scripted', 2: 'crouch-scripted'}[s], n, 'frames:', 'IDENTICAL' if r is None else f'first difference at frame {r}')
