import arcade
import math
import random
from Vec2D import Vec2D
from Orb import Orb
from map import draw_map

WIDTH = 1200
HEIGHT = 800

WORLD_WIDTH = WIDTH*10
WORLD_HEIGHT = HEIGHT*10
BORDER = WIDTH/2

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

def find_center_of_mass(bodies):

	mass_weighted_average_x = 0
	mass_weighted_average_y = 0
	total_mass = 0

	for bodie in bodies:
		mass_weighted_average_x += bodie.mass*bodie.pos.x
		mass_weighted_average_y += bodie.mass*bodie.pos.y
		total_mass							+= bodie.mass

	x_cm = mass_weighted_average_x/total_mass
	y_cm = mass_weighted_average_y/total_mass

	return Vec2D(x_cm, y_cm)


class Game(arcade.Window):
	
	def __init__(self, width, height, title):
		super().__init__(WIDTH, HEIGHT, 'Space?')

		arcade.set_background_color(arcade.color.BLACK)
		self.bodies = []
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

	def setup(self):
		
		
		self.bodies.append(
			Orb(WORLD_WIDTH/2, WORLD_HEIGHT/2, 1000, arcade.color.YELLOW)
		)
		self.bodies.append( 
			Orb(WORLD_WIDTH/2, WORLD_HEIGHT/2+3000, 140, arcade.color.RED) 
		)
		self.bodies.append( 
			Orb(WORLD_WIDTH/2, WORLD_HEIGHT/2-6000, 90, arcade.color.BLUE) 
		)
		# self.bodies.append( 
		# 	Orb(WORLD_WIDTH/2+300, WORLD_HEIGHT/2+16000, 200, arcade.color.ORANGE) 
		# )
		self.bodies.append( 
			Orb(WORLD_WIDTH/2, WORLD_HEIGHT/2-6500, 5, arcade.color.GREEN) 
		)
		# self.bodies.append( 
		# 	Orb(WORLD_WIDTH/2, WORLD_HEIGHT/2-5500, 5, arcade.color.TEAL) 
		# )
		
		self.center_mass = self.bodies[0]

		for bodie in self.bodies:
			if bodie == self.center_mass:
				continue
			bodie.vel = bodie.get_orbital_vel(self.center_mass, G)


		
		self.orb_index = len(self.bodies)-1
		self.orb = self.bodies[self.orb_index]

		self.dest_index = 1
		self.dest = self.bodies[self.dest_index]

	def on_draw(self):
		arcade.start_render()

		# self.stars._refresh_shape((5,1))
		# self.stars.draw()
		for bodie in self.bodies:
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


		draw_map(self.bodies, self.window_width, self.window_height)

		arcade.finish_render()

	def update(self, delta_time):

		for bodie in self.bodies:
			for other_bodie in self.bodies:
				if bodie != other_bodie:
					bodie.apply_force_from(other_bodie, G)

		for bodie in self.bodies:
			bodie.update()

		## Needs Rewrite: potential to break with multiple collisions
		absorbed = []
		for bodie in self.bodies:
			for other_bodie in self.bodies:
				if bodie.is_colliding(other_bodie):
					if bodie.mass > other_bodie.mass:
						bodie.absorb(other_bodie)
						absorbed.append(other_bodie)

		for bodie in absorbed:
			self.bodies.remove(bodie)


		for bodie in self.bodies:
			bodie.acc = Vec2D(0,0)
				
		self.apply_button_effects()

		arcade.set_viewport(
			self.orb.pos.x - self.window_width/2,
			self.orb.pos.x + self.window_width/2,
			self.orb.pos.y - self.window_height/2,
			self.orb.pos.y + self.window_height/2
		)

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
			new_orb = Orb(x+(size*2),y+(size*2))
			new_orb.vel = new_orb.get_orbital_vel(self.dest, G)
			self.bodies.append(new_orb)

		if key == arcade.key.V:
			self.buttons_down['v'] = True


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