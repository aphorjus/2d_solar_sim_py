import arcade
import uuid
import math
from Vec2D import Vec2D

class Orb:

	def __init__(self, x=0, y=0, size=30, color=arcade.color.WHITE):
		self.pos = Vec2D(x,y)
		self.size = size
		self.color = color

		self.mass = 4*3.14*((size/2)*(size/2))
		self.vel = Vec2D(0,0)
		self.acc = Vec2D(0,0)
		self.trust = 1.0

		self.uuid = uuid.uuid4()

	def __eq__(self, other):
		return self.uuid == other.uuid

	def __ne__(self, other):
		return not self.__eq__(other)

	def draw(self):
		arcade.draw_ellipse_filled(self.pos.x, 
                               self.pos.y, 
                               self.size, 
                               self.size, 
                               self.color )

	def set_direction(self, direction):
		self.acc += direction.set_mag(self.trust)

	def set_pos(self, pos):
		self.pos = pos

	def apply_force_from(self, other, G):
		force_vec = self.get_force_applyed(other, G)
		acc = force_vec.set_mag(force_vec.get_mag()/self.mass)
		self.acc += acc

	def get_force_applyed(self, other, G):
		dist_vec = self.get_dist_vec(other)
		r = dist_vec.get_mag()
		mag = (G * self.mass * other.mass) / ( r * r )

		return dist_vec.set_mag(mag)

	def get_dist_vec(self, other):
		return (other.pos-self.pos)

	def get_dist(self, other):
		return self.get_dist_vec(other).get_mag()

	def is_colliding(self, other):
		return self != other and self.get_dist(other) < self.size/2

	# def collide_elastic(self, other):
	# 	term_one = ((2*other.vel)/(self.mass+other.mass))
	# 	term_two = (self.vel-other.vel)*(self.pos-other.pos)/()
	# 	v1 = self.vel-((2*other.vel)/(self.mass+other.mass))*()

	def absorb(self, other):
		self.mass += other.mass
		self.size = 2*math.sqrt(self.mass/(4*3.14))		


	def slow(self):
		if(self.vel.get_mag() < 1):
			self.vel = Vec2D(0,0)
			self.acc = Vec2D(0,0)
			return
		direction = Vec2D(-self.vel.x, -self.vel.y)
		self.acc = direction.set_mag(self.trust*0.8)	

	def get_orbital_vel(self, other, G):
		dist_vec = self.get_dist_vec(other)
		r = dist_vec.get_mag()
		mag = math.sqrt(G*(other.mass+self.mass)/r)
		return dist_vec.rotate(math.radians(90)).set_mag(mag)+other.vel

	def orbit(self, other, G):
		o_vel = self.get_orbital_vel(other, G)
		s_vel = self.vel
		correction = o_vel - s_vel

		if correction.get_mag() > self.trust:
			correction = correction.set_mag(self.trust)

		self.acc += correction

	def update(self):
		self.vel += self.acc
		self.pos += self.vel