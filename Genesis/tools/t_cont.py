"""Continues: from st_cont.bin (CONTINUE countdown on screen, clean ROM state), keep continuing and dying
(no input), count how many CONTINUE screens appear. usage: t_cont.py ROM N"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core
G=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c=Core(sys.argv[1]); c.load(open(os.path.join(G,'st_cont.bin'),'rb').read())
if len(sys.argv)>3: c.poke(0xFFFE95,int(sys.argv[3]))   # difficulty word $FE94: 1 practice, 0 professional
def is_cont():
    f=c.frame; band=f[40:70,60:260].reshape(-1,f.shape[-1]).astype(int); rest=f[150:220].astype(int)
    return (band.sum(1)>200).sum()>300 and rest.sum()< 50*255
n=0; t=0
while n<int(sys.argv[2]) and t<60000:
    c.run(5); t+=5
    if is_cont():
        n+=1; print('CONTINUE screen',n,'at frame',t); c.run(3,'START'); c.run(200); t+=203
print('done after',t,'frames;', n, 'continue screens')
