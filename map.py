import arcade
from Vec2D import Vec2D

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

def draw_map(bodies, window_width, window_height):

	map_shape_list = arcade.ShapeElementList()

	view = arcade.get_viewport()
	map_width = window_width/3.5
	map_height = window_height/3.5
	map_padding = window_height/80
	map_center_x = view[1]-(map_width/2+map_padding)
	map_center_y = view[2]+(map_height/2+map_padding)
	#view[0] = left, view[1] = right, view[2] = bottom, view[3] = top
	rec = arcade.create_rectangle_filled(
		map_center_x, map_center_y, 
		map_width, map_height, arcade.color.BLACK)
	rec2 = arcade.create_rectangle_outline(
		map_center_x, map_center_y, 
		map_width, map_height, arcade.color.WHITE,
		window_width/400)

	map_shape_list.append(rec)
	map_shape_list.append(rec2)

	max_mass = 0
	cm = None # find_center_of_mass(bodies)
	for bodie in bodies:
		if max_mass < bodie.mass:
			max_mass = bodie.mass
			cm = bodie.pos

	max_dist = 1
	for bodie in bodies:
		this_dist = (cm - bodie.pos).get_mag()
		if max_dist < this_dist:
			max_dist = this_dist
		
	scaler = max_dist/((map_height-map_padding)/2)
	# print(scaler)
	# scaler = 60

	for bodie in bodies:
		map_pos = (bodie.pos - cm)
		map_pos.x /= scaler
		map_pos.y /= scaler
		map_pos += Vec2D(map_center_x, map_center_y)
		map_shape_list.append( 	arcade.create_ellipse_filled(
															map_pos.x, map_pos.y, 
															window_width/300, window_width/300, 
															bodie.color ))

	map_shape_list.draw()