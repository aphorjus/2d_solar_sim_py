import arcade
import uuid
from Vec2D import Vec2D

class Orb:

	def __init__(self, x=0, y=0, size=30, color=arcade.color.WHITE):
		self.pos = Vec2D(x,y)
		self.size = size
		self.color = color

		self.mass = size*size
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
		self.acc += self.get_force_applyed(other, G)

	def get_force_applyed(self, other, G):
		dist_vec = (other.pos-self.pos)
		r = dist_vec.get_mag()
		mag = (G * ( self.mass * other.mass / r * r ))/self.mass

		return dist_vec.set_mag(mag)

	def get_dist(self, other):
		return 

	def slow(self):
		if(self.vel.get_mag() < 1):
			self.vel = Vec2D(0,0)
			self.acc = Vec2D(0,0)
			return
		direction = Vec2D(-self.vel.x, -self.vel.y)
		self.acc = direction.set_mag(self.trust*0.8)

	def update(self):
		self.vel += self.acc
		self.pos += self.vel