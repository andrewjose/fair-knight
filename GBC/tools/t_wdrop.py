"""Weapon drop test: spawn a weapon item (game's own spawner $45D0) 40 px ahead of Arthur, walk into it.
usage: t_wdrop.py ROM [FK_SET hex] [weapon 0-4]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gemu import G
def start(g, fkset=None):
    g.run(660)
    if fkset is not None: g.poke(0xDF02, fkset)
    for _ in range(5): g.run(3, 'start'); g.run(110)
    for _ in range(600):          # wait until Arthur is standing (state 1) in stage 1
        g.run(0)
        if g.peek(0xC5BF) == 1 and g.peek(0xC5A6) == 0xEB and g.peek(0xC5A7) == 0x2F: break
    return g
def call(g, addr, de):
    rf = g.p.register_file
    sp = rf.SP - 2; g.poke(sp, rf.PC & 0xFF); g.poke(sp + 1, rf.PC >> 8)
    rf.SP = sp; rf.PC = addr; rf.D = de >> 8; rf.E = de & 0xFF
def spawn_item(g, w, dx_px):
    ax = g.peek(0xC5AA) * 16 + g.peek(0xC5AC) // 16 + dx_px
    g.poke(0xFF90, ax // 16); g.poke(0xFF92, (ax % 16) * 16)
    g.poke(0xFF91, g.peek(0xC5AB)); g.poke(0xFF93, 0)
    b = g.peek(0x7FFF)            # stub in free WRAM: map bank 1, call the spawner, restore the bank
    stub = [0x3E, 1, 0xEA, 0x00, 0x21, 0xCD, 0xD0, 0x45, 0x3E, b, 0xEA, 0x00, 0x21, 0xC9]
    for i, x in enumerate(stub): g.poke(0xDE00 + i, x)
    call(g, 0xDE00, 0x49A7 + 7 * w)
def items(g):
    out = []
    for s in range(32):
        b = 0xC5A4 + s * 32
        if g.peek(b + 1) & 1 and g.peek(b + 0x19) | g.peek(b + 0x1A) << 8 in range(0x49A7, 0x49CA, 7):
            out.append((s, g.peek(b + 0x1F), g.peek(b + 6) * 16 + g.peek(b + 8) // 16, g.peek(b + 7)))
    return out
if __name__ == '__main__':
    fk = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    g = start(G(sys.argv[1]), fk)
    ax = lambda: g.peek(0xC5AA) * 16 + g.peek(0xC5AC) // 16
    print('arthur x', ax(), 'weapon', g.peek(0xC0B6))
    spawn_item(g, w, 40); g.run(30); print('spawned', items(g)); g.shot('/tmp/wd0.png')
    for f in range(60):
        g.run(1, 'right')
        if g.peek(0xC0B6) == w: break
    print('picked at arthur x', ax(), 'weapon now', g.peek(0xC0B6)); g.run(30); g.shot('/tmp/wd1.png')
    print('items after', items(g))
    for f in range(60):
        g.run(1, 'left')
        if g.peek(0xC0B6) != w: break
    print('walk back: weapon', g.peek(0xC0B6), 'arthur x', ax(), 'items', items(g)); g.run(20); g.shot('/tmp/wd2.png')
