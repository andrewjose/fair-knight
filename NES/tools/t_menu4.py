# v0.4 options screen: every row and value, presets, CUSTOM, Select reset, wrap, exit.
from emu import Emu
from t_opt import to_options, tap
from rec import grid
import sys
ROM=sys.argv[1]
e=to_options(Emu(ROM)); P=[]
log=[]
def st(tag, shot=False):
    e.run(16)
    if shot: fn=f'm4_{tag}.png'; e.shot(fn); P.append(fn)
    s=(e.peek(0x7FE),e.peek(0x7FA),e.peek(0x7FB)); log.append((tag,)+s)
    print(f'{tag:16s} cur={s[0]} set={s[1]:02X} pre={s[2]:02X}')
st('start',True)
tap(e,'R'); st('LEGEND',True)
tap(e,'R'); st('ORIGINAL')
tap(e,'R'); st('KNIGHT')
for row,name,n in [(1,'knockback',2),(2,'mercy',2),(3,'wdrop',2),(4,'ladder',2),(5,'air',3),(6,'endgame',2),(7,'secrets',3)]:
    tap(e,'D')
    for i in range(n):
        tap(e,'R'); st(f'{name}_R{i+1}', shot=(name in ('air','secrets') and i==0))
    tap(e,'L'); st(f'{name}_L')
    tap(e,'R'); st(f'{name}_back')     # back to the KNIGHT value
tap(e,'SEL'); st('select_reset',True)
tap(e,'D'); tap(e,'R'); st('exit_LR_noop')
tap(e,'D'); st('wrap_down')
tap(e,'U'); st('wrap_up')
tap(e,'ST',4)
for i in range(60):
    e.run(2)
    if e.peek(0x509)==0x92: break
e.run(60); st('back_title',True)
grid(P,cols=4,out='menu4.png')
