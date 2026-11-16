import sys, numpy as np
from gnav import N
from rec import grid
from PIL import Image
sec=int(sys.argv[1]); xoff=int(sys.argv[2])
n=N('gng.nes',sec=sec)
d0=bytearray(open('gng.nes','rb').read())
def off(a): return 16+4*0x4000+a-0x8000
# make every waiting hidden item visible with sprite id SPR
x=None
import csv
rows=[r for r in csv.DictReader(open('secrets.csv')) if int(r['section'])==sec]
RI=int(sys.argv[6]) if len(sys.argv)>6 else 0
x=int(rows[RI]['x'])
for _ in range(400):
    if abs((x-xoff)-n.wx())<3 or n.wx()==0: break
    n.walk_to(x-xoff,15)
s=n.save()
tiles=[]
SPRS=[int(v,16) for v in sys.argv[3].split(',')] if ',' in sys.argv[3] else list(range(int(sys.argv[3],16),int(sys.argv[4],16)))
for spr in SPRS:
    d=bytearray(d0); d[off(0xBB8D)]=spr; d[off(0xBB92):off(0xBB94)]=bytes([0x21,0xF3]); open('tsp.nes','wb').write(d)
    m=N('tsp.nes',state=s); m.run('',6)
    sx=x-(m.e.peek(0x64)+256*m.e.peek(0x65))
    sy=int(rows[RI]['y'])%256
    im=Image.fromarray(np.asarray(m.e.frame)).crop((max(0,sx-16),max(0,sy-24),max(0,sx-16)+32,max(0,sy-24)+32)).resize((64,64),Image.NEAREST)
    tiles.append((spr,im))
W=Image.new('RGB',(16*68,((len(tiles)+15)//16)*80),(40,40,40))
from PIL import ImageDraw
dr=ImageDraw.Draw(W)
for i,(spr,im) in enumerate(tiles):
    X=(i%16)*68; Y=(i//16)*80; W.paste(im,(X,Y)); dr.text((X+2,Y+66),'%02X'%spr,fill=(255,255,0))
W.save(sys.argv[5])
