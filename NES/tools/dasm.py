import sys
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
rom=open('gng.nes','rb').read()[16:]
def dis(start,end,bank=7):
    class M:
        def __getitem__(s,a):
            if a>=0xC000: return rom[7*0x4000+a-0xC000]
            if a>=0x8000: return rom[bank*0x4000+a-0x8000]
            return 0
        def __len__(s): return 0x10000
    D=Disassembler(MPU(memory=M())); pc=start
    while pc<end:
        n,t=D.instruction_at(pc); print('%04X  %-9s %s'%(pc,' '.join('%02X'%M()[pc+i] for i in range(n)),t)); pc+=n
if __name__=='__main__':
    a=[int(x,16) for x in sys.argv[1:3]]; b=int(sys.argv[3]) if len(sys.argv)>3 else 7
    rom=open('gng.nes','rb').read()[16:]; dis(a[0],a[1],b)
