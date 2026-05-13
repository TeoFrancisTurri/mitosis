import pygame

from client.states.client_state import ClientState
from client.managers.snapshot_manager import SnapshotManager

from shared.protocol.message_types import PLAYER_INPUT

from shared.protocol.message_fields import TYPE

from shared.protocol.input_fields import (
    DIRECTION_X,
    DIRECTION_Y,
)

from shared.protocol.snapshot_fields import (
    COLOR,
    PLAYERS,
    X,
    Y,
    RADIUS,
)


class PlayingState(ClientState):
    def __init__(self, game, player_id):
        super().__init__(game)
        self.player_id = player_id

    def update(self, dt):
        direction_x, direction_y = self.get_mouse_direction()

        self.game.client.send({
            TYPE: PLAYER_INPUT,
            DIRECTION_X: direction_x,
            DIRECTION_Y: direction_y,
        })

    def draw(self):
        self.screen.fill((230, 230, 230))

        snapshot = self.game.snapshot_manager.get_snapshot()

        if snapshot is None:
            return

        players = snapshot.get(PLAYERS, [])

        for player in players:
            x = int(player[X])
            y = int(player[Y])

            radius = int(player[RADIUS])
            color = tuple(player[COLOR])

            border_color = (
                max(0, color[0] - 40),
                max(0, color[1] - 40),
                max(0, color[2] - 40),
            )
            pygame.draw.circle(
                self.screen,
                border_color,
                (x, y),
                radius,
            )

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                radius - 3,
            )

    def get_mouse_direction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        center = pygame.math.Vector2(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
        )

        mouse = pygame.math.Vector2(mouse_x, mouse_y)

        direction = mouse - center

        if direction.length() > 0:
            direction = direction.normalize()

        return direction