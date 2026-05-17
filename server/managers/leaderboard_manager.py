import threading
from server.config import TOP_PLAYERS_LEADERBOARD
from shared.protocol import USERNAME, ID, POSITION


class LeaderboardManager:
    def __init__(self, match):
        self.match = match
        self.entries = []
        self.lock = threading.Lock()

    def update(self, delta_time):
        sorted_players = self.get_players_sorted_by_mass()

        self.entries = []

        for position, player in enumerate(sorted_players, start=1):
            player.update_leaderboard_stats(position, delta_time)
            self.entries.append(self.build_entry(player, position))

    def get_players_sorted_by_mass(self):
        with self.match.lock:
            players = list(self.match.players.values())

        return sorted(
            players,
            key=lambda player: player.mass,
            reverse=True
        )

    def build_entry(self, player, position):
        return {
            POSITION: position,
            ID: player.player_id,
            USERNAME: player.username
        }

    def to_snapshot(self):
        return self.entries[:TOP_PLAYERS_LEADERBOARD]