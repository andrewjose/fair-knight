"""Replays Ghouls'n Ghosts frames on Musashi (machine68k) from a GPGX savestate and logs RAM writes with PC."""
import machine68k as m, struct, numpy as np
ROM=open('gng.md','rb').read()
REGOFF=144404     # D0-D7,A0-A7,PC,SR as little-endian u32 in GPGX 1.7.6 state (found via A5=$FF8000)
def make(state, ram, rom=ROM):
    mc=m.Machine(m.CPUType.M68000,16384); mem=mc.mem; cpu=mc.cpu
    mem.w_block(0, rom); mem.w_block(0xFF0000, bytes(ram))
    regs=struct.unpack('<18I',state[REGOFF:REGOFF+72])
    for i in range(8): cpu.w_reg(getattr(m.Register,f'D{i}'),regs[i])
    for i in range(7): cpu.w_reg(getattr(m.Register,f'A{i}'),regs[8+i])
    cpu.w_sr(regs[17]); cpu.w_reg(m.Register.A7,regs[15]); cpu.w_pc(regs[16])
    st={'vb':0}
    def r16(a):
        a&=0xFFFFFF
        if a in (0xC00004,0xC00006): st['vb']^=8; return 0x3400|st['vb']
        if a==0xA11100: return 0
        return 0
    def r8(a):
        a&=0xFFFFFF
        if a in (0xA10003,0xA10005): return 0x7F
        if a in (0xC00004,0xC00005): st['vb']^=8; return 0x34|st['vb']
        return 0
    for page in (0xA0,0xA1,0xC0):
        mem.set_special_range_read_funcs(page<<16,1,r8,r16,lambda a:(r16(a)<<16)|r16(a+2))
        mem.set_special_range_write_funcs(page<<16,1,lambda a,v:None,lambda a,v:None,lambda a,v:None)
    return mc
def irq(mc,level=6):
    cpu=mc.cpu; mem=mc.mem
    sr=cpu.r_sr()
    if ((sr>>8)&7)>=level: return False
    sp=cpu.r_reg(m.Register.A7)-6
    mem.w16(sp,sr); mem.w32(sp+2,cpu.r_pc())
    cpu.w_reg(m.Register.A7,sp); cpu.w_sr((sr&0xF8FF)|0x2000|(level<<8)); cpu.w_pc(mem.r32(0x60+level*4)); return True
def run(mc,frames,watch=None,cyc=127840,trace_all=False):
    log=[]; cur={'pc':0}
    cpu=mc.cpu; mem=mc.mem
    def ih(*a): cur["pc"]=cpu.r_pc()
    if watch is not None or trace_all:
        cpu.set_instr_hook_callback(ih)
        def tf(mode,w,addr,val):
            addr&=0xFFFFFF
            if mode=='W' and addr>=0xFF0000 and (trace_all or any(lo<=addr<hi for lo,hi in watch)):
                log.append((fr['f'],cur['pc'],addr,w,val))
        mem.set_trace_mode(1); mem.set_trace_func(tf)
    fr={'f':0}
    for f in range(frames):
        fr['f']=f; irq(mc,6); cpu.execute(cyc)
    return log
def ram(mc): return np.frombuffer(mc.mem.r_block(0xFF0000,0x10000),dtype=np.uint8)
