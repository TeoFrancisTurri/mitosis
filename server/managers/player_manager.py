import random
import math
import threading

from server.entities import Player
from server.config import PLAYER_INITIAL_MASS, ATTEMPS_TO_SPAWN
from shared.config import ENTITIES_COLORS


class PlayerManager:
    def __init__(self, match):
        self.match = match
        self.next_player_id = 1
        self.lock = threading.Lock()

    def add_player(self, username):
        
        initial_radius = Player.calculate_radius_from_mass(PLAYER_INITIAL_MASS)
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

    def respawn_player(self, player):
        initial_radius = Player.calculate_radius_from_mass(PLAYER_INITIAL_MASS)
        initial_position = len(self.match.players) + 1
        x, y = self.get_random_spawn(initial_radius)
        player.respawn(x, y, initial_position)
        self.match.players[player.player_id] = player

    def update(self, delta_time):
        with self.lock:
            players = list(self.match.players.values())

        for player in players:
            player.update(delta_time)
            self.keep_inside_map(player)

    def keep_inside_map(self, player):
        player.x = max(0, min(player.x, self.match.map_width))
        player.y = max(0, min(player.y, self.match.map_height))

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
        players = self.match.players.values()

        return [
            player.to_snapshot()
            for player in players
        ]