"""Settings survive a power cycle: change some on the page, copy SRAM into a fresh boot. usage: t_persist.py ROM"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); to_options(c); c.run(20)
tap(c,'X',6,40); tap(c,'DOWN',6,30); tap(c,'RIGHT',6,30)      # knockback ON
for i in range(4): tap(c,'DOWN',6,30)
tap(c,'RIGHT',6,30); tap(c,'START',6,60)                       # weapon DROP
s=c.sram().copy(); print('before', bytes(c.ram()[0x1FF0:0x1FF7]).hex(), hex(s[0x1F02]))
d=Core(sys.argv[1])
for i,v in enumerate(s): d.poke_sram(i,int(v))
d.run(700); print('after reboot', bytes(d.ram()[0x1FF0:0x1FF7]).hex(), hex(d.sram()[0x1F02]))
