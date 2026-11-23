"""SECRETS row on the Fair Knight page: cycle Right/Left through SPARKLES/MAP/OFF, check FK_SET2, presets, flicker.
usage: t_secmenu.py ROM [out.png]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_menu import tap, to_title, to_options, to_page
import numpy as np
g = G(sys.argv[1]); to_page(g)
for _ in range(8): tap(g, "down")
print('cursor', g.peek(0xDF07), 'SET2', g.peek(0xDF03))
seq = []
for k in ('right', 'right', 'right', 'left', 'left', 'left'):
    tap(g, k); seq.append(g.peek(0xDF03) & 3)
print('right x3, left x3 ->', seq, 'preset', hex(g.peek(0xDF04)))
tap(g, 'right')                                  # MAP, for the screenshot
fr = []
for _ in range(8): g.run(1); fr.append(np.array(g.p.screen.ndarray).tobytes())
print('page: distinct frames over 8 =', len(set(fr)))
if len(sys.argv) > 2: g.shot(sys.argv[2])
tap(g, 'select'); print('select (back to base preset): SET2', g.peek(0xDF03), 'preset', hex(g.peek(0xDF04)))
for _ in range(8): tap(g, "up")                  # PRESET row
r = []
for _ in range(3): tap(g, 'right'); r.append((g.peek(0xDF04), hex(g.peek(0xDF02)), g.peek(0xDF03)))
print('presets (pre, SET, SET2):', r)
