"""v0.10 Fair Knight page: QUICKSTAND (row 9) and CAMERA (row 10) toggle FK_SET2 bits 2/3, presets,
SECRETS still cycles, EXIT is row 11, no flicker while changing rows/values.  usage: t_menu10.py ROM [out.png]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G, grid
from t_menu import tap, to_page
import numpy as np
def frames(g, n=10):
    fr = []
    for _ in range(n): g.run(0); fr.append(np.array(g.p.screen.ndarray).tobytes())
    return len(set(fr))
g = G(sys.argv[1]); to_page(g); P = []
def sh(t): fn = f'/tmp/m10_{len(P)}_{t}.png'; g.shot(fn); P.append(fn)
sh('page')
r = []
for _ in range(3): tap(g, 'right'); r.append((g.peek(0xDF04), hex(g.peek(0xDF02)), hex(g.peek(0xDF03)))); sh(f'pre{len(r)}')
print('PRESET right x3 (pre, SET, SET2):', r)
for _ in range(9): tap(g, 'down')
print('row', g.peek(0xDF07), 'SET2', hex(g.peek(0xDF03))); sh('qs_row')
tap(g, 'right'); a = hex(g.peek(0xDF03)); sh('qs_off'); tap(g, 'left'); b = hex(g.peek(0xDF03))
print('QUICKSTAND right/left SET2:', a, b, 'preset', hex(g.peek(0xDF04)))
tap(g, 'down'); print('row', g.peek(0xDF07)); sh('cam_row')
tap(g, 'a'); a = hex(g.peek(0xDF03)); sh('cam_center'); tap(g, 'a'); b = hex(g.peek(0xDF03))
print('CAMERA A/A SET2:', a, b)
print('distinct frames over 10, idle:', frames(g))
fr = []
for k in ('right', 'up', 'down', 'right'):
    g.run(3, k)
    for _ in range(12): g.run(0); fr.append(np.array(g.p.screen.ndarray).tobytes())
# a value change redraws in one frame: count frames between the change and a stable picture
print('changes: distinct pictures over 4 inputs x 13 frames =', len(set(fr)))
tap(g, 'down'); print('row', g.peek(0xDF07), '(EXIT = 11)'); sh('exit_row')
tap(g, 'up'); tap(g, 'up'); tap(g, 'select'); print('select -> SET2', hex(g.peek(0xDF03)), 'pre', hex(g.peek(0xDF04)))
tap(g, 'down'); tap(g, 'down'); tap(g, 'a', 40); print('A on EXIT -> options cursor', g.peek(0xC1E9)); sh('back')
grid(P, sys.argv[2] if len(sys.argv) > 2 else '/tmp/menu10.png', 4)
