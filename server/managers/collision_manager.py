import math

from server.config import PLAYER_EAT_MASS_MULTIPLIER

class CollisionManager:
    def __init__(self, match):
        self.match = match

    def update(self):
        self.check_player_food_collisions()
        self.check_player_player_collisions()
        self.check_player_virus_collisions()
        self.check_food_virus_collisions()
        self.check_cell_merges()

    def check_player_food_collisions(self):
        eaten_food_ids = set()
        foods = list(self.match.foods.values())

        for player in self.match.players.values():
            for cell in player.cells:
                for food in foods:
                    if food.food_id in eaten_food_ids:
                        continue
                    if self.is_center_inside_circle(food, cell):
                        cell.add_mass(food.mass)
                        player.on_food_eaten()
                        eaten_food_ids.add(food.food_id)

        for food_id in eaten_food_ids:
            self.match.foods.pop(food_id, None)
            self.match.food_manager.add_food()

    def check_player_player_collisions(self):
        players = list(self.match.players.values())
        eaten_cells = set()
        collisions = []

        for big_player in players:
            for small_player in players:
                if big_player.player_id == small_player.player_id:
                    continue

                for small_cell in small_player.cells:
                    if small_cell in eaten_cells:
                        continue

                    eating_cell = self.get_eating_cell(big_player, small_cell)
                    if eating_cell is not None:
                        eaten_cells.add(small_cell)
                        collisions.append((big_player, eating_cell, small_player, small_cell))

        dead_players = []
        for big_player, eating_cell, small_player, small_cell in collisions:
            eating_cell.add_mass(small_cell.mass)
            big_player.on_player_eaten()
            small_player.cells.remove(small_cell)

            if not small_player.cells and small_player not in dead_players:
                dead_players.append(small_player)

        for player in dead_players:
            self.match.player_dead(player)

    def get_eating_cell(self, big_player, small_cell):
        for big_cell in big_player.cells:
            if big_cell.mass >= small_cell.mass * PLAYER_EAT_MASS_MULTIPLIER:
                if self.is_center_inside_circle(small_cell, big_cell):
                    return big_cell
        return None

    def check_player_virus_collisions(self):
        viruses = list(self.match.viruses.values())
        eaten_virus_ids = set()

        for player in self.match.players.values():
            for cell in player.cells:
                for virus in viruses:
                    if virus.virus_id in eaten_virus_ids:
                        continue
                    if cell.mass < virus.mass * PLAYER_EAT_MASS_MULTIPLIER:
                        continue
                    if self.is_center_inside_circle(virus, cell):
                        cell.add_mass(virus.mass)
                        eaten_virus_ids.add(virus.virus_id)
                        self.match.player_manager.split_cell_at_virus(player, cell)

        for virus_id in eaten_virus_ids:
            self.match.viruses.pop(virus_id, None)
            self.match.virus_manager.respawn_virus()

    def check_food_virus_collisions(self):
        viruses = list(self.match.viruses.values())
        eaten_food_ids = set()

        for food in list(self.match.foods.values()):
            if food.vx == 0 and food.vy == 0:
                continue
            speed = math.hypot(food.vx, food.vy)
            dir_x = food.vx / speed
            dir_y = food.vy / speed
            for virus in viruses:
                if self.is_center_inside_circle(food, virus):
                    eaten_food_ids.add(food.food_id)
                    self.match.virus_manager.feed_virus(virus, dir_x, dir_y, food.mass)
                    break

        for food_id in eaten_food_ids:
            self.match.foods.pop(food_id, None)

    def check_cell_merges(self):
        for player in self.match.players.values():
            merged = set()

            for i, cell_a in enumerate(player.cells):
                for cell_b in player.cells[i + 1:]:
                    if cell_a in merged or cell_b in merged:
                        continue
                    if cell_a.merge_timer > 0 or cell_b.merge_timer > 0:
                        continue
                    if self.is_center_inside_circle(cell_a, cell_b) or self.is_center_inside_circle(cell_b, cell_a):
                        total_mass = cell_a.mass + cell_b.mass
                        cell_a.x = (cell_a.x * cell_a.mass + cell_b.x * cell_b.mass) / total_mass
                        cell_a.y = (cell_a.y * cell_a.mass + cell_b.y * cell_b.mass) / total_mass
                        cell_a.add_mass(cell_b.mass)
                        merged.add(cell_b)

            player.cells = [c for c in player.cells if c not in merged]

    def is_center_inside_circle(self, inner_entity, outer_entity):
        distance = self.get_distance(inner_entity, outer_entity)
        return distance <= outer_entity.radius

    def get_distance(self, entity_a, entity_b):
        return math.hypot(
            entity_a.x - entity_b.x,
            entity_a.y - entity_b.y
        )
