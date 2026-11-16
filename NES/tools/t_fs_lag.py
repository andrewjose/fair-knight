# CPU load: replay a busy stretch (stage 1 graveyard, zombies out, Arthur walking) on py65 and measure
# how many CPU cycles per frame are spent idling in the scheduler's wait loop ($C39C-$C3A1).
# Less idle = more work. Also counts "lag frames": frames where the logic tick could not start on time.
import numpy as np, sys
from emu import Emu
from trace import Mem
from py65.devices.mpu6502 import MPU
def state_at(rom, fk, frames, keys):
    e=Emu(rom); e.n.load(np.load('st_play.npy'))
    if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
    f=0
    while True:
        if fk: e.poke(0x7FA,fk[0]); e.poke(0x7FB,fk[1])
        e.poke(0x4F0,(e.peek(0x4F0)|0x40)&~0x21); e.poke(0x647,0)
        s=np.array(e.n.save())
        if f>=frames and s[6]==0xF0 and s[7]==0xC0: return s
        e.run(1,keys(f)); f+=1
def idle(state, nframes, rom):
    import trace as T
    T.ROM=open(rom,'rb').read()[16:]; T.BANKS=[T.ROM[i*0x4000:(i+1)*0x4000] for i in range(8)]
    import importlib
    s=[int(x) for x in state]; ram=bytes(s[25570:25570+0x800]); m=T.Mem(ram,ram[0xC8]&7)
    cpu=MPU(memory=m,pc=s[6]|s[7]<<8); cpu.sp=s[5]
    start=cpu.processorCycles; nmi_at=start+29781; idle=0; per=[]; fi=0; fidle=0
    while cpu.processorCycles<start+29781*nframes:
        if cpu.processorCycles>=nmi_at:
            nmi_at+=29781; per.append(fidle); fidle=0
            for v in (cpu.pc>>8,cpu.pc&0xff,cpu.p&~0x10): m[0x100+cpu.sp]=v; cpu.sp=(cpu.sp-1)&0xff
            cpu.p|=0x04; cpu.pc=0xC0F0
        pc=cpu.pc; c0=cpu.processorCycles; m.pc=(pc,m.bank); cpu.step()
        if 0xC39C<=pc<=0xC3A0: fidle+=cpu.processorCycles-c0
    return per
if __name__=='__main__':
    rom=sys.argv[1]
    keys=lambda f:'R' if f%40<20 else ''
    for name,r,fk in [('clean','gng.nes',None),('v0.5 ORIGINAL',rom,(0xFF,0xC2)),('v0.5 KNIGHT',rom,(0,0))]:
        st=state_at(r,fk,300,keys)
        per=idle(st,120,r)
        per=np.array(per)
        print(f'{name:14} idle cycles per frame: mean {per.mean():7.0f} of 29781 ({per.mean()/297.81:4.1f}%)  min {per.min():6}  frames with <500 idle cycles: {(per<500).sum()}/{len(per)}')
