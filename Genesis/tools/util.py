from PIL import Image
def grid(paths,out='grid.png',cols=4,w=320,h=224):
    ims=[Image.open(p).resize((w,h)) for p in paths]; rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(w*cols,h*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*w,(i//cols)*h))
    W.save(out)
