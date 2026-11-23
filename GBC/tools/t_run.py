"""Auto-runner for tests: invincible (debug flag $C0A1 bit 1), holds Right, jumps when blocked,
optionally tries Up (ladders). run(g, frames, cb) calls cb(g, f) each frame."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
def X(g): return g.peek(0xC5AA) * 16 + g.peek(0xC5AC) // 16
def autorun(g, frames, cb=None, up=False, direction='right', inv=True):
    last = X(g); still = 0; jt = 0
    g.p.button_press(direction)
    for f in range(frames):
        if inv: g.poke(0xC0A1, g.peek(0xC0A1) | 2)
        st = g.peek(0xC5BF)
        if up and st != 4 and f % 40 == 0: g.p.button_press('up')
        if up and st != 4 and f % 40 == 20: g.p.button_release('up')
        if st == 4 and up: g.p.button_press('up')
        x = X(g); still = still + 1 if x == last else 0; last = x
        if jt: jt -= 1
        if jt == 1: g.p.button_release('a')
        if still > 8 and st == 1 and not jt: g.p.button_press('a'); jt = 6; still = 0
        g.p.tick(1, False)
        if cb and cb(g, f): break
    for k in (direction, 'a', 'up'): g.p.button_release(k)
    g.run(0)
