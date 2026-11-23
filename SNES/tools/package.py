"""Package a Fair Knight SNES version. usage: package.py VERSION "main change" OUTDIR
Builds normal + Classic, writes ROM, IPS/BPS against Enhanced Arthur v1.2, BPS against the
clean USA ROM, MD5SUMS, and verifies every patch by applying it from scratch."""
import sys, os, subprocess, hashlib, zlib
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE); import mkpatch
V,change,OUT=sys.argv[1:4]
base=open(os.path.join(ROOT,'ea.sfc'),'rb').read(); clean=open(os.path.join(ROOT,'clean.sfc'),'rb').read()
md5=lambda b: hashlib.md5(b).hexdigest(); crc=lambda b: '%08X'%(zlib.crc32(b)&0xFFFFFFFF)
for ed in ['','Classic']:
    tag=f'v{V}'+(' Classic' if ed else '')
    d=os.path.join(OUT,f'Fair Knight SNES {tag} - {change}'); os.makedirs(d,exist_ok=True)
    rom_p=os.path.join(ROOT,'out',f'fk{V}{ed}.sfc')
    subprocess.check_call([sys.executable,os.path.join(HERE,'build.py'),os.path.join(ROOT,'ea.sfc'),rom_p]+(['--classic'] if ed else []),stdout=subprocess.DEVNULL)
    rom=open(rom_p,'rb').read()
    files={f'Super Ghouls n Ghosts (Fair Knight SNES {tag}).sfc':rom,
           f'Fair Knight SNES {tag} - patch Enhanced Arthur v1.2.ips':mkpatch.ips(base,rom),
           f'Fair Knight SNES {tag} - patch Enhanced Arthur v1.2.bps':mkpatch.bps(base,rom),
           f'Fair Knight SNES {tag} - patch clean USA ROM.bps':mkpatch.bps(clean,rom)}
    for n,b in files.items(): open(os.path.join(d,n),'wb').write(b)
    for n,b in files.items():
        if n.endswith('.ips'): assert mkpatch.apply_ips(base,b)==rom,n
        if n.endswith('.bps'): assert mkpatch.apply_bps(clean if 'clean' in n else base,b)==rom,n
    m=[f'{md5(b)}  {n}' for n,b in files.items()]
    m+=['',f"Base for the first two patches: Super Ghouls n Ghosts (Enhanced Arthur v1.2).sfc  MD5 {md5(base)}  CRC32 {crc(base)}",
        f"Base for the clean-ROM patch:   Super Ghouls'n Ghosts (USA).sfc  MD5 {md5(clean)}  CRC32 {crc(clean)} (headerless)",
        f"Result: MD5 {md5(rom)}  CRC32 {crc(rom)}"]
    open(os.path.join(d,'MD5SUMS.txt'),'w').write('\n'.join(m)+'\n')
    print(d); print('\n'.join(m))
