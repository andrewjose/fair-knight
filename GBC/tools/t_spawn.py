"""Fair spawns: Arthur stands at the left edge of stage 1 (zombie column 1 is there) for N frames,
invincible; logs zombie spawn distances and touches.  usage: t_spawn.py ROM FK_SET [frames]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_wdrop import start
from t_run import X
rom, fk = sys.argv[1], int(sys.argv[2], 16); N = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
g = start(G(rom), fk); g.poke(0xC5AA, 1); g.poke(0xC5AC, 0x80); g.run(5)   # stand in zombie column 1
prev = [0] * 32; d = []; maxz = 0
for f in range(N):
    g.poke(0xC0A1, g.peek(0xC0A1) | 2); g.p.tick(1, False)
    z = 0
    for s in range(1, 32):
        b = 0xC5A4 + s * 32; act = g.peek(b + 1) & 1
        if act and g.peek(b) == 8:
            z += 1
            if not prev[s]: d.append(g.peek(b + 6) * 16 + g.peek(b + 8) // 16 - X(g))
        prev[s] = act and g.peek(b) == 8
    maxz = max(maxz, z)
near = [x for x in d if abs(x) < 32]
print(rom, hex(fk), f'arthur x {X(g)}; {len(d)} zombies, {len(near)} within 32 px {sorted(near)}, nearest {min(map(abs, d)) if d else None} px, max at once {maxz}')
