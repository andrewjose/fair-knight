# Navigate every row, change every value, Select reset, Start exit; checks RAM + screenshots.
from emu import Emu
from t_opt import to_options, tap
from rec import grid
import sys
ROM=sys.argv[1]
e=to_options(Emu(ROM)); P=[]
def st(tag):
    e.run(16); fn=f'm_{tag}.png'; e.shot(fn); P.append(fn)
    print(f'{tag:14s} cur={e.peek(0x7FE)} set={e.peek(0x7FA):02X} pre={e.peek(0x7FB):02X}')
st('start')
tap(e,'R'); st('preset_R')          # LEGEND
tap(e,'R'); st('preset_RR')         # ORIGINAL
tap(e,'R'); st('preset_RRR')        # back to KNIGHT
tap(e,'L'); st('preset_L')          # ORIGINAL
tap(e,'L'); tap(e,'L'); st('preset_LLL')   # KNIGHT
tap(e,'D'); tap(e,'R'); st('kb_toggle')    # knockback ON, CUSTOM
tap(e,'D'); tap(e,'L'); st('mercy_toggle') # mercy NORMAL
tap(e,'D'); tap(e,'R'); st('wdrop_toggle') # weapon drop OFF
tap(e,'SEL'); st('select_reset')           # back to KNIGHT
tap(e,'D'); tap(e,'R'); st('exit_LR_noop') # on EXIT, L/R does nothing
tap(e,'U'); tap(e,'U'); tap(e,'U'); tap(e,'U'); tap(e,'U'); st('wrap_up')   # wraps to EXIT
tap(e,'D'); st('wrap_down')                 # wraps to PRESET
tap(e,'R'); tap(e,'D'); tap(e,'R'); st('legend_custom')  # LEGEND then knockback flipped -> CUSTOM
tap(e,'SEL'); st('select_legend')           # reset to LEGEND
tap(e,'ST',4)
for i in range(60):
    e.run(2)
    if e.peek(0x509)==0x92: break
e.run(60); st('back_title')
grid(P,cols=4)
