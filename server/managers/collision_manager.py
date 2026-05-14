import math


class CollisionManager:
    def __init__(self, match):
        self.match = match

    def update(self):
        self.check_player_food_collisions()

    def check_player_food_collisions(self):
        eaten_food_ids = []

        for player in self.match.players.values():
            for food in self.match.foods.values():
                if self.is_player_eating_food(player, food):
                    player.eat(food)
                    eaten_food_ids.append(food.food_id)

        for food_id in eaten_food_ids:
            self.match.foods.pop(food_id, None)
            self.match.add_food()

    def is_player_eating_food(self, player, food):
        distance = math.hypot(
            player.x - food.x,
            player.y - food.y
        )

        return distance <= player.radius