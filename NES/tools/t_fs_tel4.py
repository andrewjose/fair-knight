# FAIR SPAWNS telegraph test with a flyer that is harmful at once (type 4, stage 1 end, generator $8610).
# Test-only ROM variants: the $8718 offset table is set so every type-4 spawn lands exactly on Arthur
# (dx 0, Y 184 = Arthur standing on the ground); "nonudge" also disables the 32 px push.
import numpy as np, sys
from stagesel import goto
OFF=lambda b,a: 16+b*0x4000+a-0x8000
def variant(src, out, nonudge=False):
    d=bytearray(open(src,'rb').read())
    for i in range(16):
        d[OFF(2,0x8718)+3*i]=0; d[OFF(2,0x8718)+3*i+1]=0; d[OFF(2,0x8718)+3*i+2]=184
    if nonudge:
        bank2=bytes(d[OFF(2,0x8000):OFF(2,0xC000)])
        i=bank2.find(bytes([0x00,0x03,0x04,0x06,0x07,0x14]),0xBB67-0x8000); assert i>0
        for k in range(6): d[OFF(2,0x8000)+i+k]=0xFE
    open(out,'wb').write(d)
def run(rom, fk, frames=900):
    e=goto(rom, 2, 1, fk)
    seen=set(); spawns=[]; hit=None
    for f in range(frames):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.run(1)
        ax=e.peek(0x583)*256+e.peek(0x5AF)
        for s in range(1,17):
            fl=e.peek(0x4F0+s)
            if fl and e.peek(0x631+s)==4 and s not in seen:
                seen.add(s); spawns.append((f,s,e.peek(0x583+s)*256+e.peek(0x5AF+s)-ax))
            if not fl: seen.discard(s)
        if spawns and (e.peek(0x4F0)&0x08):
            hit=f; break
        if f==60: e.shot(f'tel4_{rom[:-4]}_{fk}.png'.replace(' ','').replace(',','_'))
    return spawns,hit
if __name__=='__main__':
    rom=sys.argv[1]
    variant('gng.nes','tst4_clean.nes'); variant(rom,'tst4_fs.nes'); variant(rom,'tst4_fs_nonudge.nes',nonudge=True)
    for name,r,fk in [('clean ROM','tst4_clean.nes',None),('v0.5 ORIGINAL','tst4_fs.nes',(0xFF,0xC2)),
                      ('v0.5 KNIGHT, push disabled','tst4_fs_nonudge.nes',(0,0)),('v0.5 KNIGHT','tst4_fs.nes',(0,0))]:
        sp,hit=run(r,fk)
        last=[s for s in sp if hit is None or s[0]<=hit]
        print(f'{name:28} flyer spawns {len(sp)} (first {sp[:2]})  Arthur hit at {hit}  -> {None if hit is None or not last else hit-last[-1][0]} frames after the latest spawn before it')
