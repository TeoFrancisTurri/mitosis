from shared.protocol import (
    TYPE,
    USERNAME,
    DIRECTION_X,
    DIRECTION_Y,
    CONNECT,
    PLAYER_INPUT,
    RESPAWN,
    DISCONNECT,
)


def connect(username):
    return {
        TYPE: CONNECT,
        USERNAME: username,
    }


def player_input(direction_x, direction_y):
    return {
        TYPE: PLAYER_INPUT,
        DIRECTION_X: direction_x,
        DIRECTION_Y: direction_y,
    }


def respawn():
    return {
        TYPE: RESPAWN,
    }


def disconnect():
    return {
        TYPE: DISCONNECT,
    }