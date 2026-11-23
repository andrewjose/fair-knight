"""GBC Fair Knight: open OPTIONS -> FAIR KNIGHT page, exercise it, screenshot each step."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from gemu import G, grid
import numpy as np
ROM = sys.argv[1] if len(sys.argv) > 1 else None
def tap(g, k, w=12): g.run(3, k); g.run(w)
def to_title(g): g.run(660); return g
def to_options(g):
    to_title(g); tap(g, 'down'); tap(g, 'a', 40); return g
def to_page(g):
    to_options(g); tap(g, 'down'); tap(g, 'down'); tap(g, 'a', 40); return g
if __name__ == '__main__':
    g = G(ROM); P = []
    def sh(tag):
        fn = f'/tmp/gm_{len(P)}_{tag}.png'; g.shot(fn); P.append(fn)
    to_options(g); sh('opts'); tap(g, 'down'); tap(g, 'down'); sh('opts_fk_row')
    print('opt cursor', g.peek(0xC1E9))
    tap(g, 'a', 40); sh('page'); print('page cur', g.peek(0xDF07), 'set', hex(g.peek(0xDF02)), 'pre', hex(g.peek(0xDF04)))
    tap(g, 'down'); sh('down1'); tap(g, 'right'); sh('knock_on'); print('set', hex(g.peek(0xDF02)), 'pre', hex(g.peek(0xDF04)))
    tap(g, 'up'); tap(g, 'right'); sh('legend'); print('legend set', hex(g.peek(0xDF02)), 'pre', hex(g.peek(0xDF04)))
    tap(g, 'select'); sh('reset')
    tap(g, 'b', 40); sh('back'); print('after exit opt cursor', g.peek(0xC1E9))
    grid(P, sys.argv[2] if len(sys.argv) > 2 else 'menu_test.png', 4)
