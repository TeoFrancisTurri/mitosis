import random
from server.entities import Food
from server.config import FOOD_INITIAL_AMOUNT, FOOD_TYPES, EJECT_FRICTION, EJECT_SPEED, EJECT_FOOD_RADIUS
from shared.protocol import RADIUS, MASS
from server.config import ENTITIES_COLORS

class FoodManager:
    def __init__(self, match):
        self.match = match
        self.next_food_id = 1

    def generate_initial_foods(self):
        for _ in range(FOOD_INITIAL_AMOUNT):
            self.add_food()

    def add_food(self):
        food_type = random.choice(FOOD_TYPES)

        radius = food_type[RADIUS]
        mass = food_type[MASS]

        x = random.randint(radius, self.match.map_width - radius)
        y = random.randint(radius, self.match.map_height - radius)

        color = random.choice(ENTITIES_COLORS)

        food = Food(
            food_id=self.next_food_id,
            x=x,
            y=y,
            radius=radius,
            mass=mass,
            color=color
        )

        self.match.foods[food.food_id] = food
        self.next_food_id += 1

    def update(self, delta_time):
        for food in self.match.foods.values():
            if food.vx == 0 and food.vy == 0:
                continue
            food.x += food.vx * delta_time
            food.y += food.vy * delta_time
            decay = 1 - EJECT_FRICTION * delta_time
            food.vx *= decay
            food.vy *= decay
            if abs(food.vx) < 1 and abs(food.vy) < 1:
                food.vx = 0.0
                food.vy = 0.0

    def add_ejected_food(self, x, y, direction_x, direction_y, color, mass, cell_radius):
        food = Food(
            food_id=self.next_food_id,
            x=x + direction_x * (cell_radius + EJECT_FOOD_RADIUS),
            y=y + direction_y * (cell_radius + EJECT_FOOD_RADIUS),
            radius=EJECT_FOOD_RADIUS,
            mass=mass,
            color=color,
        )
        food.vx = direction_x * EJECT_SPEED
        food.vy = direction_y * EJECT_SPEED
        self.match.foods[food.food_id] = food
        self.next_food_id += 1

    def to_snapshot(self):
        foods = self.match.foods.values()
        return [
            food.to_snapshot()
            for food in foods
        ]