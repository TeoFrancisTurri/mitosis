import pygame

from client.states import ClientState
from client.managers import SnapshotManager

from shared.config import MAP_WIDTH, MAP_HEIGHT
from shared.protocol import STATS, TYPE, PLAYER_DEAD
from client.config import (
    GRID_COLOR,
    GRID_SIZE,
    MAP_CLIP_EXTRA,
)
from client.network import player_input

from client.config.ui.playing_state_config import *

from shared.protocol import *


class PlayingState(ClientState):
    def __init__(self, game, player_id):
        super().__init__(game)
        self.player_id = player_id
        self.mass_font = pygame.font.SysFont(None, PLAYING_SCORE_FONT_SIZE)

        self.leaderboard_font = pygame.font.SysFont(None, PLAYING_LEADERBOARD_FONT_SIZE)

        self.username_font = pygame.font.SysFont(None, PLAYING_USERNAME_FONT_SIZE)

    def handle_event(self, event):
        if isinstance(event, pygame.event.Event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.leave_game()
        else:
            event_type = event.get(TYPE)

            if event_type == PLAYER_DEAD:
                from client.states import RespawnState
                stats = event.get(STATS)
                self.game.change_state(RespawnState(self.game, stats, self))
                return

            super().handle_event(event)
                
        
    def update(self, dt):
        direction_x, direction_y = self.get_mouse_direction()
        self.game.client.send(player_input(direction_x, direction_y))

    def draw(self):
        self.screen.fill(PLAYING_BACKGROUND_COLOR)

        snapshot = self.game.snapshot_manager.get_snapshot()

        if snapshot is None:
            return

        players = snapshot.get(PLAYERS)
        local_player = self.find_local_player(players)

        if local_player is None:
            return

        # Actualizar cámara siguiendo al jugador local
        self.game.camera.update(
            local_player[X],
            local_player[Y]
        )
            
        #bordes
        map_x, map_y = self.game.camera.apply(0, 0)

        map_rect = pygame.Rect(
            int(map_x) - MAP_CLIP_EXTRA,
            int(map_y) - MAP_CLIP_EXTRA,
            MAP_WIDTH + MAP_CLIP_EXTRA * 2,
            MAP_HEIGHT + MAP_CLIP_EXTRA * 2
        )

        self.screen.set_clip(map_rect)

        self.draw_grid()

        foods = snapshot.get(FOODS, [])
        self.draw_foods(foods, self.game.camera.x, self.game.camera.y)

        sorted_players = sorted(
            players,
            key=lambda player: player[RADIUS]
        )

        for player in sorted_players:
            world_x = player[X]
            world_y = player[Y]

            screen_x, screen_y = self.game.camera.apply(world_x, world_y)

            x = int(screen_x)
            y = int(screen_y)

            radius = int(player[RADIUS])
            color = tuple(player[COLOR])

            border_color = (
                max(0, color[0] - 40),
                max(0, color[1] - 40),
                max(0, color[2] - 40),
            )

            pygame.draw.circle(self.screen, border_color, (x, y), radius,)
            pygame.draw.circle(self.screen, color, (x, y), radius - 3,)

            self.draw_username(player[USERNAME], x, y)
        
        self.screen.set_clip(None)

        

        leaderboard = snapshot.get(LEADERBOARD, [])

        if local_player is not None:
            self.draw_score(local_player)
            self.draw_leaderboard(leaderboard, local_player)

    def leave_game(self):
        from client.states import MainMenuState
        self.game.client.disconnect()
        self.game.change_state(MainMenuState(self.game))

    def find_local_player(self, players):
        for player in players:
            if player[ID] == self.player_id:
                return player

        return None

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

            pygame.draw.circle(self.screen, food_color, (x, y), food_radius)

    def draw_grid(self):
        camera_x = int(self.game.camera.x)
        camera_y = int(self.game.camera.y)

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        visible_start_x = max(0, camera_x)
        visible_end_x = min(MAP_WIDTH, camera_x + screen_width)

        visible_start_y = max(0, camera_y)
        visible_end_y = min(MAP_HEIGHT, camera_y + screen_height)

        first_grid_x = (visible_start_x // GRID_SIZE) * GRID_SIZE
        first_grid_y = (visible_start_y // GRID_SIZE) * GRID_SIZE

        for world_x in range(first_grid_x, visible_end_x + 1, GRID_SIZE):
            screen_x = world_x - camera_x

            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (screen_x, visible_start_y - camera_y),
                (screen_x, visible_end_y - camera_y),
            )

        for world_y in range(first_grid_y, visible_end_y + 1, GRID_SIZE):
            screen_y = world_y - camera_y

            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (visible_start_x - camera_x, screen_y),
                (visible_end_x - camera_x, screen_y),
            )

    def draw_score(self, player):
        mass = int(player.get(MASS))

        text = self.mass_font.render(
            f"Score: {mass}",
            True,
            SCORE_TEXT_COLOR
        )

        x = SCORE_MARGIN_LEFT
        y = self.screen.get_height() - text.get_height() - SCORE_MARGIN_BOTTOM

        self.screen.blit(text, (x, y))


    def draw_leaderboard(self, leaderboard, local_player):

        x = self.screen.get_width() - LEADERBOARD_WIDTH - LEADERBOARD_MARGIN_RIGHT
        y = LEADERBOARD_MARGIN_TOP

        background = pygame.Surface((LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT))
        background.set_alpha(LEADERBOARD_BACKGROUND_ALPHA)
        background.fill(LEADERBOARD_BACKGROUND_COLOR)

        self.screen.blit(background, (x, y))

        title = self.leaderboard_font.render(LEADERBOARD_TITLE, True, LEADERBOARD_TEXT_COLOR)

        self.screen.blit(title, (x + LEADERBOARD_TITLE_OFFSET_X, y + LEADERBOARD_TITLE_OFFSET_Y))

        local_player_was_drawn = False

        for index, player in enumerate(leaderboard):
            username = player.get(USERNAME)

            is_local_player = (player[ID] == local_player[ID])
            
            if is_local_player:
                local_player_was_drawn = True

            color = (LEADERBOARD_LOCAL_PLAYER_COLOR if is_local_player else LEADERBOARD_TEXT_COLOR)

            text = self.leaderboard_font.render(f"{index + 1}. {username}", True, color)

            self.screen.blit(
                text,
                (
                    x + LEADERBOARD_ENTRY_OFFSET_X,
                    y + LEADERBOARD_ENTRY_OFFSET_Y
                    + index * LEADERBOARD_LINE_HEIGHT
                )
            )

        if not local_player_was_drawn:
            position = local_player.get(POSITION)
            username = local_player.get(USERNAME)

            text = self.leaderboard_font.render(
                f"{position}. {username}",
                True,
                LEADERBOARD_LOCAL_PLAYER_COLOR
            )

            local_player_y = (
                y + LEADERBOARD_ENTRY_OFFSET_Y
                + len(leaderboard) * LEADERBOARD_LINE_HEIGHT
            )

            self.screen.blit(
                text,
                (
                    x + LEADERBOARD_ENTRY_OFFSET_X,
                    local_player_y
                )
            )
        

    def draw_username(self, username, x, y):
        text = self.username_font.render(username, True, USERNAME_TEXT_COLOR)

        text_x = x - text.get_width() // 2
        text_y = y - text.get_height() // 2

        self.screen.blit(text, (text_x, text_y))