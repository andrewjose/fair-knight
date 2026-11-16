# What are the type-0 objects that appear exactly on Arthur (dx 0, dy 0) in sections 1/4/5/11?
import random
from stagesel import goto
random.seed(1); e=goto('v05c.nes',1,300,(0,0))
keys=['R','R','R','R+B','L','','R+A','U','D']; k='R'
for f in range(300):
    e.poke(0x7FA,0); e.poke(0x7FB,0)
    e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x21); e.poke(0x647,0)
    if f%20==0: k=random.choice(keys)
    e.run(1,k)
    if f in (294,295,296,300-1):
        print(f,[(s,hex(e.peek(0x4F0+s)),hex(e.peek(0x631+s)),e.peek(0x5AF+s),e.peek(0x599+s),hex(e.peek(0x522+s)),hex(e.peek(0x4C9+((s&15)>>1)))) for s in (0,1,3)])
e.shot('fs_t0.png')
