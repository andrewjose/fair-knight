"""v0.10 fair spawns with the AHEAD camera: walk stage 1 (invincible, debug flag $C0A1 bit 1), turning
every 300 frames, and log where new zombies rise relative to Arthur (px, + = in front of his facing).
usage: t_spawn2.py ROM SET2 [frames]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_wdrop import start
from t_run import X
rom, s2 = sys.argv[1], int(sys.argv[2], 0); N = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
g = start(G(rom), 0x00); g.poke(0xDF03, s2); p = g.p
prev = [0] * 32; d = []; key = 'right'; p.button_press(key)
for f in range(N):
    if f % 300 == 299 and f < N - 300:
        p.button_release(key); key = 'left' if key == 'right' else 'right'; p.button_press(key)
    if f % 300 == 0 and key == 'left': pass
    g.poke(0xC0A1, g.peek(0xC0A1) | 2); p.tick(1, False)
    face = 1 if g.peek(0xC5C0) & 1 else -1
    for s in range(1, 32):
        b = 0xC5A4 + s * 32; act = g.peek(b + 1) & 1
        if act and g.peek(b) == 8 and not prev[s]:
            d.append((g.peek(b + 6) * 16 + g.peek(b + 8) // 16 - X(g)) * face)
        prev[s] = act and g.peek(b) == 8
behind = sorted(x for x in d if x < 0)
print(rom, hex(s2), f'{len(d)} zombies; behind Arthur: {behind}; closest behind {max(behind) if behind else None}; in front: {sorted(x for x in d if x >= 0)}')
