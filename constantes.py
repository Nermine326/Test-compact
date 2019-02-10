
from os import popen, name
from sys import path
from pygame.locals import *
from math import pi, cos, sin, atan
from enumerations import *
try:
	from ctypes import windll
except ImportError:
	print "Importation non possible de windll."

def getSystemResolutionOnLin():
	screen = popen("xrandr -q -d :0").readlines()[0]
	tmp = screen.split()
	return int( tmp[7] ), int( tmp[9][:-1] )

def getSystemResolutionOnWin():
        return windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)

if name == "nt" :
	WIN_WIDTH, WIN_HEIGH = getSystemResolutionOnWin()
elif name == "posix" :
	WIN_WIDTH, WIN_HEIGH = getSystemResolutionOnLin()
else:
	WIN_WIDTH = 500
	WIN_HEIGH = 380
	
WIN_WIDTH = int( WIN_WIDTH * 0.8 )
WIN_HEIGH = int( WIN_HEIGH * 0.8 )

FONT_SIZE = int( WIN_WIDTH * 0.05 )
TITRE = "Visualisation d'objets géométriques"
SCRIPT_PATH=path[0]

OMEGA = pi / 6 / 1000#rad/ms
SPEED = 100.0 / 1000#px/ms

L = 10
N = 50

MB_LEFT, MB_MIDDLE, MB_RIGHT, MBSW_UP, MBSW_DOWN = 1, 2, 3, 4, 5

#              R    G    B
WHITE      = (250, 250, 250)
BLACK      = ( 10,  10,  10)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)
RED        = (200,   0,   0)
