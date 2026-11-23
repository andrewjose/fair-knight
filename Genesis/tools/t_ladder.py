"""LADDER SAFETY (synthetic): from st_play.bin, at frame 222 put Arthur in the ladder top-out state
($334C = $8F36, counters 0) with Up held, so the top-out completes (hook $8F7C) just before the
enemy contact that hits an idle Arthur at frame 234. usage: t_ladder.py FK_ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core
G=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ST=open(os.path.join(G,'st_play.bin'),'rb').read()
def run(rom, set2):
    c=Core(rom); c.load(ST); log=[]
    for f in range(330):
        c.poke(0xFF5A00,0x01); c.poke(0xFF5A02,set2)      # knockback ON so a hit is easy to see
        if f==222:
            for i,b in enumerate((0,0,0x8F,0x36)): c.poke(0xFFB34C+i,b)
            c.poke(0xFFB20E,0); c.poke(0xFFB20F,0)
        c.run(1,'UP' if 222<=f<226 else ''); r=c.ram()
        log.append((int(r[0xB200])*256+int(r[0xB201]), int(r[0xB317]), int(r[0xB318])*256+int(r[0xB319]),
                    int.from_bytes(r[0xB338:0xB33C].tobytes(),'big'), int(r[0xB20C])))
    return log
for tag,s2 in (('ON',0x00),('OFF',0x01)):
    L=run(sys.argv[1],s2)
    inv=[f for f,l in enumerate(L) if l[1]]
    fl=[f for f in range(1,len(L)) if L[f][4]!=L[f-1][4]]
    print(f'LADDER {tag}: invincible frames {inv[0] if inv else None}-{inv[-1] if inv else None} ({len(inv)}), '
          f'X 220->{L[300][0]} (start {L[220][0]}), blink frames {len(fl)}, wrapper@226={L[226][3]:X} @300={L[300][3]:X}')
