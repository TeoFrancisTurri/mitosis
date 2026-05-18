import math

from server.config import VIRUS_INITIAL_MASS, VIRUS_COLOR
from shared.protocol.snapshot_fields import ID, X, Y, RADIUS, COLOR


class Virus:
    def __init__(self, virus_id, x, y):
        self.virus_id = virus_id
        self.x = x
        self.y = y
        self.mass = VIRUS_INITIAL_MASS
        self.radius = self._calc_radius(VIRUS_INITIAL_MASS)
        self.color = VIRUS_COLOR
        self.vx = 0.0
        self.vy = 0.0
        self.last_feed_dx = 1.0
        self.last_feed_dy = 0.0

    @staticmethod
    def _calc_radius(mass):
        return int(math.sqrt(mass) * 4)

    def add_mass(self, amount, direction_x, direction_y):
        self.mass += amount
        self.radius = self._calc_radius(self.mass)
        self.last_feed_dx = direction_x
        self.last_feed_dy = direction_y

    def reset(self):
        self.mass = VIRUS_INITIAL_MASS
        self.radius = self._calc_radius(VIRUS_INITIAL_MASS)

    def to_snapshot(self):
        return {
            ID: self.virus_id,
            X: self.x,
            Y: self.y,
            RADIUS: self.radius,
            COLOR: self.color,
        }
