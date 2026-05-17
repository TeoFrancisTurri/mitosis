import random

from server.entities import Food
from server.config import FOOD_INITIAL_AMOUNT, FOOD_TYPES, RADIUS, MASS
from shared.config import ENTITIES_COLORS

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

    def to_snapshot(self):
        foods = self.match.foods.values()
        return [
            food.to_snapshot()
            for food in foods
        ]