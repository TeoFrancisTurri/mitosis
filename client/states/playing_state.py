import pygame

from client.states.client_state import ClientState
from client.managers.snapshot_manager import SnapshotManager

from shared.config.world_config import MAP_WIDTH, MAP_HEIGHT
from shared.protocol.message_types import PLAYER_INPUT
from client.config.map_config import GRID_COLOR, GRID_SIZE

from shared.protocol.message_fields import TYPE

from shared.protocol.input_fields import (
    DIRECTION_X,
    DIRECTION_Y,
)

from shared.protocol.snapshot_fields import (
    COLOR,
    PLAYERS,
    USERNAME,
    FOODS,
    X,
    Y,
    RADIUS,
    ID,
    MASS
)


class PlayingState(ClientState):
    def __init__(self, game, player_id):
        super().__init__(game)
        self.player_id = player_id
        self.mass_font = pygame.font.SysFont(None, 32)
        self.leaderboard_font = pygame.font.SysFont(None, 26)
        self.username_font = pygame.font.SysFont(None, 24)

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
        local_player = None

        # Actualizar cámara siguiendo al jugador local
        for player in players:
            if player[ID] == self.player_id:
                local_player = player
                self.game.camera.update(
                    player[X],
                    player[Y]
                )
                break

        self.draw_grid()
        
        for player in players:
            world_x = player[X]
            world_y = player[Y]

            screen_x, screen_y = self.game.camera.apply(
                world_x,
                world_y
            )

            x = int(screen_x)
            y = int(screen_y)

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
        
        foods = snapshot.get(FOODS, [])
        self.draw_foods(foods, self.game.camera.x, self.game.camera.y)

        if local_player is not None:
            self.draw_score(local_player)
            self.draw_leaderboard(players, local_player)

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
    
    def draw_foods(self, foods, camera_x, camera_y):
        for food in foods:
            food_x = food[X]
            food_y = food[Y]

            food_radius = food[RADIUS]
            food_color = food[COLOR]

            x = int(food_x - camera_x)
            y = int(food_y - camera_y)

            pygame.draw.circle(
                self.screen,
                food_color,
                (x, y),
                food_radius
            )

    def draw_grid(self):
        grid_size = GRID_SIZE
        grid_color = GRID_COLOR

        camera_x = int(self.game.camera.x)
        camera_y = int(self.game.camera.y)

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        visible_start_x = max(0, camera_x)
        visible_end_x = min(MAP_WIDTH, camera_x + screen_width)

        visible_start_y = max(0, camera_y)
        visible_end_y = min(MAP_HEIGHT, camera_y + screen_height)

        first_grid_x = (visible_start_x // grid_size) * grid_size
        first_grid_y = (visible_start_y // grid_size) * grid_size

        for world_x in range(first_grid_x, visible_end_x + 1, grid_size):
            screen_x = world_x - camera_x

            pygame.draw.line(
                self.screen,
                grid_color,
                (screen_x, visible_start_y - camera_y),
                (screen_x, visible_end_y - camera_y),
            )

        for world_y in range(first_grid_y, visible_end_y + 1, grid_size):
            screen_y = world_y - camera_y

            pygame.draw.line(
                self.screen,
                grid_color,
                (visible_start_x - camera_x, screen_y),
                (visible_end_x - camera_x, screen_y),
            )

    def draw_score(self, player):
        mass = int(player.get(MASS, 0))

        text = self.mass_font.render(
            f"Score: {mass}",
            True,
            (40, 40, 40)
        )

        x = 20
        y = self.screen.get_height() - text.get_height() - 20

        self.screen.blit(text, (x, y))


    def draw_leaderboard(self, players, local_player):
        sorted_players = sorted(
            players,
            key=lambda player: player.get(MASS, 0),
            reverse=True
        )

        x = self.screen.get_width() - 240
        y = 20

        width = 220
        height = 180

        background = pygame.Surface((width, height))
        background.set_alpha(160)

        background.fill((45, 45, 45))

        self.screen.blit(background, (x, y))

        title = self.leaderboard_font.render(
            "Leaderboard",
            True,
            (255, 255, 255)
        )

        self.screen.blit(title, (x + 15, y + 10))

        line_height = 26

        for index, player in enumerate(sorted_players[:5]):
            username = player.get(USERNAME, "Player")

            is_local_player = (
                player[ID] == local_player[ID]
            )

            color = (
                (255, 120, 120)
                if is_local_player
                else (255, 255, 255)
            )

            text = self.leaderboard_font.render(
                f"{index + 1}. {username}",
                True,
                color
            )

            self.screen.blit(
                text,
                (
                    x + 15,
                    y + 45 + index * line_height
                )
            )