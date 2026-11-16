# v0.4 secret markers: found tracking, READY-screen summary, sparkles, OFF.
import sys, csv, numpy as np
from gnav import N
from rec import grid
ROM=sys.argv[1]
rows=list(csv.DictReader(open('secrets.csv')))
idx={(int(r['section']),int(r['x'])):i for i,r in enumerate(rows)}
def found(n): return [i for i in range(len(rows)) if n.e.peek(0x4C4+(i>>3))&(1<<(i&7))]
def setfk(n,s,p=0):
    n.e.poke(0x7FA,s); n.e.poke(0x7FB,p)
def travel(n,x):
    n.mode='mercy'
    for _ in range(400):
        if abs(x-n.wx())<3 or n.wx()==0: break
        n.walk_to(x,15)
def reveal(n,x,duck):
    travel(n,x-40); n.walk_to(x,800,tol=1)
    slot=[k for k in range(1,22) if n.e.peek(0x4F0+k) and n.e.peek(0x631+k)==0x11 and n.e.peek(0x583+k)*256+n.e.peek(0x5AF+k)==x]
    slot=slot[0] if slot else None
    n.mode='clear'
    for t in range(15):
        if n.wx()!=x: n.walk_to(x,200,tol=0,jump=False)
        for i in range(40):
            n.step('D' if duck else ('A' if i<8 else ''))
            if slot and n.e.peek(0x631+slot)==0x12: return True
    return False
def timeout_death(n, tag):
    n.mode='clear'
    for a in (0x6F6,0x6F8,0x6FA): n.e.poke(a,0)
    n.e.poke(0x6FC,1)
    shots=[]
    for i in range(900):
        n.e.run(1)
        if i%15==0 and n.e.peek(0x4F1)==0x80 and n.e.peek(0x523)==0x1D:   # READY screen lives icon
            n.e.run(20); shots.append(n.shot(tag)); break
    return shots
P=[]
# A: KNIGHT (SECRETS = MAP): reveal two stage 4 items, then lose a life and look at the READY screen
n=N(ROM,sec=10); setfk(n,0x01)   # v0.5.2: MAP = 01
print('before', found(n))
for x,duck in [(1264,1),(2160,0)]:
    ok=reveal(n,x,duck); print('reveal',x,ok,'found bits ->',found(n),'expected index',idx[(10,x)])
P+=timeout_death(n,'sec_ready_map')
print('found after death', found(n), 'sig', hex(n.e.peek(0x4C8)))
# B: SPARKLES: duck star (4B 1264), normal spark (4B 2160), red spark (1B 2000, time down)
for sec,x,tag in [(10,1264,'spark_duck'),(10,2160,'spark_norm'),(1,2000,'spark_red')]:
    n=N(ROM,sec=sec); setfk(n,0x00); travel(n,x-70); n.mode='clear'
    best=None
    for i in range(40):
        n.step('')
        sl=[k for k in range(1,22) if n.e.peek(0x4F0+k) and n.e.peek(0x631+k)==0x11]
        vis=[(k,hex(n.e.peek(0x4F0+k)),hex(n.e.peek(0x522+k)),n.e.peek(0x53B+k)) for k in sl if n.e.peek(0x4F0+k)&0x80]
        if vis and best is None: best=vis; P.append(n.shot(tag))
    print(tag,'visible sparkle objects',best)
# C: OFF: same spot, nothing drawn; READY screen without the summary
n=N(ROM,sec=10); setfk(n,0x03); travel(n,1264-70); n.mode='clear'
vis=0
for i in range(40):
    n.step('')
    vis+=sum(1 for k in range(1,22) if n.e.peek(0x4F0+k)&0x80 and n.e.peek(0x631+k)==0x11)
P.append(n.shot('spark_off')); print('OFF visible hidden-item frames',vis)
P+=timeout_death(n,'sec_ready_off')
grid(P,'secrets_test.png',3)
