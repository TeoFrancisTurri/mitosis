import random
import math
import threading
import time

from server.entities.player import Player
from server.config.player_config import PLAYER_INITIAL_RADIUS
from server.config.match_config import MATCH_TICK_RATE
from server.config.food_config import FOOD_TYPES, FOOD_INITIAL_AMOUNT, RADIUS, MASS
from server.entities.food import Food
from server.managers.collision_manager import CollisionManager

from shared.config.world_config import MAP_HEIGHT, MAP_WIDTH
from shared.config.colors import ENTITIES_COLORS
from shared.protocol.message_types import MATCH_FOUND, GAME_STATE
from shared.protocol.message_fields import TYPE, PLAYER_ID, SNAPSHOT, TICK


class Match:
    def __init__(self, match_id):
        self.match_id = match_id

        self.client_handlers = []
        self.players = {}
        self.foods = {}

        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT

        self.next_player_id = 1
        self.next_food_id = 1
        self.tick = 0
        self.collision_manager = CollisionManager(self)

        self.generate_initial_foods()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.running:
            self.tick += 1

            self.update()
            self.collision_manager.update()
            self.send_snapshot()

            time.sleep(1 / MATCH_TICK_RATE)

    def add_client(self, client_handler, username):
        with self.lock:
            player = self.add_player(username)

            self.client_handlers.append(client_handler)

            client_handler.player = player
            client_handler.match = self

        client_handler.send({
            TYPE: MATCH_FOUND,
            PLAYER_ID: player.player_id,
        })

    def remove_client(self, client_handler):
        with self.lock:
            if client_handler in self.client_handlers:
                self.client_handlers.remove(client_handler)

            if client_handler.player is not None:
                self.players.pop(client_handler.player.player_id, None)

            client_handler.player = None
            client_handler.match = None


    def add_player(self, username):
        
        x, y = self.get_random_spawn(PLAYER_INITIAL_RADIUS)
        color = random.choice(ENTITIES_COLORS)

        player = Player(
            self.next_player_id,
            username,
            x,
            y,
            color
        )

        self.players[player.player_id] = player
        self.next_player_id += 1

        return player

    def get_random_spawn(self, radius):
        max_attempts = 100

        for _ in range(max_attempts):
            x = random.randint(radius, self.map_width - radius)
            y = random.randint(radius, self.map_height - radius)

            if self.is_valid_spawn(x, y, radius):
                return x, y

        return self.map_width // 2, self.map_height // 2

    def is_valid_spawn(self, x, y, radius):
        for player in self.players.values():
            distance = math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2)
            min_distance = radius + player.radius + 50

            if distance < min_distance:
                return False

        return True

    def update(self):
        with self.lock:
            for player in self.players.values():
                player.update()
                self.clamp_player(player)

    def send_snapshot(self):
        with self.lock:
            snapshot = self.generate_snapshot()
            client_handlers = list(self.client_handlers)

        message = {
            TYPE: GAME_STATE,
            TICK: self.tick,
            SNAPSHOT: snapshot,
        }
        print(message)
        for client_handler in client_handlers:
            client_handler.send(message)

    def clamp_player(self, player):
        player.x = max(
            player.radius,
            min(MAP_WIDTH - player.radius, player.x)
        )

        player.y = max(
            player.radius,
            min(MAP_HEIGHT - player.radius, player.y)
        )
    def generate_snapshot(self):
        return {
            "players": [
                player.to_snapshot()
                for player in self.players.values()
            ],
            "foods": [
                food.to_snapshot()
                for food in self.foods.values()
            ],
        }

    def stop(self):
        self.running = False

    
    def generate_initial_foods(self):
        for _ in range(FOOD_INITIAL_AMOUNT):
            self.add_food()


    def add_food(self):
        x = random.randint(0, self.map_width)
        y = random.randint(0, self.map_height)

        food_type = random.choice(FOOD_TYPES)
        color = random.choice(ENTITIES_COLORS)
        food = Food(
            food_id=self.next_food_id,
            x=x,
            y=y,
            radius=food_type[RADIUS],
            mass=food_type[MASS],
            color=color
        )

        self.foods[food.food_id] = food

        self.next_food_id += 1