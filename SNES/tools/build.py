#!/usr/bin/env python3
"""Build Fair Knight SNES.  usage: build.py BASE.sfc OUT.sfc [--classic]
Assembles src/fk.s with ca65/ld65 (one memory area per patch site), checks every site's
original bytes in the base ROM, checks the FK bank is blank, writes the ROM and fixes the
internal header checksum."""
import sys, os, subprocess, hashlib
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); SRC=os.path.join(ROOT,'src')
BASE_MD5='3ca29fc2defbf638aeb0ea38036b7215'
# name: (SNES address, original bytes)
SITES={
 'S_KB':     (0x01D7ED,'22488801'),     # JSL $018848  (hit: load hop velocity)
 'S_CONT':   (0x0496CC,'e901'),         # SBC #$01     (continue counter)
 'S_BOOT':   (0x03EA29,'22c5f20c'),     # JSL $0CF2C5  (boot, after settings load)
 'S_OPTDRAW':(0x03B92E,'22569704'),     # JSL $049756  (OPTION MODE labels)
 'S_CLS':    (0x0CF291,'2046f28f90af7e'), # JSR $F246 / STA $7EAF90 (board type)
 'S_OPTIN':  (0x03B939,'adbb020dbc02'), # LDA $02BB / ORA $02BC
}
FK_BANK=0x38
def off(a): return ((a>>16)&0x7F)*0x8000+(a&0x7FFF)
def main():
    a=sys.argv[1:]; classic='--classic' in a; a=[x for x in a if not x.startswith('--')]
    base=open(a[0],'rb').read(); assert hashlib.md5(base).hexdigest()==BASE_MD5,'not Enhanced Arthur v1.2'
    rom=bytearray(base); od=os.path.join(ROOT,'out','obj'); os.makedirs(od,exist_ok=True)
    mem=[];seg=[]
    for n,(ad,orig) in SITES.items():
        mem.append(f'  M_{n}: start=${ad:06X}, size={len(orig)//2}, file="{od}/{n}.bin";')
        seg.append(f'  {n}: load=M_{n}, type=ro;')
    mem.append(f'  M_FK: start=$8000, size=$8000, file="{od}/FK.bin";'); seg.append('  FKCODE: load=M_FK, type=ro;')
    cfg='MEMORY {\n'+'\n'.join(mem)+'\n}\nSEGMENTS {\n'+'\n'.join(seg)+'\n}\n'
    open(os.path.join(od,'fk.cfg'),'w').write(cfg)
    defs=['-D','CLASSIC=1'] if classic else []
    subprocess.check_call(['ca65','--cpu','65816','-I',SRC,*defs,'-o',f'{od}/fk.o','-l',f'{od}/fk.lst',os.path.join(SRC,'fk.s')])
    subprocess.check_call(['ld65','-C',f'{od}/fk.cfg','-o',f'{od}/dummy.bin','-m',f'{od}/fk.map','-Ln',f'{od}/fk.lbl',f'{od}/fk.o'])
    for n,(ad,orig) in SITES.items():
        b=open(f'{od}/{n}.bin','rb').read(); o=off(ad); ob=bytes.fromhex(orig)
        assert rom[o:o+len(ob)]==ob,(n,rom[o:o+len(ob)].hex(),orig)
        assert len(b)==len(ob),(n,len(b))
        rom[o:o+len(b)]=b
    fk=open(f'{od}/FK.bin','rb').read(); o=off(FK_BANK<<16|0x8000)
    assert not any(rom[o:o+0x8000]),'FK bank not blank'
    rom[o:o+len(fk)]=fk
    # header checksum (LoROM header at $7FC0)
    rom[0x7FDC:0x7FE0]=b'\xff\xff\x00\x00'
    cs=sum(rom)&0xFFFF; rom[0x7FDE]=cs&0xFF; rom[0x7FDF]=cs>>8; rom[0x7FDC]=(cs^0xFFFF)&0xFF; rom[0x7FDD]=(cs^0xFFFF)>>8
    open(a[1],'wb').write(rom)
    print(a[1], hashlib.md5(rom).hexdigest(), 'FK code', len(fk), 'bytes', 'classic' if classic else '')
if __name__=='__main__': main()
