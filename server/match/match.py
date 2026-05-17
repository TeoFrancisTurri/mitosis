import random
import math
import threading
import time


from server.config import MATCH_TICK_RATE, message_game_state, message_match_found, message_player_dead, message_disconnected
from server.managers import (
    CollisionManager,
    LeaderboardManager,
    PlayerManager,
    FoodManager
)


from shared.config import (MAP_HEIGHT, MAP_WIDTH)
from shared.protocol import (MATCH_FOUND, GAME_STATE, TYPE, SNAPSHOT, TICK, FOODS, LEADERBOARD, PLAYERS)



class Match:
    def __init__(self, match_id):
        self.match_id = match_id

        self.client_handlers = []
        self.players = {}
        self.foods = {}

        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT

        self.tick = 0

        self.player_manager = PlayerManager(self)
        self.collision_manager = CollisionManager(self)
        self.leaderboard_manager = LeaderboardManager(self)
        self.food_manager = FoodManager(self)

        self.food_manager.generate_initial_foods()

        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        last_time = time.monotonic()
        
        while self.running:
            current_time = time.monotonic()
            delta_time = current_time - last_time
            last_time = current_time

            self.tick += 1

            self.update(delta_time)
            self.send_snapshot()

            time.sleep(1 / MATCH_TICK_RATE)

    def update(self, delta_time): 
        self.player_manager.update(delta_time)
        self.collision_manager.update()
        self.leaderboard_manager.update(delta_time)
            
    
    def add_client(self, client_handler, username):
       
        player = self.player_manager.add_player(username)

        with self.lock:
            self.client_handlers.append(client_handler)

            client_handler.player = player
            client_handler.match = self
        
        client_handler.send(message_match_found(player.player_id))

    def remove_client(self, client_handler):
        with self.lock:
            if client_handler in self.client_handlers:
                self.client_handlers.remove(client_handler)

            client_handler.player = None
            client_handler.match = None


    def send_snapshot(self):
        with self.lock:
            snapshot = self.generate_snapshot()
            client_handlers = list(self.client_handlers)
            tick = self.tick

        self.broadcast(message_game_state(snapshot, tick))

        
    def broadcast(self, message):
        for client_handler in self.client_handlers:
            client_handler.send(message)


    def generate_snapshot(self):
        return {
            PLAYERS: self.player_manager.to_snapshot(),
            FOODS: self.food_manager.to_snapshot(),
            LEADERBOARD: self.leaderboard_manager.to_snapshot(),
        }

    def player_dead(self, player):
        with self.lock:
            removed_player = self.player_manager.remove_player(player)

        if removed_player is None:
            return


        dead_client_handler = self.find_client_handler_by_player(removed_player)

        if dead_client_handler is not None:
            dead_client_handler.send(
                message_player_dead(removed_player)
            )

        print(
            f"Jugador muerto: {player.username} "
            f"({player.player_id})"
        )

    def find_client_handler_by_player(self, player):
        for client_handler in self.client_handlers:
            if client_handler.player == player:
                return client_handler

        return None

    def respawn_player(self, player):
        with self.lock:
            self.player_manager.respawn_player(player)

    def stop(self):
        self.running = False
