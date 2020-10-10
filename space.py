import arcade
import math
import random
from Vec2D import Vec2D
from Orb import Orb, Ship
from map import draw_map

WIDTH = 1200
HEIGHT = 800

WORLD_WIDTH = WIDTH*10
WORLD_HEIGHT = HEIGHT*10
BORDER = WIDTH/2

SEED = 1000
random.seed(SEED)

G = 0.6

def make_stars(star_count=1000):
	shape_list = arcade.ShapeElementList()

	for star_no in range(star_count):
		x = random.randrange(WORLD_WIDTH)
		y = random.randrange(WORLD_HEIGHT)
		radius = random.randrange(1, 4)
		brightness = random.randrange(127, 256)
		color = (brightness, brightness, brightness)
		shape = arcade.create_rectangle_filled(x, y, radius, radius, color)
		shape_list.append(shape)

	return shape_list

def get_player_thrust_vector(x,y):
	return Vec2D(x-(WIDTH/2), y-(HEIGHT/2))


def get_orbital_pos_vec(orbiting):
	direction = Vec2D(random.random()-0.5, random.random()-0.5)
	position = direction.set_mag(random.randint(orbiting.size, orbiting.size*10))
	position += orbiting.pos
	return position


def get_orbital_pos(orbiting, orbital_level):
	pos_found = False

	while not pos_found:
		position = get_orbital_pos_vec(orbiting)
		pos_found = True

		for bodie in orbital_level:
			if (bodie.pos - position).get_mag() < orbiting.size*5:
				pos_found = False

	return position

def build_solor_system(center_mass, num_bodies_arr):
	solor_system = []
	center_mass = Orb(0, 0, center_mass, arcade.color.YELLOW)
	solor_system.append([center_mass])

	for i in range(1, len(num_bodies_arr)):
		orbital_level = []
		for j in range(num_bodies_arr[i]):
			color = ( random.randint(0,255), 
								random.randint(0,255), 
								random.randint(0,255))

			orbiting = solor_system[i-1][random.randint(0, len(solor_system[i-1])-1)]
						
			position = get_orbital_pos(orbiting, orbital_level)

			size = random.randint(int(orbiting.size/20), int(orbiting.size/5))
			orbital_level.append(
				Orb(position.x, position.y, size, color, [orbiting, G]))

		# print(orbital_level)
		solor_system.append(orbital_level)

	return_system = []
	for system in solor_system:
		return_system += system

	return return_system

def orb_in_view(orb):
	view = arcade.get_viewport()
	# view[0] = left, view[1] = right, view[2] = bottom, view[3] = top
	offset = int(orb.size/2)
	view = (view[0]-offset, view[1]+offset, view[2]-offset, view[3]+offset)

	in_vert_view = orb.pos.x > view[0] and view[1] > orb.pos.x
	in_horz_view = orb.pos.y > view[2] and view[3] > orb.pos.y

	return in_vert_view and in_horz_view

