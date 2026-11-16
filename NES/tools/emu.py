import cynes, numpy as np
from cynes import NES
from PIL import Image
B=dict(A=cynes.NES_INPUT_A,B=cynes.NES_INPUT_B,SEL=cynes.NES_INPUT_SELECT,ST=cynes.NES_INPUT_START,
       U=cynes.NES_INPUT_UP,D=cynes.NES_INPUT_DOWN,L=cynes.NES_INPUT_LEFT,R=cynes.NES_INPUT_RIGHT)
class Emu:
    def __init__(s,rom='gng.nes'):
        s.n=NES(rom); s.frame=None
    def run(s,frames=1,btn=''):
        v=0
        for k in btn.split('+'):
            if k: v|=B[k]
        s.n.controller=v
        for _ in range(frames): s.frame=s.n.step()
        s.n.controller=0
        return s
    def ram(s): return np.array([s.n[i] for i in range(0x800)],dtype=np.uint8)
    def peek(s,a): return s.n[a]
    def poke(s,a,v): s.n[a]=v
    def shot(s,path): Image.fromarray(np.asarray(s.frame)).resize((512,480),Image.NEAREST).save(path)
