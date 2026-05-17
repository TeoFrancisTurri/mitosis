# server/config/__init__.py
from .messages import message_match_found, message_game_state, message_disconnected, message_player_dead
from .match_config import MATCH_TICK_RATE, TOP_PLAYERS_LEADERBOARD, PLAYER_EAT_MASS_MULTIPLIER
from .player_config import (
    PLAYER_INITIAL_MASS, PLAYER_DEFAULT_USERNAME, ATTEMPS_TO_SPAWN,
    PLAYER_MAX_SPEED, PLAYER_MIN_SPEED, PLAYER_SPEED_FACTOR,
)
from .food_config import FOOD_INITIAL_AMOUNT, FOOD_TYPES, RADIUS, MASS