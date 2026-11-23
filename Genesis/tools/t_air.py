"""AIR CONTROL checks from st_play.bin (stage 1 start). usage: t_air.py FK_ROM [grid.png]
Scenarios run with FK_SET=$00 (FULL) and $08 (OFF) and on the clean ROM."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core; from util import grid
G=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ST=open(os.path.join(G,'st_play.bin'),'rb').read()
def run(rom, fk, script, n):
    c=Core(rom); c.load(ST); xs=[]; ys=[]
    for f in range(n):
        if fk is not None: c.poke(0xFF5A00,fk)
        c.run(1,script(f)); r=c.ram()
        xs.append(int(r[0xB200])*256+int(r[0xB201])); ys.append(int(r[0xB204])*256+int(r[0xB205]))
    return xs,ys,c
S={
 'jump right, hold right': lambda f: 'RIGHT+A' if f<3 else 'RIGHT',
 'jump right, reverse at +10': lambda f: 'RIGHT+A' if f<3 else ('RIGHT' if f<10 else 'LEFT'),
 'neutral jump, steer right': lambda f: 'A' if f<3 else ('' if f<6 else 'RIGHT'),
 'jump right, let go': lambda f: 'RIGHT+A' if f<3 else '',
}
for name,sc in S.items():
    out=[]
    for tag,rom,fk in (('clean',os.path.join(G,'gng.md'),None),('OFF',sys.argv[1],0x08),('FULL',sys.argv[1],0x00)):
        xs,ys,_=run(rom,fk,sc,60)
        land=next((i for i in range(5,60) if ys[i]==ys[0]),None)
        out.append(f'{tag}: dx@10={xs[10]-xs[0]:+d} dx@land={(xs[land]-xs[0]) if land else None} land@{land} peakY={max(ys)-ys[0]}')
    print(f'{name:28s} | '+' | '.join(out))
# hit recoil while holding LEFT (towards the hop) with FULL: must equal the plain knockback
for fk in (0x01,0x09):
    xs,ys,_=run(sys.argv[1],fk,lambda f:'LEFT' if f>=228 else '',300)
    print(f'hit hop holding LEFT, FK_SET={fk:02X}: X {xs[226]} -> {xs[280]} ({xs[280]-xs[226]:+d})')
