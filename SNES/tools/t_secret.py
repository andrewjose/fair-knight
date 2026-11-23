"""The base's secret menu (L+START on EXIT) still opens and shows the KNIGHT defaults. usage: t_secret.py ROM out.png"""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nav import *
c=Core(sys.argv[1]); to_secret(c); c.shot(sys.argv[2],1)
