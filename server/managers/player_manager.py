import random
import math
import threading

from server.entities import Player, Cell
from server.config import PLAYER_INITIAL_MASS, ATTEMPS_TO_SPAWN, SPLIT_MIN_MASS, SPLIT_MAX_CELLS, SPLIT_EJECT_SPEED, SPLIT_MERGE_TIMER, CELL_MAX_ATTRACTION, EJECT_MIN_MASS, EJECT_MASS_AMOUNT
from server.config import ENTITIES_COLORS


class PlayerManager:
    def __init__(self, match):
        self.match = match
        self.next_player_id = 1
        self.lock = threading.Lock()

    def add_player(self, username):
        
        initial_radius = Cell.calculate_radius_from_mass(PLAYER_INITIAL_MASS)
        initial_position = len(self.match.players) + 1

        x, y = self.get_random_spawn(initial_radius)
        color = random.choice(ENTITIES_COLORS)
        player = Player(
            self.next_player_id,
            username,
            x,
            y,
            color,
            initial_position
        )
        self.match.players[player.player_id] = player
        self.next_player_id += 1

        return player

    def remove_player(self, player):
        return self.match.players.pop(player.player_id, None)

    def split_player(self, player):
        cells_to_split = [
            cell for cell in player.cells
            if cell.mass >= SPLIT_MIN_MASS and len(player.cells) < SPLIT_MAX_CELLS
        ]

        for cell in cells_to_split:
            if len(player.cells) >= SPLIT_MAX_CELLS:
                break

            half_mass = cell.mass / 2
            cell.mass = half_mass
            cell.radius = Cell.calculate_radius_from_mass(half_mass)

            new_cell = Cell(cell.x, cell.y, half_mass)
            new_cell.set_direction(cell.direction_x, cell.direction_y)
            new_cell.eject_speed_x = cell.direction_x * SPLIT_EJECT_SPEED
            new_cell.eject_speed_y = cell.direction_y * SPLIT_EJECT_SPEED
            new_cell.merge_timer = SPLIT_MERGE_TIMER
            cell.merge_timer = SPLIT_MERGE_TIMER

            player.cells.append(new_cell)

    def split_cell_at_virus(self, player, cell):
        total_cells = 1
        while (total_cells * 2 <= SPLIT_MAX_CELLS - len(player.cells) + 1
               and cell.mass / (total_cells * 2) >= SPLIT_MIN_MASS / 2):
            total_cells *= 2

        max_new = total_cells - 1
        if max_new <= 0:
            return

        piece_mass = cell.mass / total_cells
        cell.mass = piece_mass
        cell.radius = Cell.calculate_radius_from_mass(piece_mass)
        cell.merge_timer = SPLIT_MERGE_TIMER

        angle_step = 2 * math.pi / max_new
        new_cells = []
        for i in range(max_new):
            angle = angle_step * i
            new_cell = Cell(cell.x, cell.y, piece_mass)
            new_cell.set_direction(cell.direction_x, cell.direction_y)
            new_cell.eject_speed_x = math.cos(angle) * SPLIT_EJECT_SPEED
            new_cell.eject_speed_y = math.sin(angle) * SPLIT_EJECT_SPEED
            new_cell.merge_timer = SPLIT_MERGE_TIMER
            new_cells.append(new_cell)
        player.cells.extend(new_cells)

    def eject_mass(self, player):
        for cell in player.cells:
            if cell.mass <= EJECT_MIN_MASS:
                continue
            if cell.direction_x == 0 and cell.direction_y == 0:
                continue
            cell.add_mass(-EJECT_MASS_AMOUNT)
            self.match.food_manager.add_ejected_food(
                cell.x, cell.y,
                cell.direction_x, cell.direction_y,
                player.color, EJECT_MASS_AMOUNT,
                cell.radius,
            )

    def respawn_player(self, player):
        initial_radius = Cell.calculate_radius_from_mass(PLAYER_INITIAL_MASS)
        initial_position = len(self.match.players) + 1
        x, y = self.get_random_spawn(initial_radius)
        player.respawn(x, y, initial_position)
        self.match.players[player.player_id] = player

    def update(self, delta_time):
        with self.lock:
            players = list(self.match.players.values())

        for player in players:
            player.update(delta_time)
            self.attract_cells(player, delta_time)
            self.separate_cells(player)
            self.keep_inside_map(player)

    def attract_cells(self, player, delta_time):
        if len(player.cells) <= 1:
            return

        all_cells = player.cells
        centroid_x = sum(c.x for c in all_cells) / len(all_cells)
        centroid_y = sum(c.y for c in all_cells) / len(all_cells)

        ready_cells = [c for c in all_cells if c.merge_timer <= 0]
        if len(ready_cells) > 1:
            ready_cx = sum(c.x for c in ready_cells) / len(ready_cells)
            ready_cy = sum(c.y for c in ready_cells) / len(ready_cells)
        else:
            ready_cx = ready_cy = None

        for cell in player.cells:
            still_ejecting = cell.eject_speed_x != 0 or cell.eject_speed_y != 0
            if still_ejecting:
                continue

            if cell.merge_timer > 0:
                dx = centroid_x - cell.x
                dy = centroid_y - cell.y
                attraction = CELL_MAX_ATTRACTION
            else:
                if ready_cx is None:
                    continue
                dx = ready_cx - cell.x
                dy = ready_cy - cell.y
                attraction = CELL_MAX_ATTRACTION / 3

            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0:
                step = min(attraction * delta_time, dist)
                cell.x += (dx / dist) * step
                cell.y += (dy / dist) * step

    def separate_cells(self, player):
        cells = player.cells
        for i, cell_a in enumerate(cells):
            for cell_b in cells[i + 1:]:
                if cell_a.merge_timer <= 0 and cell_b.merge_timer <= 0:
                    continue
                dx = cell_b.x - cell_a.x
                dy = cell_b.y - cell_a.y
                dist = (dx * dx + dy * dy) ** 0.5
                min_dist = cell_a.radius + cell_b.radius
                if dist < min_dist and dist > 0:
                    overlap = (min_dist - dist) / 2
                    cell_a.x -= (dx / dist) * overlap
                    cell_a.y -= (dy / dist) * overlap
                    cell_b.x += (dx / dist) * overlap
                    cell_b.y += (dy / dist) * overlap

    def keep_inside_map(self, player):
        for cell in player.cells:
            cell.x = max(0, min(cell.x, self.match.map_width))
            cell.y = max(0, min(cell.y, self.match.map_height))

    def get_random_spawn(self, radius):
    
        for _ in range(ATTEMPS_TO_SPAWN):
            x = random.randint(radius, self.match.map_width - radius)
            y = random.randint(radius, self.match.map_height - radius)

            if self.is_valid_spawn(x, y, radius):
                return x, y

        return self.match.map_width // 2, self.match.map_height // 2

    def is_valid_spawn(self, x, y, radius):
        for player in self.match.players.values():
            distance = math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2)
            min_distance = radius + player.radius + 50

            if distance < min_distance:
                return False

        return True

    def to_snapshot(self):
        cells = []
        for player in self.match.players.values():
            cells.extend(player.to_snapshot())
        return cells