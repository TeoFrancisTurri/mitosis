from shared.protocol.snapshot_fields import (
    ID,
    X,
    Y,
    RADIUS,
    MASS,
    COLOR,
)


class Food:
    def __init__(self, food_id, x, y, radius, mass, color):
        self.food_id = food_id

        self.x = x
        self.y = y

        self.radius = radius
        self.mass = mass

        self.color = color

        self.vx = 0.0
        self.vy = 0.0

    def to_snapshot(self):
        return {
            ID: self.food_id,
            X: self.x,
            Y: self.y,
            RADIUS: self.radius,
            MASS: self.mass,
            COLOR: self.color,
        }