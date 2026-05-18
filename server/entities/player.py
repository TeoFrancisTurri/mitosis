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
	PLAYER_INITIAL_MASS,
	TOP_PLAYERS_LEADERBOARD
)

from server.entities.cell import Cell


class Player:
	def __init__(self, player_id, username, x, y, color, initial_position):
		self.player_id = player_id
		self.username = username
		self.color = color
		self.current_position = initial_position

		self.cells = [Cell(x, y, PLAYER_INITIAL_MASS)]

		self.spawn_time = time.monotonic()

		self.food_eaten = 0
		self.highest_mass = PLAYER_INITIAL_MASS
		self.time_alive = 0
		self.cells_eaten = 0
		self.leaderboard_time = 0
		self.top_position = initial_position

	@property
	def x(self):
		return sum(cell.x for cell in self.cells) / len(self.cells)

	@property
	def y(self):
		return sum(cell.y for cell in self.cells) / len(self.cells)

	@property
	def mass(self):
		return sum(cell.mass for cell in self.cells)

	@property
	def radius(self):
		return max(cell.radius for cell in self.cells)

	def update_input(self, message):
		direction_x = message.get(DIRECTION_X, 0)
		direction_y = message.get(DIRECTION_Y, 0)
		for cell in self.cells:
			cell.set_direction(direction_x, direction_y)

	def update(self, delta_time):
		self.time_alive = time.monotonic() - self.spawn_time
		for cell in self.cells:
			cell.update(delta_time)

	def on_food_eaten(self):
		self.food_eaten += 1
		self.update_highest_mass()

	def on_player_eaten(self):
		self.cells_eaten += 1
		self.update_highest_mass()

	def update_highest_mass(self):
		if self.mass > self.highest_mass:
			self.highest_mass = self.mass

	def kill(self):
		self.time_alive = time.monotonic() - self.spawn_time
		for cell in self.cells:
			cell.mass = 0
			cell.radius = 0

	def respawn(self, x, y, initial_position):
		self.cells = [Cell(x, y, PLAYER_INITIAL_MASS)]
		self.spawn_time = time.monotonic()
		self.food_eaten = 0
		self.highest_mass = PLAYER_INITIAL_MASS
		self.time_alive = 0
		self.cells_eaten = 0
		self.leaderboard_time = 0
		self.current_position = initial_position
		self.top_position = initial_position

	def update_leaderboard_stats(self, position, delta_time):
		self.current_position = position

		if position < self.top_position:
			self.top_position = position

		if position <= TOP_PLAYERS_LEADERBOARD:
			self.leaderboard_time += delta_time

	def to_snapshot(self):
		return [
			{
				ID: self.player_id,
				USERNAME: self.username,
				X: cell.x,
				Y: cell.y,
				RADIUS: cell.radius,
				COLOR: self.color,
				MASS: cell.mass,
			}
			for cell in self.cells
		]

	def stats_to_snapshot(self):
		return {
			FOOD_EATEN: self.food_eaten,
			CELLS_EATEN: self.cells_eaten,
			HIGHEST_MASS: self.highest_mass,
			LEADERBOARD_TIME: self.leaderboard_time,
			TOP_POSITION: self.top_position,
			TIME_ALIVE: self.time_alive,
		}
