# Fair Knight GBC prototype 0: no knockback + longer mercy invincibility (hard-coded on)
import sys, hashlib
src=sys.argv[1] if len(sys.argv)>1 else 'gng.gbc'; out=sys.argv[2] if len(sys.argv)>2 else 'fk_gbc_proto0.gbc'
d=bytearray(open(src,'rb').read())
assert hashlib.md5(d).hexdigest()=='9b846e9a4eb6b80cdbc8e6c82f2b9e9e', 'not the clean USA/Europe ROM'
def patch(off, old, new):
    ob,nb=bytes.fromhex(old),bytes.fromhex(new); assert d[off:off+len(ob)]==ob,(hex(off),d[off:off+len(ob)].hex()); d[off:off+len(nb)]=nb
# knockback: hit state (5) horizontal move call -> NOPs; knockback velocity on hit -> 0 (armor-loss and death paths)
patch(0x35CD,'cd2537','000000')
patch(0x3387,'3ef0','3e00')
patch(0x33A6,'3ef0','3e00')
# mercy invincibility after armor loss: 120 -> 240 frames
patch(0x3375,'3e78','3ef0')
# fix global checksum (0x14E-0x14F, big-endian sum of all other bytes)
s=(sum(d)-d[0x14E]-d[0x14F])&0xFFFF; d[0x14E]=s>>8; d[0x14F]=s&0xFF
open(out,'wb').write(d); print(out, hashlib.md5(d).hexdigest())
