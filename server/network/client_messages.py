from shared.protocol import (
    MATCH_FOUND, GAME_STATE, DISCONNECT, PLAYER_DEAD, TYPE, PLAYER_ID, SNAPSHOT, TICK, STATS
)


def message_match_found(player_id=0):
    return {
        TYPE: MATCH_FOUND,
        PLAYER_ID: player_id,
    }


def message_game_state(snapshot, tick):
    return {
        TYPE: GAME_STATE,
        SNAPSHOT: snapshot,
        TICK: tick,
    }

def message_player_dead(player):
    return{
        TYPE: PLAYER_DEAD,
        STATS: player.stats_to_snapshot(),
    }

def message_disconnected():
    return {
        TYPE: DISCONNECT,
    }