import math

from server.config import PLAYER_EAT_MASS_MULTIPLIER

class CollisionManager:
    def __init__(self, match):
        self.match = match

    def update(self):
        self.check_player_food_collisions()
        self.check_player_player_collisions()

    def check_player_food_collisions(self):
        eaten_food_ids = []
        foods = list(self.match.foods.values())

        for player in self.match.players.values():
            for food in foods:
                if self.is_center_inside_circle(food, player):
                    player.eat_food(food)
                    eaten_food_ids.append(food.food_id)

        for food_id in eaten_food_ids:
            self.match.foods.pop(food_id, None)
            self.match.food_manager.add_food()

    def check_player_player_collisions(self):
        dead_players = []

        players = list(self.match.players.values())

        for big_player in players:
            for small_player in players:
                if big_player.player_id == small_player.player_id:
                    continue

                if small_player in dead_players:
                    continue

                if self.can_player_eat_player(big_player, small_player):
                    big_player.eat_player(small_player)
                    dead_players.append(small_player)

        for player in dead_players:
            self.match.player_dead(player)

    def can_player_eat_player(self, big_player, small_player):
        if big_player.mass < (small_player.mass * PLAYER_EAT_MASS_MULTIPLIER):
            return False

        return self.is_center_inside_circle(
            inner_entity=small_player,
            outer_entity=big_player
        )

    def is_center_inside_circle(self, inner_entity, outer_entity):
        distance = self.get_distance(inner_entity, outer_entity)

        return distance <= outer_entity.radius

    def get_distance(self, entity_a, entity_b):
        return math.hypot(
            entity_a.x - entity_b.x,
            entity_a.y - entity_b.y
        )