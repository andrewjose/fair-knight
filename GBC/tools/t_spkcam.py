"""v0.10: sparkles stay locked to the level while the AHEAD camera moves and eases. Bot: hold Right,
jump every 24 frames, invincible, Arthur pinned to his start height; when a sparkle first appears it
turns around for 60 frames (camera easing) and then goes on. Per frame, sprite X (tile $6F) + camera
X must stay constant.  usage: t_spkcam.py ROM stage_index [frames]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
g = start_stage(G(sys.argv[1]), int(sys.argv[2])); g.poke(0xDF03, 0); p = g.p
N = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
p.button_press('right'); y0 = None; seen = {}; fr = 0; turned = None; camset = set()
for f in range(N):
    if f % 24 == 0: p.button_press('a')
    if f % 24 == 12: p.button_release('a')
    if f == 60: y0 = (g.peek(0xC5AB), g.peek(0xC5AD))
    if y0 and g.peek(0xC5BF) in (1, 3, 7): g.poke(0xC5AB, y0[0]); g.poke(0xC5AD, y0[1])
    g.poke(0xCAFC, 100); g.poke(0xC5C0, g.peek(0xC5C0) | 0x20)
    if turned is not None and f == turned + 60: p.button_release('left'); p.button_press('right')
    p.tick(1, False); m = p.memory
    xs = [m[0xFE01 + i] for i in range(0, 160, 4) if m[0xFE00 + i] and m[0xFE02 + i] == 0x6F]
    c = g.peek(0xC249) | g.peek(0xC24A) << 8
    if xs:
        fr += 1; camset.add(c)
        for x in xs: seen[x + c] = seen.get(x + c, 0) + 1
        if turned is None: turned = f; p.button_release('right'); p.button_press('left')
print(f'frames with a sparkle: {fr}, distinct camera positions then: {len(camset)}, world X -> frames: {dict(sorted(seen.items()))}')
