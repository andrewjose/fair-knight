# Find who sets a bit in a RAM byte: replay frames on py65, break when (old&mask)==0 and (new&mask)!=0.
import numpy as np, sys
from tr2 import *
from trace import Mem
from py65.devices.mpu6502 import MPU
def find_set(S, k, nframes, addr, mask, skip=0):
    s=[int(x) for x in S[k]]
    ram=bytes(s[25570:25570+0x800]); m=Mem(ram,ram[0xC8]&7)
    cpu=MPU(memory=m,pc=s[6]|s[7]<<8); cpu.sp=s[5]; cpu.a=s[1]; cpu.x=s[2]; cpu.y=s[3]
    target=cpu.processorCycles+29781*nframes; nmi_at=cpu.processorCycles+29781
    hist=[]; found=[]
    while cpu.processorCycles<target:
        if cpu.processorCycles>=nmi_at:
            nmi_at+=29781
            for v in (cpu.pc>>8,cpu.pc&0xff,cpu.p&~0x10): m[0x100+cpu.sp]=v; cpu.sp=(cpu.sp-1)&0xff
            cpu.p|=0x04; cpu.pc=0xC0F0
        old=m.ram[addr]; m.pc=(cpu.pc,m.bank); hist.append((cpu.pc,m.bank,cpu.x,cpu.y)); hist=hist[-80:]
        cpu.step()
        if not (old&mask) and (m.ram[addr]&mask):
            st=[m.ram[0x100+((cpu.sp+i)&0xff)] for i in range(1,16)]
            found.append((list(hist),st))
            if len(found)>skip: return found
    return found
