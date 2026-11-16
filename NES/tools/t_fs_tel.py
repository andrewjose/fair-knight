# FAIR SPAWNS telegraph test. Test-only ROM variants put every stage 1 zombie spawn exactly on Arthur and lift the zombie cap
# (zombie offset table bank 2 $84A7 zeroed). Variant "nonudge" also disables the 32 px push so the
# telegraph alone is tested. Arthur stands still; we log when the first zombie appears and when he is hit.
import numpy as np, sys
from emu import Emu
OFF=lambda b,a: 16+b*0x4000+a-0x8000
def variant(src, out, zero_table=True, nonudge=False, nocap=False):
    d=bytearray(open(src,'rb').read())
    if nocap:
        bank2=bytes(d[OFF(2,0x8000):OFF(2,0xC000)])
        i=bank2.find(bytes([0xC0,0x03,0x90]),0xBB67-0x8000)   # CPY #FS_ZCAP / BCC in fk_zgen
        assert i>0; d[OFF(2,0x8000)+i+1]=99
    if zero_table:
        for i in range(16):
            d[OFF(2,0x84A7)+3*i]=0; d[OFF(2,0x84A7)+3*i+1]=0
    if nonudge:
        bank2=bytes(d[OFF(2,0x8000):OFF(2,0xC000)])
        i=bank2.find(bytes([0x00,0x03,0x04,0x06,0x07,0x14]),0xBB67-0x8000)
        assert i>0
        for k in range(6): d[OFF(2,0x8000)+i+k]=0xFE
    open(out,'wb').write(d)
def run(rom, fk, frames=400):
    e=Emu(rom); e.n.load(np.load('st_play.npy'))
    if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    for s in range(1,17):           # start with no enemies on screen (old zombies would muddy the test)
        e.poke(0x4F0+s,0)
    born={}; spawn=None; log=[]
    for f in range(frames):
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.run(1)
        ax=e.peek(0x583)*256+e.peek(0x5AF)
        for s in range(1,17):
            fl=e.peek(0x4F0+s)
            if fl and e.peek(0x631+s)==0 and s not in born:
                born[s]=f
                ox=e.peek(0x583+s)*256+e.peek(0x5AF+s)
                if spawn is None and f>5: spawn=(f,ox-ax)
            if not fl: born.pop(s,None)
        if spawn and (e.peek(0x4F0)&0x08):   # bit 3 = in hit
            return spawn,f
    return spawn,None
if __name__=='__main__':
    rom=sys.argv[1]
    variant('gng.nes','tst_clean0.nes'); variant(rom,'tst_fs0.nes',nocap=True); variant(rom,'tst_fs0_nonudge.nes',nonudge=True,nocap=True)
    for name,r,fk in [('clean ROM, zombies spawn on Arthur','tst_clean0.nes',None),
                      ('v0.5 ORIGINAL preset','tst_fs0.nes',(0xFF,0xC2)),
                      ('v0.5 KNIGHT, push disabled (telegraph only)','tst_fs0_nonudge.nes',(0,0)),
                      ('v0.5 KNIGHT (push + telegraph)','tst_fs0.nes',(0,0))]:
        sp,hit=run(r,fk)
        print(f'{name:48} first zombie at frame {sp[0]} dx {sp[1]:4}   Arthur hit at frame {hit}  ->  {None if hit is None else hit-sp[0]} frames after the spawn')
