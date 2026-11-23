import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lr import Core
from PIL import Image
def sheet(paths,out,cols=6):
    ims=[Image.open(p) for p in paths]; w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(w*cols,h*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*w,(i//cols)*h))
    W.save(out)
def tap(c,k,n=6,after=20): c.run(n,k); c.run(after)
def to_title(c): c.run(640); tap(c,'START',6,150); return c
def to_options(c): to_title(c); tap(c,'DOWN',6,30); tap(c,'START',6,120); return c
def to_game(c): to_title(c); tap(c,'START',6,200); return c
def opt_row(c,row):
    for i in range(12):
        if c.ram()[0x91E]==row: return True
        tap(c,'DOWN',6,30)
    return False
def to_secret(c):
    to_options(c); opt_row(c,4); c.run(4,'L'); c.run(6,'L+START'); c.run(4,'L'); c.run(90); return c
