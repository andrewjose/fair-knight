#!/usr/bin/env python3
"""Fair Knight (Genesis) build: assembles src/*.s with GNU as (m68k), places each patch site at its address
with a generated linker script, checks every overwritten original block byte-for-byte, expands the ROM to
1 MiB, fixes the header ROM-end field and checksum. usage: build.py CLEAN_ROM OUT_ROM"""
import sys, os, subprocess, hashlib, struct, re, tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
CLEAN_MD5='c61ff4bcdf10813c74f36ab57e29f646'
FK_BASE=0x0A0000; ROM_SIZE=0x100000
# site section -> (address, original bytes that must be there, hex)
SITES={
 's8ba6': (0x8BA6, '41fa00b033580014'),
 's8cbc': (0x8CBC, '3b7c00783318'),
 's2408': (0x2408, '46fc230061000032'),
 's1b600': (0x1B600, '1029000b4ef900013566'),
 's1ab1c': (0x1AB1C, '7000286d32ce'),
 's8ac6': (0x8AC6, '0ca90001219a0024'),
 's8f7c': (0x8F7C, '2b7c00008596334c'),
 's8f20': (0x8F20, '2b7c00008596334c'),
}
def sh(*a): subprocess.run(a,check=True,cwd=HERE)
def main(src,out):
    d=bytearray(open(src,'rb').read())
    assert hashlib.md5(d).hexdigest()==CLEAN_MD5,'not the clean Ghouls n Ghosts (USA, Europe) ROM'
    tmp=tempfile.mkdtemp()
    objs=[]
    for f in sorted(x for x in os.listdir(HERE) if x.endswith('.s')):
        o=os.path.join(tmp,f[:-2]+'.o'); objs.append(o)
        sh('m68k-linux-gnu-as','-m68000','--register-prefix-optional','-I',HERE,'-o',o,f)
    ld=os.path.join(tmp,'fk.ld')
    with open(ld,'w') as L:
        L.write('SECTIONS {\n')
        for name,(addr,_) in SITES.items(): L.write(f'  .{name} 0x{addr:X} : {{ *(.{name}) }}\n')
        L.write(f'  .fk 0x{FK_BASE:X} : {{ *(.fk) }}\n  /DISCARD/ : {{ *(.note*) *(.comment) }}\n}}\n')
    elf=os.path.join(tmp,'fk.elf')
    subprocess.run(['m68k-linux-gnu-ld','-T',ld,'-o',elf]+objs,check=True)
    def section(name):
        b=os.path.join(tmp,name+'.bin')
        subprocess.run(['m68k-linux-gnu-objcopy','-O','binary','-j','.'+name,elf,b],check=True)
        return open(b,'rb').read()
    for name,(addr,orig) in SITES.items():
        ob=bytes.fromhex(orig); nb=section(name)
        assert d[addr:addr+len(ob)]==ob, (name,'original bytes differ',d[addr:addr+len(ob)].hex())
        assert len(nb)<=len(ob), (name,'patch longer than the original block',len(nb),len(ob))
        d[addr:addr+len(nb)]=nb
        for i in range(len(nb),len(ob)): raise SystemExit(f'{name}: patch shorter than block; pad with nops')
    fk=section('fk')
    d+=b'\xFF'*(ROM_SIZE-len(d))
    assert all(x==0xFF for x in d[FK_BASE:FK_BASE+len(fk)])
    d[FK_BASE:FK_BASE+len(fk)]=fk
    d[0x1A4:0x1A8]=struct.pack('>I',ROM_SIZE-1)
    s=sum(struct.unpack('>%dH'%((len(d)-0x200)//2),d[0x200:]))&0xFFFF
    d[0x18E:0x190]=struct.pack('>H',s)
    open(out,'wb').write(d)
    # symbol map for tests/docs
    nm=subprocess.run(['m68k-linux-gnu-nm',elf],capture_output=True,text=True).stdout
    open(os.path.splitext(out)[0]+'.sym','w').write(nm)
    print(out,hashlib.md5(d).hexdigest(),'fk code bytes',len(fk))
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
