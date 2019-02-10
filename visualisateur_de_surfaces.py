

import pygame as pg
from pygame.locals import *
from pygame.draw import *
from math import *
from random import *
from constantes import *
from dictionnaires import *
from enumerations import *
from os import path, environ
import time

class Pos(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
		
class Dim(object):
	def __init__(self):
		self.w = 0
		self.h = 0
		
class Time(object):
	def __init__(self):
		self.past = 0.
		self.pres = 0.

class Vect(object):
	def __init__(self, x=0., y=0., z=0.):
		self.x = x
		self.y = y
		self.z = z
	
	def norm2(self):
		return self.x ** 2 + self.y ** 2 + self.z ** 2
	
	def norm(self):
		return sqrt( norm2( self.x , self.y , self.z ) )
	
	def homothetie(self, k):
		self.x *= k
		self.y *= k
		self.z *= k
	
	def add(self, x, y, z):
		self.x += x
		self.y += y
		self.z += z
	
	def rot(self, theta, basis):
		out = Vect()
		cosTheta = cos(theta)
		sinTheta = sin(theta)
		tmp = Vect()
		
		out.x =  basis.A.x * self.x + basis.A.y * self.y + basis.A.z * self.z
		out.y =  basis.B.x * self.x + basis.B.y * self.y + basis.B.z * self.z
		out.z =  basis.C.x * self.x + basis.C.y * self.y + basis.C.z * self.z
		
		tmp.y = out.y
		
		out.x =  out.x
		out.y =  out.y * cosTheta - out.z * sinTheta
		out.z =  tmp.y * sinTheta + out.z * cosTheta
		
		tmp.x = out.x
		tmp.y = out.y
		
		out.x =  basis.A.x * out.x + basis.B.x * out.y + basis.C.x * out.z
		out.y =  basis.A.y * tmp.x + basis.B.y * out.y + basis.C.y * out.z
		out.z =  basis.A.z * tmp.x + basis.B.z * tmp.y + basis.C.z * out.z

		return out

	def one_point_perspective(self):
		#return Pos( WIN_HEIGH * self.x / ( -WIN_HEIGH + self.z ) , WIN_HEIGH * self.y / ( -WIN_HEIGH + self.z ) )
		return Pos( self.x , self.y )

class Basis(object):
	def __init__(self):
		self.A = Vect(1.)#BRIGHTBLUE
		self.B = Vect(0.,1.)#RED
		self.C = Vect(0.,0.,1.)#GREEN
		self.theta = 0.
		self.phi = 0.
	
	def move(self,c):
		if c == 0 :
			self.theta -= pi / 12
			if self.theta < 0. :
				self.theta = 0.
		elif c == 1 :
			self.theta += pi / 12
			if pi < self.theta :
				self.theta = pi
		elif c == 2 :
			self.phi -= pi / 12
			if self.phi < 0. :
				self.phi = 0.
		else:
			self.phi += pi / 12
			if 2 * pi < self.phi :
				self.phi = 2 * pi
		self.A = Vect(  cos(self.theta) * cos(self.phi) , cos(self.theta) * sin(self.phi) , -sin(self.theta) )
		self.B = Vect( -sin(self.phi)                   , cos(self.phi)                   ,  0.              )
		self.C = Vect(  sin(self.theta) * cos(self.phi) , sin(self.theta) * sin(self.phi) ,  cos(self.theta) )
		
class Surface(object):
	def __init__(self, nature):
		self.p = []
		self.isMoving = False
		self.tps = 0.
		self.edge = []
			
		if nature == CUBE :
			self.edge.append( [ 0 , 1 ] )
			self.edge.append( [ 2 , 3 ] )
			self.edge.append( [ 4 , 5 ] )
			self.edge.append( [ 6 , 7 ] )
			self.edge.append( [ 0 , 2 ] )
			self.edge.append( [ 0 , 4 ] )
			self.edge.append( [ 4 , 6 ] )
			self.edge.append( [ 1 , 3 ] )
			self.edge.append( [ 2 , 6 ] )
			self.edge.append( [ 1 , 5 ] )
			self.edge.append( [ 3 , 7 ] )
			self.edge.append( [ 5 , 7 ] )
				
			for i in range(2) :
				for j in range(2) :
					for k in range(2) :
						self.p.append( [ Vect( L / 2 * ( 2 * i - 1 ) ,  L / 2 * ( 2 * j - 1 ) ,  L / 2 * ( 2 * k - 1 ) ) , Vect() ] )
			
		if nature == TORUS :
			for i in range(N*N-1) :
				self.edge.append( [ i , i+1 ] )
			
			dtheta = 2*pi/(N-1)
			R = L
			r = L // 3
			for i in range(N) :
				for j in range(N) :
					self.p.append( [ Vect( ( R + r * cos(i*dtheta) ) * cos(j*dtheta) ,  \
						( R + r * cos(i*dtheta) ) * sin(j*dtheta) , \
							r * sin(-i*dtheta) + r * cos(4*j*dtheta) ) , Vect() ] )
			
		if nature == TREFOIL_KNOT :
			for i in range(N*N-1) :
				self.edge.append( [ i , i+1 ] )
			
			dtheta = 2*pi/(N-1)
			R = L
			r = L // 3
			for i in range(N) :
				for j in range(N) :
					self.p.append( [ Vect( ( R + r * cos(i*dtheta) ) * ( sin(j*dtheta) + 2 * sin(2*j*dtheta) ) ,  \
						( R + r * cos(i*dtheta) ) * ( cos(j*dtheta) - 2 * cos(2*j*dtheta) ) , \
							-R * sin(i*dtheta) + 1.7 * R * sin(3*j*dtheta) ) , Vect() ] )
			
		if nature == HELICOID :
			for i in range(5*N*N-1) :
				if i % (5*N) != 5*N-1 :
					self.edge.append( [ i , i+1 ] )
			
			dtheta = 2*pi/(N-1)
			for j in range(N) :
				for i in range(5*N) :
					self.p.append( [ Vect( j * cos(i*dtheta) , j * sin(i*dtheta) , i * 1. ) , Vect() ] )
	
	def move(self, basis):
		for i in range( len( self.p ) ) :
			self.p[i][PRES] = self.p[i][PAST].rot( OMEGA * ( pg.time.get_ticks() - self.tps ) % ( 2 * pi ) , basis )
	
	def startToMove(self):
		self.isMoving = True
		self.tps = pg.time.get_ticks()
		for i in range( len( self.p ) ) :
			self.p[i][PAST] = self.p[i][PRES]

class Visualization(object):
	def __init__(self):
		"""Init game"""
		self.surface = [ Surface(i) for i in range(4) ]
		self.zoom = 40.
		self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGH), pg.DOUBLEBUF | pg.HWSURFACE)
		self.bg = pg.Surface(self.screen.get_size())
		self.quitterJeu = False
		self.focus = CUBE
		self.basis = Basis()
		
	def main_loop(self):
		"""Main loop"""
		while not self.quitterJeu :
			self.event_loop()
			self.update()
			self.draw()
			pg.display.flip()
	
	def event_loop(self):
		"""Récupération des événements utilisateur"""
		for event in pg.event.get():
			if event.type == pg.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
				self.quitterJeu = True
			elif event.type == KEYDOWN and event.key == K_q :
				if self.surface[self.focus].isMoving :
					self.surface[self.focus].isMoving = False
				else:
					self.surface[self.focus].startToMove()
			elif event.type == KEYDOWN and event.key == K_e :
				self.basis.move(0)
			elif event.type == KEYDOWN and event.key == K_r :
				self.basis.move(1)
			elif event.type == KEYDOWN and event.key == K_t :
				self.basis.move(2)
			elif event.type == KEYDOWN and event.key == K_y :
				self.basis.move(3)
			elif ( event.type == MOUSEBUTTONDOWN and event.button ) == MBSW_UP :
				self.zoom *= 1.41
			elif ( event.type == MOUSEBUTTONDOWN and event.button ) == MBSW_DOWN :
				self.zoom /= 1.41
			elif ( event.type == MOUSEBUTTONDOWN and event.button ) == MB_LEFT :
				self.surface[self.focus].isMoving = False
				self.focus = ( self.focus + 1 ) % len(self.surface)
			elif ( event.type == MOUSEBUTTONDOWN and event.button ) == MB_RIGHT :
				self.surface[self.focus].isMoving = False
				self.focus = ( self.focus - 1 ) % len(self.surface)
	
	def update(self):
		"""Actualisation positions corps"""
		if self.surface[self.focus].isMoving :
			self.surface[self.focus].move(self.basis)

	def draw(self):
		"""Dessine l'interface."""
		self.bg.fill(WHITE)
		for edge in self.surface[self.focus].edge :
			if 0. < self.surface[self.focus].p[edge[0]][PRES].z and 0. < self.surface[self.focus].p[edge[1]][PRES].z :
				line( self.bg, RED, ( change_basis( self.surface[self.focus].p[edge[0]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( self.surface[self.focus].p[edge[1]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ) )
			elif sign(self.surface[self.focus].p[edge[0]][PRES].z) != sign(self.surface[self.focus].p[edge[1]][PRES].z) :
				line( self.bg, BRIGHTBLUE, ( change_basis( self.surface[self.focus].p[edge[0]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( self.surface[self.focus].p[edge[1]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ) )
			else:
				line( self.bg, GREEN, ( change_basis( self.surface[self.focus].p[edge[0]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( self.surface[self.focus].p[edge[1]][PRES].one_point_perspective(), Pos(0,0), self.zoom ) ) )
		line( self.bg, BRIGHTBLUE, ( change_basis( self.basis.A.one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( Pos(0,0), Pos(0,0), self.zoom ) ) )
		line( self.bg, RED, ( change_basis( self.basis.B.one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( Pos(0,0), Pos(0,0), self.zoom ) ) )
		line( self.bg, GREEN, ( change_basis( self.basis.C.one_point_perspective(), Pos(0,0), self.zoom ) ), ( change_basis( Pos(0,0), Pos(0,0), self.zoom ) ) )
		self.screen.blit(self.bg, (0, 0))

def sign(x):
	if x < 0 :
		return -1
	else:
		return 1

def d(x1, y1, x2, y2):
	return ( x2 - x1 ) ** 2 + ( y2 - y1 ) ** 2

def dot_product(x1, y1, x2, y2):
	return x2 * x1 + y2 * y1

def change_basis(e, ref, zoom):#from map basis to window basis
	return ( int( ( e.x - ref.x ) * zoom ) + WIN_WIDTH // 2 , int( ( e.y - ref.y ) * zoom ) + WIN_HEIGH // 2 )

if __name__ == '__main__' :
	pg.init()
	environ['SDL_VIDEO_CENTERED'] = '1'
	pg.display.set_caption(TITRE)
	icon_32x32 = pg.image.load( path.join(SCRIPT_PATH, "tore.png") )
	pg.display.set_icon(icon_32x32)
	pg.key.set_repeat(500, 100)
	
	visualization = Visualization()
	visualization.main_loop()
	
	pg.quit()
