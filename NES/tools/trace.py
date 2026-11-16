# py65-based one-tick tracer: runs the game's scheduler tick from a cynes RAM snapshot
import numpy as np
from py65.devices.mpu6502 import MPU
ROM=open('gng.nes','rb').read()[16:]
BANKS=[ROM[i*0x4000:(i+1)*0x4000] for i in range(8)]
class Mem:
    def __init__(s,ram,bank,pad=0):
        s.ram=bytearray(ram); s.bank=bank; s.writes=[]; s.reads=[]; s.pc=None; s.pad=pad; s.shift=0
    def __getitem__(s,a):
        if isinstance(a,slice): return [s[i] for i in range(*a.indices(0x10000))]
        if a<0x2000: return s.ram[a&0x7ff]
        if a<0x4000:
            return 0x80 if (a&7)==2 else 0
        if a==0x4016:
            v=(s.pad>>(7-s.shift))&1 if s.shift<8 else 1; s.shift+=1; return v
        if a<0x8000: return 0
        if a<0xC000: return BANKS[s.bank][a-0x8000]
        return BANKS[7][a-0xC000]
    def __setitem__(s,a,v):
        if a<0x2000:
            s.ram[a&0x7ff]=v; s.writes.append((s.pc,a&0x7ff,v,s.bank))
        elif a==0x4016: s.shift=0
        elif a>=0x8000: s.bank=v&7
    def __len__(s): return 0x10000
def tick(ram,pad=0,maxsteps=200000,watch=None):
    m=Mem(ram,ram[0xC8]&7,pad)
    m.ram[0x4E]=max(m.ram[0x4E],m.ram[0xCD])
    cpu=MPU(memory=m,pc=0xC39C); cpu.sp=0xFF
    log=[]
    for i in range(maxsteps):
        m.pc=(cpu.pc,m.bank); cpu.step()
        if cpu.pc==0xC39C and i>10: break
    return m
def frame(ram,pad=0,maxsteps=400000):
    m=Mem(ram,ram[0xC8]&7,pad)
    cpu=MPU(memory=m,pc=0xC39C); cpu.sp=0xFF
    # fake an NMI: push return addr C39C and flags
    def push(v): m[0x100+cpu.sp]=v; cpu.sp=(cpu.sp-1)&0xFF
    push(0xC3); push(0x9C); push(0x20)
    cpu.pc=0xC0F0
    n=0; nmi_done=False
    for i in range(maxsteps):
        m.pc=(cpu.pc,m.bank)
        op=m[cpu.pc]
        cpu.step()
        if op==0x40: nmi_done=True
        if nmi_done and cpu.pc==0xC39C:
            n+=1
            if m.ram[0x4E]<m.ram[0xCD]: break
    return m,cpu
def run_frames(state, nframes=1, pad=0, bank=None):
    """state: cynes save array taken at a frame boundary. Returns Mem with write log."""
    s=[int(x) for x in np.asarray(state)]
    ram=bytes(s[25570:25570+0x800])
    m=Mem(ram, (ram[0xC8]&7) if bank is None else bank, pad)
    cpu=MPU(memory=m,pc=s[6]|s[7]<<8); cpu.sp=s[5]; cpu.a=s[1]; cpu.x=s[2]; cpu.y=s[3]
    target=cpu.processorCycles+29781*nframes
    nmi_at=cpu.processorCycles+29781
    while cpu.processorCycles<target:
        if cpu.processorCycles>=nmi_at:
            nmi_at+=29781
            for v in (cpu.pc>>8,cpu.pc&0xff,cpu.p&~0x10): m[0x100+cpu.sp]=v; cpu.sp=(cpu.sp-1)&0xff
            cpu.p|=0x04; cpu.pc=0xC0F0
        m.pc=(cpu.pc,m.bank); cpu.step()
    return m,cpu
