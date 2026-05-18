import math
import random

from server.entities import Virus
from server.config import VIRUS_INITIAL_AMOUNT, VIRUS_MAX_AMOUNT, VIRUS_INITIAL_MASS, VIRUS_SPLIT_MASS, VIRUS_EJECT_SPEED, EJECT_FRICTION, VIRUS_SPAWN_ATTEMPTS, VIRUS_SAFE_DISTANCE


class VirusManager:
    def __init__(self, match):
        self.match = match
        self.next_virus_id = 1

    def generate_initial_viruses(self):
        for _ in range(VIRUS_INITIAL_AMOUNT):
            self.add_virus()

    def add_virus(self, x=None, y=None, vx=0.0, vy=0.0):
        if x is None or y is None:
            x, y = self.get_random_spawn()
        virus = Virus(self.next_virus_id, x, y)
        virus.vx = vx
        virus.vy = vy
        self.match.viruses[virus.virus_id] = virus
        self.next_virus_id += 1
        return virus

    def get_random_spawn(self):
        for _ in range(VIRUS_SPAWN_ATTEMPTS):
            x = random.randint(50, self.match.map_width - 50)
            y = random.randint(50, self.match.map_height - 50)
            if self.is_valid_spawn(x, y):
                return x, y
        return random.randint(50, self.match.map_width - 50), random.randint(50, self.match.map_height - 50)

    def is_valid_spawn(self, x, y):
        for player in self.match.players.values():
            distance = math.hypot(x - player.x, y - player.y)
            if distance < player.radius + VIRUS_SAFE_DISTANCE:
                return False
        return True

    def respawn_virus(self):
        if len(self.match.viruses) < VIRUS_MAX_AMOUNT:
            self.add_virus()

    def feed_virus(self, virus, direction_x, direction_y, mass):
        virus.add_mass(mass, direction_x, direction_y)
        if virus.mass >= VIRUS_SPLIT_MASS:
            self._eject_virus(virus)

    def _eject_virus(self, virus):
        self.add_virus(
            x=virus.x,
            y=virus.y,
            vx=virus.last_feed_dx * VIRUS_EJECT_SPEED,
            vy=virus.last_feed_dy * VIRUS_EJECT_SPEED,
        )
        virus.reset()

    def update(self, delta_time):
        for virus in list(self.match.viruses.values()):
            if virus.vx == 0.0 and virus.vy == 0.0:
                continue
            virus.x += virus.vx * delta_time
            virus.y += virus.vy * delta_time
            decay = 1 - EJECT_FRICTION * delta_time
            virus.vx *= decay
            virus.vy *= decay
            if abs(virus.vx) < 1 and abs(virus.vy) < 1:
                virus.vx = 0.0
                virus.vy = 0.0
            virus.x = max(0, min(virus.x, self.match.map_width))
            virus.y = max(0, min(virus.y, self.match.map_height))

    def to_snapshot(self):
        return [v.to_snapshot() for v in self.match.viruses.values()]
