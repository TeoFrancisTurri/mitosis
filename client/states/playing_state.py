import math
import pygame

from client.states import ClientState

from shared.config import MAP_WIDTH, MAP_HEIGHT
from shared.protocol import STATS, TYPE, PLAYER_DEAD
from client.config import (
    GRID_COLOR,
    GRID_SIZE,
    MAP_CLIP_EXTRA,
)
from client.network import player_input

from client.config.ui.playing_state_config import *
from client.config.ui.leaderboard_config import *

from shared.protocol import *


class PlayingState(ClientState):
    def __init__(self, game, player_id):
        super().__init__(game)
        self.player_id = player_id
        self.last_dt = 0
        self.mass_font = pygame.font.SysFont(None, PLAYING_SCORE_FONT_SIZE)

        self.leaderboard_font = pygame.font.SysFont(None, PLAYING_LEADERBOARD_FONT_SIZE)

        self.username_font = pygame.font.SysFont(None, PLAYING_USERNAME_FONT_SIZE)

    def handle_event(self, event):
        if isinstance(event, pygame.event.Event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_game()
                elif event.key == pygame.K_SPACE:
                    from client.network import split
                    self.game.client.send(split())
                elif event.key == pygame.K_w:
                    from client.network import eject
                    self.game.client.send(eject())
        else:
            event_type = event.get(TYPE)

            if event_type == PLAYER_DEAD:
                from client.states import RespawnState
                stats = event.get(STATS)
                self.game.change_state(RespawnState(self.game, stats, self))
                return

            super().handle_event(event)
                
        
    def update(self, dt):
        self.last_dt = dt / 1000
        direction_x, direction_y = self.get_mouse_direction()
        self.game.client.send(player_input(direction_x, direction_y))

    def draw(self):
        self.screen.fill(PLAYING_BACKGROUND_COLOR)

        snapshot = self.game.snapshot_manager.get_snapshot()

        if snapshot is None:
            return

        players = snapshot.get(PLAYERS)
        local_cells = self.find_local_cells(players)

        if not local_cells:
            return

        centroid_x = sum(c[X] for c in local_cells) / len(local_cells)
        centroid_y = sum(c[Y] for c in local_cells) / len(local_cells)

        total_mass = sum(c[MASS] for c in local_cells)
        self.game.camera.update(centroid_x, centroid_y, len(local_cells), total_mass, self.last_dt)

        local_player = local_cells[0]

        map_x, map_y = self.game.camera.apply(0, 0)
        map_end_x, map_end_y = self.game.camera.apply(MAP_WIDTH, MAP_HEIGHT)

        map_rect = pygame.Rect(
            int(map_x) - MAP_CLIP_EXTRA,
            int(map_y) - MAP_CLIP_EXTRA,
            int(map_end_x - map_x) + MAP_CLIP_EXTRA * 2,
            int(map_end_y - map_y) + MAP_CLIP_EXTRA * 2
        )

        self.screen.set_clip(map_rect)

        self.draw_grid()

        foods = snapshot.get(FOODS, [])
        self.draw_foods(foods)

        viruses = snapshot.get(VIRUSES, [])

        tagged_players = [(ENTITY_PLAYER, p) for p in players]
        tagged_viruses = [(ENTITY_VIRUS, v) for v in viruses]

        sorted_entities = sorted(
            tagged_players + tagged_viruses,
            key=self.get_entity_radius
        )

        for kind, entity in sorted_entities:
            world_x = entity[X]
            world_y = entity[Y]
            screen_x, screen_y = self.game.camera.apply(world_x, world_y)
            x = int(screen_x)
            y = int(screen_y)
            radius = max(1, int(self.game.camera.scale(entity[RADIUS])))
            color = tuple(entity[COLOR])

            if kind == ENTITY_VIRUS:
                self.draw_virus(x, y, radius, color)
            else:
                self.draw_player(entity, x, y, radius, color)
        
        self.screen.set_clip(None)

        

        leaderboard = snapshot.get(LEADERBOARD, [])

        self.draw_score(sum(c[MASS] for c in local_cells))
        self.draw_leaderboard(leaderboard, local_player)

    def leave_game(self):
        from client.states import MainMenuState
        self.game.client.disconnect()
        self.game.change_state(MainMenuState(self.game))

    def find_local_cells(self, players):
        return [p for p in players if p[ID] == self.player_id]

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
    
    def get_entity_radius(self, kind_entity):
        _, entity = kind_entity
        return entity[RADIUS]

    def draw_foods(self, foods):
        camera = self.game.camera
        for food in foods:
            x, y = camera.apply(food[X], food[Y])
            radius = max(1, int(camera.scale(food[RADIUS])))
            pygame.draw.circle(self.screen, food[COLOR], (int(x), int(y)), radius)

    def draw_player(self, player, x, y, radius, color):
        border_color = (
            max(0, color[0] - PLAYING_PLAYER_BORDER_DARKEN_AMOUNT),
            max(0, color[1] - PLAYING_PLAYER_BORDER_DARKEN_AMOUNT),
            max(0, color[2] - PLAYING_PLAYER_BORDER_DARKEN_AMOUNT),
        )
        pygame.draw.circle(self.screen, border_color, (x, y), radius)
        pygame.draw.circle(self.screen, color, (x, y), max(0, radius - PLAYING_PLAYER_INNER_RADIUS_OFFSET))
        self.draw_username(player[USERNAME], x, y)

    def draw_virus(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)
        spike_length = max(1, int(self.game.camera.scale(PLAYING_VIRUS_SPIKE_LENGTH)))
        for i in range(PLAYING_VIRUS_SPIKE_COUNT):
            angle = (2 * math.pi / PLAYING_VIRUS_SPIKE_COUNT) * i
            tip_x = x + (radius + spike_length) * math.cos(angle)
            tip_y = y + (radius + spike_length) * math.sin(angle)
            left_x = x + radius * math.cos(angle - 0.25)
            left_y = y + radius * math.sin(angle - 0.25)
            right_x = x + radius * math.cos(angle + 0.25)
            right_y = y + radius * math.sin(angle + 0.25)
            pygame.draw.polygon(self.screen, color, [
                (int(tip_x), int(tip_y)),
                (int(left_x), int(left_y)),
                (int(right_x), int(right_y)),
            ])

    def draw_grid(self):
        camera = self.game.camera

        world_half_w = self.screen.get_width() / (2 * camera.zoom)
        world_half_h = self.screen.get_height() / (2 * camera.zoom)
        center_wx = camera.x + camera.half_screen_width
        center_wy = camera.y + camera.half_screen_height

        visible_start_x = max(0, center_wx - world_half_w)
        visible_end_x = min(MAP_WIDTH, center_wx + world_half_w)
        visible_start_y = max(0, center_wy - world_half_h)
        visible_end_y = min(MAP_HEIGHT, center_wy + world_half_h)

        first_grid_x = (int(visible_start_x) // GRID_SIZE) * GRID_SIZE
        first_grid_y = (int(visible_start_y) // GRID_SIZE) * GRID_SIZE

        for world_x in range(first_grid_x, int(visible_end_x) + 1, GRID_SIZE):
            sx, sy1 = camera.apply(world_x, visible_start_y)
            _, sy2 = camera.apply(world_x, visible_end_y)
            pygame.draw.line(self.screen, GRID_COLOR, (sx, sy1), (sx, sy2))

        for world_y in range(first_grid_y, int(visible_end_y) + 1, GRID_SIZE):
            sx1, sy = camera.apply(visible_start_x, world_y)
            sx2, _ = camera.apply(visible_end_x, world_y)
            pygame.draw.line(self.screen, GRID_COLOR, (sx1, sy), (sx2, sy))

    def draw_score(self, mass):
        mass = int(mass)

        text = self.mass_font.render(
            f"Score: {mass}",
            True,
            PLAYING_SCORE_TEXT_COLOR
        )

        x = PLAYING_SCORE_MARGIN_LEFT
        y = self.screen.get_height() - text.get_height() - PLAYING_SCORE_MARGIN_BOTTOM

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
        text = self.username_font.render(username, True, PLAYING_USERNAME_TEXT_COLOR)

        text_x = x - text.get_width() // 2
        text_y = y - text.get_height() // 2

        self.screen.blit(text, (text_x, text_y))