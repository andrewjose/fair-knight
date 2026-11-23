import numpy as np, sys
from lr import Core
rom=sys.argv[1] if len(sys.argv)>1 else 'gng.md'
c=Core(rom)
ever=np.zeros(0x10000,bool); first=None; frames=0
def step(n,b=''):
    global first,ever,frames
    for _ in range(n):
        c.run(1,b); r=c.ram(); frames+=1
        if first is None: first=r.copy()
        ever|=(r!=first)
step(700); step(2,'START'); step(30)
for k in range(2): step(2,'DOWN'); step(10)
step(2,'START'); step(60); step(2,'RIGHT'); step(20); step(2,'DOWN'); step(10); step(2,'RIGHT'); step(10); step(2,'START'); step(80)
for k in range(2): step(2,'UP'); step(10)
step(2,'START')
import random; random.seed(1)
keys=['','RIGHT','LEFT','A','B','RIGHT+A','RIGHT+B']
for f in range(9000):
    if f%30==0: k=random.choice(keys)
    step(1,k)
    if f%400==0: step(2,'START'); step(2)
print('frames',frames,'never-changed bytes',int((~ever).sum()))
np.save('/tmp/ever.npy',ever); np.save('/tmp/first.npy',first)
r=c.ram(); print('final state sample', r[0xF77C], c.ram()[0xB200:0xB204])
