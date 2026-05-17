import math
import time

from shared.protocol import (
	COLOR,
	ID,
	USERNAME,
	X,
	Y,
	RADIUS,
	MASS,
	DIRECTION_X,
	DIRECTION_Y,
	CELLS_EATEN,
	FOOD_EATEN,
	HIGHEST_MASS,
	LEADERBOARD_TIME,
	TOP_POSITION,
	TIME_ALIVE
)

from server.config import (
	PLAYER_MIN_SPEED,
	PLAYER_MAX_SPEED,
	PLAYER_SPEED_FACTOR,
	PLAYER_INITIAL_MASS,
	TOP_PLAYERS_LEADERBOARD
)




class Player:
	def __init__(self, player_id, username, x, y, color, initial_position):
		self.player_id = player_id
		self.username = username
		self.color = color

		self.x = x
		self.y = y
		self.color = color
		self.mass = PLAYER_INITIAL_MASS
		self.radius = Player.calculate_radius_from_mass(self.mass)
		self.direction_x = 0
		self.direction_y = 0
		self.current_position = initial_position

		self.spawn_time = time.monotonic()

		#stats
		self.food_eaten = 0
		self.highest_mass = self.mass
		self.time_alive = 0
		self.cells_eaten = 0
		self.leaderboard_time = 0
		self.top_position = self.current_position


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

	def update(self, delta_time):
		self.time_alive = time.monotonic() - self.spawn_time
		self.x += self.direction_x * self.speed * delta_time
		self.y += self.direction_y * self.speed * delta_time

	@staticmethod
	def calculate_radius_from_mass(mass):
		if not mass or mass <= 0:
			return 0
		return int(math.sqrt(mass) * 4)
	
	def eat_food(self, food):
		self.add_mass(food.mass)
		self.food_eaten += 1


	def eat_player(self, player):
		self.add_mass(player.mass)
		self.cells_eaten += 1

	
	def update_radius(self):
		self.radius = self.calculate_radius_from_mass(self.mass)

	def add_mass(self, amount):
		self.mass += amount
		self.update_radius()
		self.update_highest_mass()
		

	def remove_mass(self, amount):
		self.mass = max(1, self.mass - amount)
		self.update_radius()

	def calculate_alive_time(self):
		return time.monotonic() - self.spawn_time

	def kill(self):
		self.time_alive = self.calculate_alive_time()

		self.mass = 0
		self.radius = 0

	def respawn(self, x, y, initial_position):
		self.x = x
		self.y = y

		self.mass = PLAYER_INITIAL_MASS
		self.radius = self.calculate_radius_from_mass(self.mass)

		self.spawn_time = time.monotonic()

		self.food_eaten = 0
		self.highest_mass = self.mass
		self.time_alive = 0
		self.cells_eaten = 0
		self.leaderboard_time = 0
		self.current_position = initial_position
		self.top_position = initial_position


	def update_highest_mass(self):
		if self.mass > self.highest_mass:
			self.highest_mass = self.mass

	def update_leaderboard_stats(self, position, delta_time):
		self.current_position = position

		if position < self.top_position:
			self.top_position = position

		if position <= TOP_PLAYERS_LEADERBOARD:
			self.leaderboard_time += delta_time

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
	
	def stats_to_snapshot(self):
		return {
			FOOD_EATEN: self.food_eaten,
			CELLS_EATEN: self.cells_eaten,
			HIGHEST_MASS: self.highest_mass,
			LEADERBOARD_TIME: self.leaderboard_time,
			TOP_POSITION: self.top_position,
			TIME_ALIVE: self.time_alive 
		}