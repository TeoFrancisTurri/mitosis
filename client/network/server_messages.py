from shared.protocol import (
    TYPE,
    USERNAME,
    DIRECTION_X,
    DIRECTION_Y,
    CONNECT,
    PLAYER_INPUT,
    RESPAWN,
    SPLIT,
    EJECT,
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


def split():
    return {
        TYPE: SPLIT,
    }


def eject():
    return {
        TYPE: EJECT,
    }


def disconnect():
    return {
        TYPE: DISCONNECT,
    }