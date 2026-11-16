import sys, numpy as np
from lr import Core
c=Core(sys.argv[1]); c.load(open('st_play.bin','rb').read())
xs=[];vis=[];P=[]
for f in range(1,700):
    c.run(1); r=c.ram(); xs.append((f,int(r[0xB200])*256+int(r[0xB201]))); vis.append((f,int(r[0xB20C])))
    if f in (240,270,330,450,520,560): c.shot(f'{sys.argv[2]}{f}.png',1); P.append(f'{sys.argv[2]}{f}.png')
ch=[xs[i] for i in range(1,len(xs)) if xs[i][1]!=xs[i-1][1]]
fl=[vis[i][0] for i in range(1,len(vis)) if vis[i][1]!=vis[i-1][1]]
print(sys.argv[1],'X changes',len(ch),ch[:3],'flicker',fl[:1],fl[-1:])
