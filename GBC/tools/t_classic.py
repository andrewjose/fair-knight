"""Classic-edition test: run stages 1, 3 and 4 past their secret spots with SECRETS forced to a value,
count frames with sparkle-marker sprites in OAM and read VRAM tile $6F (bank 0) on the way.
usage: t_classic.py ROM SET2 [shotprefix]      (SET2: 0 = KNIGHT default, 1 = MAP, 3 = OFF)
Prints one line per stage: marker frames, tile-$6F states seen, X reached."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
from t_run import autorun, X
SPOTS = {1: 1872, 3: 2240, 4: 2176}          # world X of a secret per stage (secrets.csv / v0.9 tests)
MARK_TILES = (0x6F,)          # SPK_T, the sparkle tile (only Fair Knight sparkles use it)
def tile6f(g):
    vb = g.p.memory[0xFF4F]
    return bytes(g.p.memory[0x86F0 + i] for i in range(16)) if (vb & 1) == 0 else None
def markers(g):
    m = g.p.memory
    return sum(1 for i in range(0, 160, 4) if m[0xFE00 + i] and m[0xFE02 + i] in MARK_TILES)
if __name__ == '__main__':
    rom, s2 = sys.argv[1], int(sys.argv[2], 0)
    pre = sys.argv[3] if len(sys.argv) > 3 else None
    for st, spot in SPOTS.items():
        g = G(rom); g.run(10); g.poke(0xDF03, s2)
        start_stage(g, st - 1); g.poke(0xDF03, s2)
        res = {'mf': 0, 'tiles': set(), 'shot': False}
        def cb(g, f):
            g.poke(0xDF03, s2)
            n = markers(g)
            if n: res['mf'] += 1
            if f % 30 == 0:
                t = tile6f(g)
                if t is not None: res['tiles'].add(t.hex())
            if pre and not res['shot'] and abs(X(g) - spot) < 24 and markers(g) + (1 if 'cls' in pre or 'clean' in pre else 0):
                g.p.tick(1, True); g.shot(f'{pre}_s{st}.png'); res['shot'] = True
            return X(g) > spot + 120
        autorun(g, 5000, cb)
        print(f'stage {st}: marker frames {res["mf"]}, tile $6F states {sorted(res["tiles"])}, X {X(g)} (spot {spot})')
