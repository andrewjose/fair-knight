"""Fair Knight Genesis core checks. usage: t_core.py FK_ROM
1) knockback / mercy per setting from the stage 1 idle hit
2) ORIGINAL (FK_SET=$FF) vs the clean ROM, RAM compared every frame (idle 600, bot 3000).
   The stack scratch below SP ($FFFD00-$FFFDFF) is excluded: the new JSRs leave return-address residue there."""
import sys, subprocess, numpy as np, os
T = os.path.dirname(os.path.abspath(__file__)); G = os.path.dirname(T)
FK = sys.argv[1]; ST = os.path.join(G, 'st_play.bin'); CLEAN = os.path.join(G, 'gng.md')
def run(rom, fks, n, script, out):
    subprocess.run([sys.executable, os.path.join(T, 'run1.py'), rom, ST, fks, str(n), script, out], check=True)
    return np.load(out)
def measure(R):
    x = R[:, 0xB200].astype(int) * 256 + R[:, 0xB201]; y = R[:, 0xB204].astype(int) * 256 + R[:, 0xB205]
    hit = next(f for f in range(1, len(R)) if x[f] != x[f-1] or y[f] != y[f-1] and f > 200)
    fl = [f for f in range(1, len(R)) if R[f, 0xB20C] != R[f-1, 0xB20C]]
    return hit, x[hit-1], x[min(hit+45, len(R)-1)], (fl[0], fl[-1]) if fl else None
res = {}
for tag, rom, s in [('clean', CLEAN, 'none'), ('KNIGHT', FK, '0x00'), ('ORIGINAL', FK, '0xFF'),
                    ('knockback ON', FK, '0x01'), ('mercy NORMAL', FK, '0x02')]:
    R = run(rom, s, 700, 'idle', '/tmp/tc.npy'); hit, x0, x1, fl = measure(R)
    res[tag] = (x1 - x0, fl)
    print(f'{tag:13s} hit@{hit} X {x0}->{x1} ({x1-x0:+d})  flicker frames {fl} ({fl[1]-fl[0] if fl else 0})')
for script, n in [('idle', 600), ('bot', 3000)]:
    A = run(CLEAN, 'none', n, script, '/tmp/ta.npy'); B = run(FK, '0xFF', n, script, '/tmp/tb.npy')
    mask = np.ones(0x10000, bool); mask[0xFD00:0xFE00] = False; mask[0x5A00] = False
    bad = [f for f in range(n) if (A[f][mask] != B[f][mask]).any()]
    print(f'ORIGINAL vs clean, {script} {n} frames: {len(bad)} frames differ', bad[:5])
