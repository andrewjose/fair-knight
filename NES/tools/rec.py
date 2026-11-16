from emu import Emu
import numpy as np
def boot():
    e=Emu(); e.run(120); e.run(5,'ST'); e.run(1075); return e
def record(e,frames,btnfn=lambda f:''):
    R=[]
    for f in range(frames):
        e.run(1,btnfn(f)); R.append(e.ram())
    return np.array(R)
def fresh(st='st_play.npy'):
    e=Emu(); e.n.load(np.load(st)); e.run(1); return e
def grid(paths,out='grid.png',cols=4):
    from PIL import Image
    ims=[Image.open(p).resize((256,240)) for p in paths]
    rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(256*cols,240*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*256,(i//cols)*240))
    W.save(out)
