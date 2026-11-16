# FAIR SPAWNS: log every new object's distance from Arthur on its spawn frame, original vs KNIGHT,
# in every section that has a bank-2 generator, with Arthur invulnerable (poked mercy) and a random walk.
import numpy as np, sys, random
from stagesel import goto
GEN_TYPES={0,3,4,6,7,0x14}
def run(rom, fk, ac, frames, seed):
    random.seed(seed)
    e=goto(rom, ac, 300, fk)
    prev=[e.peek(0x4F0+s) for s in range(22)]
    out=[]; zmax=0
    keys=['R','R','R','R+B','L','','R+A','U','D']
    k='R'
    for f in range(frames):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x21); e.poke(0x647,0)
        if f%20==0: k=random.choice(keys)
        e.run(1,k)
        ax=e.peek(0x583)*256+e.peek(0x5AF); ay=e.peek(0x56D)*256+e.peek(0x599)
        z=0
        for s in range(1,17):
            fl=e.peek(0x4F0+s); t=e.peek(0x631+s)
            if fl and t==0: z+=1
            if fl and not prev[s]:
                ox=e.peek(0x583+s)*256+e.peek(0x5AF+s); oy=e.peek(0x56D+s)*256+e.peek(0x599+s)
                out.append((f,s,t,ox-ax,oy-ay))
            prev[s]=fl
        zmax=max(zmax,z)
    return out,zmax
if __name__=='__main__':
    rom=sys.argv[1]
    for ac in [0,1,2,4,5,11,12]:
        for name,r,fk in [('orig','gng.nes',None),('knight',rom,(0,0))]:
            out,zmax=run(r,fk,ac,2500,ac)
            gen=[o for o in out if o[2] in GEN_TYPES]
            near=[o for o in gen if abs(o[3])<32 and abs(o[4])<48]
            mind=min([abs(o[3]) for o in gen if abs(o[4])<48],default=None)
            print(f'section {ac:2} {name:6} new objects {len(out):3}  generator-type {len(gen):3}  within 32px {len(near):2}  min|dx| {mind}  max zombies {zmax}')
            if near: print('   near:',near[:6])
