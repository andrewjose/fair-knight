from gemu import *
ST=open('st_after.bin','rb').read()
def fresh(rom='gng.gbc'):
    g=G(rom); g.load(ST); g.run(1); return g
def mem(g): return np.concatenate([g.wram(), g.hram()])
def addr(i): return 0xC000+i if i<0x2000 else 0xFF80+i-0x2000
def record(g,n,fn=lambda f:''):
    return np.array([mem(g.run(1,fn(f))) for f in range(n)])
