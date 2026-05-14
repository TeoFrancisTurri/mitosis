import math

from shared.protocol.snapshot_fields import (
	COLOR,
	ID,
	USERNAME,
	X,
	Y,
	RADIUS,
	MASS
)

from shared.protocol.input_fields import (
	DIRECTION_X,
	DIRECTION_Y,
)


from server.config.player_config import (
	PLAYER_MIN_SPEED,
	PLAYER_MAX_SPEED,
	PLAYER_SPEED_FACTOR,
	PLAYER_INITIAL_MASS,
	PLAYER_INITIAL_RADIUS
)



class Player:
	def __init__(self, player_id, username, x, y, color):
		self.player_id = player_id
		self.username = username
		self.color = color

		self.x = x
		self.y = y
		self.color = color
		self.mass = PLAYER_INITIAL_MASS
		self.radius = PLAYER_INITIAL_RADIUS
		self.direction_x = 0
		self.direction_y = 0

		self.alive = True


	@property
	def speed(self):
		return max(
			PLAYER_MIN_SPEED,
			PLAYER_MAX_SPEED - self.radius * PLAYER_SPEED_FACTOR
		)

	def update_input(self, message):
		direction_x = message.get(DIRECTION_X, 0)
		direction_y = message.get(DIRECTION_Y, 0)

		self.set_direction(direction_x, direction_y)

	def set_direction(self, direction_x, direction_y):
		self.direction_x = direction_x
		self.direction_y = direction_y

	def update(self):
		self.x += self.direction_x * self.speed
		self.y += self.direction_y * self.speed

	def calculate_radius_from_mass(self):
		return int(math.sqrt(self.mass) * 4)
	
	def eat(self, food):
		self.mass += food.mass
		self.radius = self.calculate_radius_from_mass()

	def to_snapshot(self):
		return {
			ID: self.player_id,
			USERNAME: self.username,
			X: self.x,
			Y: self.y,
			RADIUS: self.radius,
			COLOR: self.color,
			MASS: self.mass
		}
	

	def add_mass(self, amount):
		self.mass += amount
		self.update_radius()

	def remove_mass(self, amount):
		self.mass = max(1, self.mass - amount)
		self.update_radius()