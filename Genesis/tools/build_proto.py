# Fair Knight Genesis prototype 0 (Ghouls 'n Ghosts): no knockback (+ mercy, once found)
import sys, hashlib, struct
src=sys.argv[1] if len(sys.argv)>1 else 'gng.md'; out=sys.argv[2] if len(sys.argv)>2 else 'fk_gen_proto0.md'
d=bytearray(open(src,'rb').read())
assert hashlib.md5(d).hexdigest()=='c61ff4bcdf10813c74f36ab57e29f646', 'unexpected base ROM'
def patch(off, old, new):
    ob,nb=bytes.fromhex(old),bytes.fromhex(new); assert d[off:off+len(ob)]==ob,(hex(off),d[off:off+len(ob)].hex()); d[off:off+len(nb)]=nb
# knockback: Arthur hit-hop X velocity table (routine at $3AD22) -> 0 in every branch
# hit hop velocity table at $8C58 (vx, vy, gravity, ax), loaded by the hit routine at $8B98; vx 2.0 -> 0
patch(0x8C58,'02000440ffc80000','00000440ffc80000')
# mercy invincibility after landing: move.w #120,$3318(a5) at $8CBC -> 240 frames
patch(0x8CBC,'3b7c00783318','3b7c00f03318')
for extra in sys.argv[3:]:
    off,old,new=extra.split(':'); patch(int(off,16),old,new)
# header checksum: sum of big-endian words from $200 to end
s=sum(struct.unpack('>%dH'%((len(d)-0x200)//2),d[0x200:]))&0xFFFF
d[0x18E:0x190]=struct.pack('>H',s)
open(out,'wb').write(d); print(out, hashlib.md5(d).hexdigest())
