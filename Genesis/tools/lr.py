"""Minimal headless libretro frontend (ctypes) for genesis_plus_gx."""
import ctypes as C, numpy as np, os
CORE='/usr/lib/x86_64-linux-gnu/libretro/genesis_plus_gx_libretro.so'
class GameInfo(C.Structure): _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class Geom(C.Structure): _fields_=[('bw',C.c_uint),('bh',C.c_uint),('mw',C.c_uint),('mh',C.c_uint),('ar',C.c_float)]
class Timing(C.Structure): _fields_=[('fps',C.c_double),('sr',C.c_double)]
class AV(C.Structure): _fields_=[('geometry',Geom),('timing',Timing)]
ENV=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
VID=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
AUD=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
AUDB=C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
POLL=C.CFUNCTYPE(None)
STATE=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
# joypad ids: B=0 Y=1 SELECT=2 START=3 UP=4 DOWN=5 LEFT=6 RIGHT=7 A=8 X=9 L=10 R=11  (GPGX: B->A? see map below)
KEYS={'B':0,'Y':1,'MODE':2,'START':3,'UP':4,'DOWN':5,'LEFT':6,'RIGHT':7,'A':8,'X':9,'L':10,'R':11}
SYSDIR=C.create_string_buffer(b'/tmp/lrsys'); os.makedirs('/tmp/lrsys',exist_ok=True)
class Core:
    def __init__(s,rom):
        s.l=C.CDLL(CORE); s.keys=0; s.frame=None; s.fmt=1
        def env(cmd,data):
            if cmd==9 or cmd==31:   # GET_SYSTEM_DIRECTORY / GET_SAVE_DIRECTORY
                C.cast(data,C.POINTER(C.c_char_p))[0]=C.cast(SYSDIR,C.c_char_p).value; return True
            if cmd==10: s.fmt=C.cast(data,C.POINTER(C.c_int))[0]; return True   # SET_PIXEL_FORMAT
            if cmd==3: C.cast(data,C.POINTER(C.c_bool))[0]=False; return True      # GET_CAN_DUPE
            return False
        def vid(data,w,h,pitch):
            if not data: return
            if s.fmt==1:  # XRGB8888
                a=np.ctypeslib.as_array(C.cast(data,C.POINTER(C.c_uint32)),shape=(h,pitch//4))[:,:w].copy()
                s.frame=np.stack([(a>>16)&255,(a>>8)&255,a&255],-1).astype(np.uint8)
            else:         # RGB565
                a=np.ctypeslib.as_array(C.cast(data,C.POINTER(C.c_uint16)),shape=(h,pitch//2))[:,:w].astype(np.uint32).copy()
                s.frame=np.stack([((a>>11)&31)*255//31,((a>>5)&63)*255//63,(a&31)*255//31],-1).astype(np.uint8)
        def st(port,dev,idx,id_): return 1 if (port==0 and dev==1 and (s.keys>>id_)&1) else 0
        s._cb=[ENV(env),VID(vid),AUD(lambda l,r:None),AUDB(lambda d,n:n),POLL(lambda:None),STATE(st)]
        s.l.retro_set_environment(s._cb[0]); s.l.retro_set_video_refresh(s._cb[1]); s.l.retro_set_audio_sample(s._cb[2])
        s.l.retro_set_audio_sample_batch(s._cb[3]); s.l.retro_set_input_poll(s._cb[4]); s.l.retro_set_input_state(s._cb[5])
        s.l.retro_init()
        s.rom=open(rom,'rb').read(); s.buf=C.create_string_buffer(s.rom,len(s.rom))
        gi=GameInfo(rom.encode(),C.cast(s.buf,C.c_void_p),len(s.rom),None)
        assert s.l.retro_load_game(C.byref(gi))
        s.l.retro_get_memory_data.restype=C.c_void_p; s.l.retro_get_memory_size.restype=C.c_size_t
        s.l.retro_serialize_size.restype=C.c_size_t
    def run(s,n=1,btn=''):
        s.keys=0
        for k in btn.split('+'):
            if k: s.keys|=1<<KEYS[k]
        for _ in range(n): s.l.retro_run()
        s.keys=0; return s
    def ram(s):   # 68k work RAM $FF0000-$FFFFFF, returned in 68k (big-endian) byte order
        p=s.l.retro_get_memory_data(2); n=s.l.retro_get_memory_size(2)
        a=np.ctypeslib.as_array(C.cast(p,C.POINTER(C.c_uint8)),shape=(n,)).copy()
        return a.reshape(-1,2)[:,::-1].reshape(-1) if s.swap else a
    swap=True
    def poke(s,addr,v):
        p=s.l.retro_get_memory_data(2); o=(addr&0xFFFF)^(1 if s.swap else 0)
        C.cast(p,C.POINTER(C.c_uint8))[o]=v
    def save(s):
        n=s.l.retro_serialize_size(); b=C.create_string_buffer(n); assert s.l.retro_serialize(b,n); return b.raw
    def load(s,raw):
        b=C.create_string_buffer(raw,len(raw)); assert s.l.retro_unserialize(b,len(raw))
    def shot(s,path,scale=2):
        from PIL import Image
        Image.fromarray(s.frame).resize((s.frame.shape[1]*scale,s.frame.shape[0]*scale),Image.NEAREST).save(path)
