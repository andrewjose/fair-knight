# Set options through the real menu, start a 1-player game, check the gameplay effect.
from emu import Emu
from t_opt import to_options, tap
import numpy as np, sys
ROM='v03b.nes'
def play_from_menu(keys, tag):
    e=to_options(Emu(ROM))
    for k in keys: tap(e,k)
    s=(e.peek(0x7FA),e.peek(0x7FB))
    tap(e,'ST',4)
    for i in range(120):
        e.run(2)
        if e.peek(0x509)==0x92 and e.peek(0xA3)==0: break
    e.run(40); tap(e,'ST',4)            # 1 PLAYER
    # wait until Arthur is controllable: timer digit ticking and Arthur standing (Y=184)
    for i in range(3000):
        e.run(1)
        if e.peek(0x599)==184 and e.peek(0x6FC)!=0 and i>600: break
    e.run(30)
    np.save(f'st_{tag}.npy', e.n.save()); e.shot(f'pl_{tag}.png')
    return e,s
def hit_test(tag):
    e=Emu(ROM); e.n.load(np.load(f'st_{tag}.npy')); e.run(1)
    xs=[];c=[]
    for f in range(700):
        e.run(1); xs.append(e.peek(0x5AF)); c.append(e.peek(0x647))
    kb=sum(1 for i in range(1,len(xs)) if xs[i]!=xs[i-1])
    return kb, max(c)
for tag,keys in [('knight',[]),('custom',['D','R','D','D','R']),('original',['R','R']),('legend',['R'])]:
    e,s=play_from_menu(keys,tag)
    kb,mc=hit_test(tag)
    print(f'{tag:9s} FK_SET={s[0]:02X} pre={s[1]:02X}  X-changes over 700 idle frames={kb}  mercy counter max={mc}  inplay Y={e.peek(0x599)}')
