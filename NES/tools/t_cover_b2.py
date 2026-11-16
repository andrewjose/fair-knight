# Does the original game ever read bank 2 $BB67-$BFFF (the padding v0.5 uses)? Replay play in every
# section on py65 with the CLEAN ROM and log any CPU read of that range while bank 2 is mapped.
import numpy as np, random
from stagesel import goto
import trace as T
from py65.devices.mpu6502 import MPU
class Mem2(T.Mem):
    hits=[]
    def __getitem__(s,a):
        if isinstance(a,int) and 0xBB67<=a<0xC000 and s.bank==2: Mem2.hits.append((s.pc,a))
        return T.Mem.__getitem__(s,a)
def replay(state, nframes, pad=0):
    s=[int(x) for x in state]; ram=bytes(s[25570:25570+0x800]); m=Mem2(ram,ram[0xC7]&7,pad)
    cpu=MPU(memory=m,pc=s[6]|s[7]<<8); cpu.sp=s[5]; cpu.a=s[1]; cpu.x=s[2]; cpu.y=s[3]
    end=cpu.processorCycles+29781*nframes; nmi=cpu.processorCycles+29781
    while cpu.processorCycles<end:
        if cpu.processorCycles>=nmi:
            nmi+=29781
            for v in (cpu.pc>>8,cpu.pc&0xff,cpu.p&~0x10): m[0x100+cpu.sp]=v; cpu.sp=(cpu.sp-1)&0xff
            cpu.p|=0x04; cpu.pc=0xC0F0
        m.pc=(cpu.pc,m.bank); cpu.step()
random.seed(5)
total=0
for ac in range(14):
    e=goto('gng.nes',ac,200)
    for blk in range(6):
        for f in range(random.randint(30,80)): e.run(1,random.choice(['R','R+A','R+B','L','']))
        while True:
            st=np.array(e.n.save())
            if st[6]==0xF0 and st[7]==0xC0: break
            e.run(1)
        replay(st,20)
        total+=20
print('frames replayed',total,'reads of bank 2 $BB67-$BFFF:',len(Mem2.hits), Mem2.hits[:5])
