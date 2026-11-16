#!/usr/bin/env python3
"""Fair Knight (NES) builder: assembles src/*.s with ca65/ld65 and patches the clean ROM.
usage: build.py CLEAN.nes OUT.nes [--save]"""
import sys, os, subprocess, hashlib, tempfile
CLEAN_MD5='80dcd911aaa221fd3de883d5128eb97c'
HERE=os.path.dirname(os.path.abspath(__file__))
# name, bank, cpu start, size, kind ('code' = overwrite original code, region sha1 asserted; 'free' = must be all $FF)
REGIONS=[
 ('HITHOP', 7, 0xE229, 0x5D, 'code', '278dd6be'),
 ('MERCY',  7, 0xE3B9, 0x23, 'code', '034bbb93'),
 ('FAR',    7, 0xFFE8, 13,   'free', None),
 ('FARTAIL',7, 0xDA6A, 7,    'free', None),
 ('BANK2',  2, 0x89D1, 0xD00,'free', None),
 ('BANK2B', 2, 0xBB67, 0x300,'free', None),   # end-of-bank padding $BB67-$BFFF (v0.5)
 ('WPICK',  4, 0xBA63, 20,   'code', '89e7f2b3'),
 ('TITLE',  7, 0xC4A5, 41,   'code', 'd9d9f3f2'),
 ('STARTGO',7, 0xC458, 3,    'code', 'a6b423cc'),
 ('TCUR',   7, 0xC43B, 16,   'code', '1e43e1d6'),
 ('LADDER', 7, 0xDD90, 9,    'code', 'a5cd94db'),
 ('AIRRISE',7, 0xDE40, 8,    'code', '51c28dbb'),
 ('AIRPEAK',7, 0xDE86, 8,    'code', '51c28dbb'),
 ('AIRFALL',7, 0xDEC9, 8,    'code', '746bab81'),
 ('SECCALL',7, 0xD3AD, 3,    'code', '1821e67a'),
 ('SECSTUB',7, 0xE562, 7,    'free', None),
 ('FARSEC', 7, 0xFFF5, 5,    'free', None),
 ('SPARKSITE',4,0xBB8C, 8,   'code', '95be628f'),
 ('FOUNDSITE',4,0xBBB9, 17,  'code', 'e38b8fc9'),
 ('READYSITE',7,0xC9E2, 14,  'code', '1d70671e'),
 ('GEN0',     2,0x8400, 3,   'code', '9bf34b49'),
 ('GENEND',   2,0x8412, 3,   'code', '07c89a1f'),
 ('HITCHK',   7,0xE014, 9,   'code', 'e632d2b4'),
]
SOURCES=['hit_hop.s','mercy.s','far.s','bank2.s','wpick_site.s','title_site.s','tcur_site.s','start_site.s','ladder_site.s','air_site.s','sec_site.s','secret_sites.s','ready_site.s','fairspawn.s','fs_sites.s']
def off(bank,addr): return 16+bank*0x4000+(addr-(0xC000 if bank==7 else 0x8000))
def main():
    clean,out=sys.argv[1],sys.argv[2]; save='--save' in sys.argv
    rom=bytearray(open(clean,'rb').read())
    assert hashlib.md5(rom).hexdigest()==CLEAN_MD5,'not the clean USA ROM'
    tmp=tempfile.mkdtemp()
    cfg=['MEMORY {']+[f'  M_{n}: start=${a:04X}, size=${s:X}, file="{tmp}/{n}.bin", fill=yes, fillval=$FF;' for n,b,a,s,k,h in REGIONS]+['}','SEGMENTS {']+[f'  {n}: load=M_{n}, type=ro;' for n,b,a,s,k,h in REGIONS]+['}']
    open(f'{tmp}/fk.cfg','w').write('\n'.join(cfg))
    objs=[]
    for s in SOURCES:
        o=f'{tmp}/{s}.o'; subprocess.check_call(['ca65','-I',HERE]+(['-D','SAVE_ENABLED=1'] if save else ['-D','SAVE_ENABLED=0'])+[os.path.join(HERE,s),'-o',o,'-l',f'{tmp}/{s}.lst']); objs.append(o)
    subprocess.check_call(['ld65','-C',f'{tmp}/fk.cfg','-o',f'{tmp}/unused.bin','-m',os.path.join(HERE,'fk.map')]+objs)
    for n,b,a,s,k,h in REGIONS:
        o=off(b,a); orig=bytes(rom[o:o+s])
        if k=='free': assert orig==b'\xff'*s,(n,'not free')
        if h: assert hashlib.sha1(orig).hexdigest()[:8]==h,(n,'original bytes differ',hashlib.sha1(orig).hexdigest()[:8])
        new=open(f'{tmp}/{n}.bin','rb').read(); assert len(new)==s
        rom[o:o+s]=new
    if save:
        rom[7]=(rom[7]&0xF0)|0x08; rom[6]|=0x02; rom[10]=0x70   # NES 2.0, battery, 8 KiB PRG-NVRAM
    open(out,'wb').write(rom); print(out, hashlib.md5(rom).hexdigest())
main()
