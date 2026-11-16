import warnings; warnings.filterwarnings('ignore')
from pyboy import PyBoy
import numpy as np, io
class G:
    def __init__(s,rom='gng.gbc'):
        s.p=PyBoy(rom,window='null',sound_emulated=False); s.p.set_emulation_speed(0)
    def run(s,n=1,btn=''):
        ks=[k for k in btn.split('+') if k]
        for k in ks: s.p.button_press(k)
        for _ in range(n): s.p.tick(1,False)
        for k in ks: s.p.button_release(k)
        s.p.tick(1,True)
        return s
    def wram(s): return np.array(s.p.memory[0xC000:0xE000],dtype=np.uint8)
    def hram(s): return np.array(s.p.memory[0xFF80:0xFFFF],dtype=np.uint8)
    def peek(s,a): return s.p.memory[a]
    def poke(s,a,v): s.p.memory[a]=v
    def shot(s,path): s.p.screen.image.convert('RGB').resize((320,288)).save(path)
    def save(s):
        f=io.BytesIO(); s.p.save_state(f); return f.getvalue()
    def load(s,b): s.p.load_state(io.BytesIO(b))
def grid(paths,out='grid.png',cols=4):
    from PIL import Image
    ims=[Image.open(p).resize((240,216)) for p in paths]; rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(240*cols,216*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*240,(i//cols)*216))
    W.save(out)