class Game(arcade.Window):
	
	def __init__(self, width, height, title):
		super().__init__(WIDTH, HEIGHT, 'Space?')

		arcade.set_background_color(arcade.color.BLACK)
		self.bodies = []
		self.ships = []
		self.orb = None
		self.dest = None
		self.center_mass = None
		# self.stars = make_stars()
		self.buttons_down = {
			'rmb' : False,
			'lmb' : False,
			'v'		: False
		}

		self.orb_index = 0
		self.dest_index = 0
		
		self.mouse_pos = Vec2D(0,0)
		self.window_width = WIDTH
		self.window_height = HEIGHT

		self.zoom_speed = 20
		self.map_on = True


	def setup(self):
		
		self.bodies = build_solor_system(1000, [1,3,1])
		
		self.orb_index = len(self.bodies)-1
		self.orb = self.bodies[self.orb_index]

		self.dest_index = 2
		self.dest = self.bodies[self.dest_index]

	def on_draw(self):
		arcade.start_render()

		# self.stars._refresh_shape((5,1))
		# self.stars.draw()
		
		for bodie in self.bodies:
			if orb_in_view(bodie):
				bodie.draw()

				if(self.buttons_down['v']):
					arcade.draw_line(
						bodie.pos.x, bodie.pos.y, 
						bodie.pos.x+bodie.vel.x,
						bodie.pos.y+bodie.vel.y,
						arcade.color.WHITE, bodie.size/10)

			if bodie == self.orb and self.dest != self.orb:
				arcade.draw_line(
					bodie.pos.x, bodie.pos.y, 
					self.dest.pos.x, self.dest.pos.y,
					self.dest.color, 2)

		if self.map_on:
			draw_map(self.bodies, self.window_width, self.window_height)

		arcade.finish_render()

	def update(self, delta_time):

		## updating gravitational effects ##
		forces = [Vec2D(0,0) for _ in range(len(self.bodies))]

		for i, bodie in enumerate(self.bodies):
			for other_bodie in self.bodies:
				if bodie != other_bodie and not isinstance(other_bodie, Ship):
						forces[i] += bodie.get_force_applyed(other_bodie, G)

		for ship in self.ships:
			for bodie in self.bodies:
				ship.apply_force_from(bodie, G)

		##  ############################  ##

		for i, bodie in enumerate(self.bodies):
			bodie.apply_force(forces[i])
			bodie.update()

		for ship in self.ships:
			ship.update()

		
		## calculating collisions and collision effects ##
		## Needs Rewrite: potential to break with multiple collisions
		absorbed = []
		for bodie in self.bodies:
			for other_bodie in self.bodies:
				if bodie.is_colliding(other_bodie):
					if bodie.mass > other_bodie.mass:
						bodie.absorb(other_bodie)
						absorbed.append(other_bodie)
						if self.orb == other_bodie:
							self.orb = bodie

			for ship in self.ships:
				if bodie.is_colliding(ship):
					bodie.absorb(ship)

		for bodie in absorbed:
			self.bodies.remove(bodie)

		##  ##########################################  ##

		## reset acceleration of all bodies to 0 for next update 
		for bodie in self.bodies:
			bodie.acc = Vec2D(0,0)
				
		self.apply_button_effects()

		## center view-port on selected orb
		arcade.set_viewport(
			self.orb.pos.x - self.window_width/2,
			self.orb.pos.x + self.window_width/2,
			self.orb.pos.y - self.window_height/2,
			self.orb.pos.y + self.window_height/2
		)


	########################
	##			CONTROLS 			##
	########################

	def apply_button_effects(self):
		if self.buttons_down['lmb']:
			x, y = self.mouse_pos.x, self.mouse_pos.y
			self.orb.set_direction(get_player_thrust_vector(x,y))

		if self.buttons_down['rmb']:
			self.orb.orbit(self.dest, G)

	def on_key_press(self, key, key_modifiers):

		if key == arcade.key.S:
			self.orb_index += 1
			if self.orb_index >= len(self.bodies):
				self.orb_index = 0

			self.orb = self.bodies[self.orb_index]

		if key == arcade.key.D:
			self.dest_index += 1
			if self.dest_index >= len(self.bodies):
				self.dest_index = 0

			self.dest = self.bodies[self.dest_index]

		## make satellite around dest
		## prob should be it's own function
		if key == arcade.key.A:
			x = self.dest.pos.x
			y = self.dest.pos.y
			size = self.dest.size
			new_orb = Ship(x+(size*2),y+(size*2))
			new_orb.vel = new_orb.get_orbital_vel(self.dest, G)
			self.ships.append(new_orb)

		if key == arcade.key.V:
			self.buttons_down['v'] = True

		if key == arcade.key.M:
			self.map_on = not self.map_on


	def on_key_release(self, key, key_modifiers):

		if key == arcade.key.V:
			self.buttons_down['v'] = False


	def on_mouse_press(self, x, y, button, key_modifiers):
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.buttons_down['lmb'] = True
		if button == arcade.MOUSE_BUTTON_RIGHT:
			self.buttons_down['rmb'] = True


	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_pos = Vec2D(x,y)


	def on_mouse_release(self, x, y, button, key_modifiers):
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.orb.acc = Vec2D(0,0)
			self.buttons_down['lmb'] = False
		if button == arcade.MOUSE_BUTTON_RIGHT:
			self.orb.acc = Vec2D(0,0)
			self.buttons_down['rmb'] = False

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

		if scroll_y > 0 and self.window_height > self.window_width/self.zoom_speed:
			self.window_height -= self.window_height/self.zoom_speed
			self.window_width -= self.window_width/self.zoom_speed
		if scroll_y < 0:
			self.window_height += self.window_height/self.zoom_speed
			self.window_width += self.window_width/self.zoom_speed


def main():
  game = Game(WIDTH, HEIGHT, 'sprouts')
  game.setup()
  arcade.run()

if __name__ == "__main__":
  main()