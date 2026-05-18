import math

from server.config import PLAYER_MIN_SPEED, PLAYER_MAX_SPEED, PLAYER_SPEED_FACTOR, SPLIT_EJECT_FRICTION


class Cell:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = Cell.calculate_radius_from_mass(mass)
        self.direction_x = 0
        self.direction_y = 0
        self.eject_speed_x = 0
        self.eject_speed_y = 0
        self.merge_timer = 0.0

    @property
    def speed(self):
        return max(
            PLAYER_MIN_SPEED,
            PLAYER_MAX_SPEED - self.radius * PLAYER_SPEED_FACTOR,
        )

    def update(self, delta_time):
        self.x += (self.direction_x * self.speed + self.eject_speed_x) * delta_time
        self.y += (self.direction_y * self.speed + self.eject_speed_y) * delta_time

        if self.eject_speed_x != 0 or self.eject_speed_y != 0:
            decay = 1 - SPLIT_EJECT_FRICTION * delta_time
            self.eject_speed_x *= decay
            self.eject_speed_y *= decay

            if abs(self.eject_speed_x) < 1 and abs(self.eject_speed_y) < 1:
                self.eject_speed_x = 0
                self.eject_speed_y = 0

        if self.merge_timer > 0:
            self.merge_timer = max(0.0, self.merge_timer - delta_time)

    def set_direction(self, direction_x, direction_y):
        self.direction_x = direction_x
        self.direction_y = direction_y

    def add_mass(self, amount):
        self.mass += amount
        self.radius = Cell.calculate_radius_from_mass(self.mass)

    @staticmethod
    def calculate_radius_from_mass(mass):
        if not mass or mass <= 0:
            return 0
        return int(math.sqrt(mass) * 4)
