"""Musashi (machine68k) replay of Ghouls'n Ghosts from a GPGX 1.7.6 savestate, with:
- RAM write logging (frame, pc, addr, width, value)
- a VDP write model (registers, VRAM/CRAM/VSRAM writes incl. 68k->VRAM DMA and fills) with PC logging
- a 3-button pad with the TH protocol (buttons: 'UP DOWN LEFT RIGHT A B C START')
Used for reverse engineering only; graphics are not rendered (use lr.py/GPGX for screenshots)."""
import machine68k as m, struct, numpy as np
REGOFF=144404     # D0-D7,A0-A7,PC,SR (LE u32) in the GPGX 1.7.6 state
RAMOFF=16         # work RAM, 16-bit words stored little-endian
BTN={'UP':0x01,'DOWN':0x02,'LEFT':0x04,'RIGHT':0x08,'B':0x10,'C':0x20,'A':0x40,'START':0x80}

class VDP:
    def __init__(s,mem):
        s.mem=mem; s.reg=[0]*32; s.pend=None; s.code=0; s.addr=0
        s.vram=bytearray(0x10000); s.log=[]; s.pc=0; s.frame=0
    def ctrl(s,v):
        if s.pend is None:
            if (v&0xC000)==0x8000:
                s.reg[(v>>8)&0x1F]=v&0xFF; return
            s.pend=v; return
        w1,w2=s.pend,v; s.pend=None
        s.code=((w1>>14)&3)|((w2>>2)&0x3C); s.addr=(w1&0x3FFF)|((w2&3)<<14)
        if (s.code&0x20) and (s.reg[1]&0x10):
            mode=s.reg[23]>>6
            ln=(s.reg[19]|s.reg[20]<<8) or 0x10000
            if mode<2:   # 68k -> VDP
                src=((s.reg[21]|s.reg[22]<<8|(s.reg[23]&0x7F)<<16)<<1)&0xFFFFFF
                for i in range(ln):
                    w=s.mem.r16(src+2*i); s.write(w,dma=True)
            elif mode==2:
                s.fill=True
    def data(s,v):
        if getattr(s,'fill',False):
            s.fill=False; ln=(s.reg[19]|s.reg[20]<<8) or 0x10000
            for i in range(ln):
                if (s.code&0xF)==1: s.vram[s.addr&0xFFFF]=v>>8
                s.log.append((s.frame,s.pc,'fill',s.code&0xF,s.addr,v>>8)); s.addr=(s.addr+s.reg[15])&0xFFFF
            return
        s.write(v)
    def write(s,v,dma=False):
        t=s.code&0xF
        if t==1:
            a=s.addr&0xFFFE; s.vram[a]=v>>8; s.vram[a+1]=v&0xFF
        s.log.append((s.frame,s.pc,'dma' if dma else 'w',t,s.addr&0xFFFF,v))
        s.addr=(s.addr+s.reg[15])&0xFFFF

class Box:
    pass
def make(state, rom):
    mach=m.Machine(m.CPUType.M68000,16384); mc=Box(); mc.m=mach; mc.mem=mach.mem; mc.cpu=mach.cpu; mem=mc.mem; cpu=mc.cpu
    mem.w_block(0, rom)
    ram=np.frombuffer(state[RAMOFF:RAMOFF+0x10000],dtype=np.uint8).reshape(-1,2)[:,::-1].reshape(-1).tobytes()
    mem.w_block(0xFF0000, ram)
    regs=struct.unpack('<18I',state[REGOFF:REGOFF+72])
    for i in range(8): cpu.w_reg(getattr(m.Register,f'D{i}'),regs[i])
    for i in range(7): cpu.w_reg(getattr(m.Register,f'A{i}'),regs[8+i])
    cpu.w_sr(regs[17]); cpu.w_reg(m.Register.A7,regs[15]); cpu.w_pc(regs[16])
    vdp=VDP(mem); io={'th':0x40,'pad':0,'vb':0}
    def r16(a):
        a&=0xFFFFFF
        if a in (0xC00004,0xC00006): io['vb']^=8; return 0x3400|io['vb']
        if a==0xA11100: return 0
        if a in (0xA10002,0xA10004): return r8(a+1)
        return 0
    def r8(a):
        a&=0xFFFFFF
        if a==0xA10003:
            p=io['pad']
            if io['th']: return 0x40|(~(p&0x3F)&0x3F)
            return (~((p>>6&1)<<4|(p>>7&1)<<5|(p&3))&0x33)
        if a==0xA10005: return 0x7F
        if a in (0xC00004,0xC00005): io['vb']^=8; return 0x34|io['vb']
        return 0
    def w8(a,v):
        a&=0xFFFFFF
        if a==0xA10003: io['th']=v&0x40
    def w16(a,v):
        a&=0xFFFFFF
        if a in (0xC00004,0xC00006): vdp.ctrl(v)
        elif a in (0xC00000,0xC00002): vdp.data(v)
        elif a==0xA10002: w8(0xA10003,v&0xFF)
    def w32(a,v): w16(a,v>>16); w16(a+2,v&0xFFFF)
    for page in (0xA0,0xA1,0xC0):
        mem.set_special_range_read_funcs(page<<16,1,r8,r16,lambda a:(r16(a)<<16)|r16(a+2))
        mem.set_special_range_write_funcs(page<<16,1,w8,w16,w32)
    mc.vdp=vdp; mc.io=io
    return mc

def irq(mc,level=6):
    cpu=mc.cpu; mem=mc.mem
    sr=cpu.r_sr()
    if ((sr>>8)&7)>=level: return False
    sp=cpu.r_reg(m.Register.A7)-6
    mem.w16(sp,sr); mem.w32(sp+2,cpu.r_pc())
    cpu.w_reg(m.Register.A7,sp); cpu.w_sr((sr&0xF8FF)|0x2000|(level<<8)); cpu.w_pc(mem.r32(0x60+level*4)); return True

def run(mc,frames,pads=None,watch=None,cyc=127840,hook_pc=True):
    """pads: function(frame)->button string. Returns RAM write log."""
    log=[]; cur={'pc':0}; cpu=mc.cpu; mem=mc.mem; fr={'f':0}
    if hook_pc:
        def ih(*a):
            cur['pc']=cpu.r_pc(); mc.vdp.pc=cur['pc']
        cpu.set_instr_hook_callback(ih)
    if watch:
        def tf(mode,w,addr,val):
            addr&=0xFFFFFF
            if mode=='W' and addr>=0xFF0000 and any(lo<=addr<hi for lo,hi in watch):
                log.append((fr['f'],cur['pc'],addr,w,val))
        mem.set_trace_mode(1); mem.set_trace_func(tf)
    for f in range(frames):
        fr['f']=f; mc.vdp.frame=f
        b=0
        if pads:
            for k in pads(f).split('+'):
                if k: b|=BTN[k]
        mc.io['pad']=b
        irq(mc,6); cpu.execute(cyc)
    return log
def ram(mc): return np.frombuffer(mc.mem.r_block(0xFF0000,0x10000),dtype=np.uint8)
