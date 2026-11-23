"""Navigation helpers (power-on based, so they work with any build)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lr import Core
def to_title_menu(c):
    c.run(700); c.run(2,'START'); c.run(30)
def to_options(c):
    to_title_menu(c)
    for k in range(2): c.run(2,'DOWN'); c.run(10)
    c.run(2,'START'); c.run(60)
def to_fk_page(c):
    to_options(c); c.run(3,'A'); c.run(20)          # RetroPad A = Genesis C
def to_stage1(c, settings=None):
    """1 PLAYER from the title; settings = FK_SET value poked before the game starts."""
    to_title_menu(c)
    if settings is not None: c.poke(0xFF5A00, settings)
    c.run(2,'START')
    c.run(300)
def tap(c,k,wait=12): c.run(3,k); c.run(wait)
