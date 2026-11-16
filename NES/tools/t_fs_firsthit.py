# FAIR SPAWNS: for each section, stand still from the start and report the first hit (armor lost),
# what hit Arthur, and the age of the closest enemy at that moment. Original vs KNIGHT.
import sys
from stagesel import goto
def first_hit(rom, fk, ac, frames=1500):
    e=goto(rom, ac, 1, fk)
    born={}
    for f in range(frames):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.run(1)
        for s in range(1,17):
            if e.peek(0x4F0+s):
                born.setdefault(s,f)
            else: born.pop(s,None)
        if e.peek(0x4F0)&0x20 or e.peek(0x4F0)&0x08:
            ax=e.peek(0x583)*256+e.peek(0x5AF); ay=e.peek(0x56D)*256+e.peek(0x599)
            best=None
            for s in range(1,17):
                if not e.peek(0x4F0+s): continue
                d=abs(e.peek(0x583+s)*256+e.peek(0x5AF+s)-ax)+abs(e.peek(0x56D+s)*256+e.peek(0x599+s)-ay)
                if best is None or d<best[0]: best=(d,s,e.peek(0x631+s),f-born.get(s,f))
            return f,best
    return None,None
if __name__=='__main__':
    rom=sys.argv[1]
    for ac in range(14):
        a=first_hit('gng.nes',None,ac); b=first_hit(rom,(0,0),ac)
        print(f'section {ac:2}: original hit at {a[0]} by {a[1]}   KNIGHT hit at {b[0]} by {b[1]}   (dist, slot, type, age frames)')
