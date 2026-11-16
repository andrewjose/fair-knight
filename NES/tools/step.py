import sys
from gnav import *
src,dst,cands,yref=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')],None
for tx in cands:
    m=N(state=np.load(src)); m.run('R',3); y0=m.y(); m.walk_to(tx,3000); y=m.climb(); print(tx,m.st())
    if y<y0: np.save(dst,m.save()); break
P=[]
for tx in [int(x) for x in sys.argv[4].split(',')]:
    k=N(state=np.load(dst)); k.run('R',3); k.walk_to(tx,3000); print(tx,k.st()); P.append(k.shot(f'v{tx}'))
grid(P,'g.png',len(P))
