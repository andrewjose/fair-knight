"""v0.10 QUICK STAND: Down 30 -> Down+Right 10 -> release Down, keep Right held.
usage: t_qs.py ROM   (runs with FK_SET2 quick stand ON and OFF, and on the clean ROM if given --clean)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
from t_stage import start_stage
def trial(rom, set2):
    g = start_stage(G(rom), 0)
    if set2 is not None: g.poke(0xDF03, set2)
    g.run(40)
    p = g.p
    # crouch-turn and crouch-attack still work: Down+Left turns, Down+B attacks crouched
    p.button_press('down'); [p.tick(1, False) for _ in range(20)]
    p.button_press('left'); [p.tick(1, False) for _ in range(5)]
    turned = (g.peek(0xC5C0) & 1) == 0 and g.peek(0xC5BF) == 2
    p.button_release('left'); p.button_press('b'); [p.tick(1, False) for _ in range(3)]
    crouch_atk = g.peek(0xC5BF) == 2
    p.button_release('b'); p.button_release('down'); [p.tick(1, False) for _ in range(30)]
    p.button_press('right'); [p.tick(1, False) for _ in range(3)]; p.button_release('right'); [p.tick(1, False) for _ in range(10)]
    p.button_press('down')
    for _ in range(30): p.tick(1, False)
    p.button_press('right')
    for _ in range(10): p.tick(1, False)
    st0 = g.peek(0xC5BF)
    p.button_release('down')
    x0 = g.peek(0xC5AC) | g.peek(0xC5AA) << 8
    walk = None; log = []
    for f in range(300):
        p.tick(1, False)
        s = g.peek(0xC5BF); x = g.peek(0xC5AC) | g.peek(0xC5AA) << 8
        log.append(s)
        if walk is None and s == 1 and x != x0: walk = f + 1
    p.button_release('right'); p.tick(1, True)
    return st0, walk, sorted(set(log)), turned, crouch_atk
if __name__ == '__main__':
    rom = sys.argv[1]
    for name, s2 in (('KNIGHT (QS on)', 0x00), ('QS off', 0x04)):
        st0, walk, states, t, c = trial(rom, s2)
        print(f'{name}: state before release {st0}; walking after {walk} frames; states seen {states}; Down+Left turns while crouched {t}; Down+B stays crouched {c}')
    if '--clean' in sys.argv:
        st0, walk, states, t, c = trial('gng.gbc', None)
        print(f'clean ROM: state {st0}; walking after {walk}; states {states}; turn {t}; crouch atk {c}')
