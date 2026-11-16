# Prototype patch v0: no knockback + longer invincibility (hard-coded on)
import sys, hashlib
src='gng.nes'; out=sys.argv[1] if len(sys.argv)>1 else 'fk_proto.nes'
d=bytearray(open(src,'rb').read())
assert hashlib.md5(d).hexdigest()=='80dcd911aaa221fd3de883d5128eb97c'
B7=16+7*0x4000
def cpu(a): return B7+a-0xC000
def patch(addr, old, new):
    o=cpu(addr); ob,nb=bytes.fromhex(old),bytes.fromhex(new); assert d[o:o+len(ob)]==ob,(hex(addr),d[o:o+len(ob)].hex()); d[o:o+len(nb)]=nb
# 1. No knockback: skip horizontal moves inside Arthur's hit routine (LE1EE..LE27D)
patch(0xE22E,'2082DB','EAEAEA')
patch(0xE252,'2082DB','EAEAEA')
patch(0xE27A,'2086E2','EAEAEA')
# 2. Mercy invincibility: 30 -> 60 Arthur ticks
patch(0xE3C4,'C91E','C93C')
open(out,'wb').write(d); print('wrote',out)
