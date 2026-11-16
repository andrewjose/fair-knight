# Endgame aid v0.4: fixed cross on the floor below the stage 6 boss (floor y=440, X=214).
# Starts from g6_11.npy (clean-ROM save state, Arthur on floor 12) loaded into the test ROM.
import numpy as np, sys
from gnav import N
from rec import grid
ROM=sys.argv[1]
def crosses(n): return [y for y in range(1,17) if n.e.peek(0x4F0+y) and n.e.peek(0x631+y)==0x10 and n.e.peek(0x61D+y)==9 and n.e.peek(0x56D+y)==1]
def setup(rom,fk,weapon=None):
    n=N(rom,state=np.load('g6_11.npy'))
    n.e.poke(0x7FA,fk[0]); n.e.poke(0x7FB,fk[1])
    if weapon is not None: n.e.poke(0x53A,weapon)
    n.mode='mercy'; return n
def wait_cross(n,frames=240):
    for f in range(frames):
        n.step('')
        c=crosses(n)
        if c: return f,c[0]
    return None
def finish(n):
    n.e.poke(0xBF,1); sec=[n.e.peek(0xAC)]
    for f in range(900):
        n.e.run(1)
        if n.e.peek(0xBF): n.e.poke(0xBF,1)
        s=n.e.peek(0xAC)
        if sec[-1]!=s: sec.append(s)
        if len(sec)>1: n.e.poke(0xBF,0)
    return sec
P=[]; R={}
# 1 KNIGHT with the lance: cross appears, sits still, pickup, clear -> 13
n=setup(ROM,(0,0)); print('start',n.st(),'weapon',hex(n.e.peek(0x53A)))
r=wait_cross(n); print('knight spawn (frame,slot)',r)
if r:
    s=r[1]; p0=(n.e.peek(0x583+s),n.e.peek(0x5AF+s),n.e.peek(0x56D+s),n.e.peek(0x599+s))
    n.run('',120); p1=(n.e.peek(0x583+s),n.e.peek(0x5AF+s),n.e.peek(0x56D+s),n.e.peek(0x599+s))
    print('cross pos (page,x,yh,y) at spawn',p0,'2s later',p1)
    P.append(n.shot('eg4_cross'))
    # despawn and see it come back (same path as after a death/continue: nothing remembers it)
    n.e.poke(0x4F0+s,0); r2=wait_cross(n); print('respawn after removal',r2)
    n.mode='clear'; n.walk_to(214,600,tol=3)
    for i in range(60):
        n.step('')
        if n.e.peek(0x53A)==0x4F: break
    print('weapon after walking over it',hex(n.e.peek(0x53A)))
    P.append(n.shot('eg4_pickup'))
    nr=wait_cross(n,240); print('spawn while holding cross',nr)
    R['knight']=finish(n)
# 2 ORIGINAL preset and 3 KNIGHT with ENDGAME AID OFF
for tag,fk in [('orig',(0xFF,0x82)),('aidoff',(0,0x80))]:
    n=setup(ROM,fk); r=wait_cross(n,300); print(tag,'spawn',r); n.walk_to(214,600,tol=3)
    P.append(n.shot('eg4_'+tag)); R[tag]=finish(n)
for k,v in R.items(): print(k,'section path after clear',v)
grid(P,'endgame4.png',3)
