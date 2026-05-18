import pygame

from client.states import ClientState
from client.ui import Button

from shared.protocol import (
    CELLS_EATEN,
    FOOD_EATEN,
    HIGHEST_MASS,
    TIME_ALIVE,
    TOP_POSITION,
    LEADERBOARD_TIME
)

from client.config.ui.respawn_config import *

class RespawnState(ClientState):
    def __init__(self, game, stats, playing_state):
        super().__init__(game)
        self.playing_state = playing_state
        self.stats = stats

        self.title_font = pygame.font.SysFont(
            None,
            RESPAWN_STATE_TITLE_FONT_SIZE
        )

        self.text_font = pygame.font.SysFont(
            None,
            RESPAWN_STATE_TEXT_FONT_SIZE
        )

        center_x = self.screen.get_width() // 2

        self.respawn_button = Button(
            rect=(
                center_x - RESPAWN_STATE_BUTTON_OFFSET_X,
                RESPAWN_STATE_RESPAWN_BUTTON_Y,
                RESPAWN_STATE_BUTTON_WIDTH,
                RESPAWN_STATE_BUTTON_HEIGHT
            ),
            text=RESPAWN_STATE_RESPAWN_BUTTON_TEXT,
            background_color=RESPAWN_STATE_RESPAWN_BUTTON_COLOR,
            hover_color=RESPAWN_STATE_RESPAWN_BUTTON_HOVER_COLOR,
        )

        self.back_button = Button(
            rect=(
                center_x - RESPAWN_STATE_BUTTON_OFFSET_X,
                RESPAWN_STATE_BACK_BUTTON_Y,
                RESPAWN_STATE_BUTTON_WIDTH,
                RESPAWN_STATE_BUTTON_HEIGHT
            ),
            text=RESPAWN_STATE_BACK_BUTTON_TEXT,
            background_color=RESPAWN_STATE_BACK_BUTTON_COLOR,
            hover_color=RESPAWN_STATE_BACK_BUTTON_HOVER_COLOR,
        )

    def handle_event(self, event):
        if isinstance(event, pygame.event.Event):
            if self.respawn_button.is_clicked(event):
                self.respawn()
            elif self.back_button.is_clicked(event):
                self.leave_game()
        else:
            super().handle_event(event)

    def respawn(self):
        from client.network import respawn
        self.game.client.send(respawn())
        self.game.change_state(self.playing_state)

    def leave_game(self):
        from client.states import MainMenuState
        self.game.client.disconnect()
        self.game.change_state(MainMenuState(self.game))

    def draw(self):
        
        self.playing_state.draw()

        overlay = pygame.Surface(self.screen.get_size())

        overlay.set_alpha(RESPAWN_STATE_OVERLAY_ALPHA)
        overlay.fill(RESPAWN_STATE_OVERLAY_COLOR)

        self.screen.blit(overlay, (0, 0))

        panel_x = (self.screen.get_width() - RESPAWN_STATE_PANEL_WIDTH) // 2

        panel_y = RESPAWN_STATE_PANEL_Y

        pygame.draw.rect(
            self.screen,
            RESPAWN_STATE_PANEL_COLOR,
            (
                panel_x,
                panel_y,
                RESPAWN_STATE_PANEL_WIDTH,
                RESPAWN_STATE_PANEL_HEIGHT
            ),
            border_radius=RESPAWN_STATE_PANEL_BORDER_RADIUS
        )

        title = self.title_font.render(RESPAWN_STATE_TITLE, True, RESPAWN_STATE_TITLE_COLOR)

        title_rect = title.get_rect(
            center=(
                self.screen.get_width() // 2,
                panel_y + RESPAWN_STATE_TITLE_OFFSET_Y
            )
        )

        self.screen.blit(title, title_rect)

        left_stats = [
            (RESPAWN_STATE_FOOD_EATEN_LABEL, self.stats[FOOD_EATEN]),
            (RESPAWN_STATE_TIME_ALIVE_LABEL, self.format_time(self.stats[TIME_ALIVE])),
            (RESPAWN_STATE_CELLS_EATEN_LABEL, self.stats[CELLS_EATEN]),
        ]
        right_stats = [
            (RESPAWN_STATE_HIGHEST_MASS_LABEL, int(self.stats[HIGHEST_MASS])),
            (RESPAWN_STATE_LEADERBOARD_TIME_LABEL, self.format_time(self.stats[LEADERBOARD_TIME])),
            (RESPAWN_STATE_TOP_POSITION_LABEL, self.stats[TOP_POSITION]),
        ]

        start_y = (panel_y + RESPAWN_STATE_STATS_START_Y)

        for index, (label, value) in enumerate(left_stats):
            y = (start_y + index * RESPAWN_STATE_STATS_LINE_SPACING)

            label_surface = self.text_font.render(label, True, RESPAWN_STATE_TEXT_COLOR)

            value_surface = self.text_font.render(str(value), True, RESPAWN_STATE_VALUE_COLOR)

            label_rect = label_surface.get_rect(center=(panel_x + RESPAWN_STATE_LEFT_COLUMN_X,y))

            value_rect = value_surface.get_rect(
                center=(
                    panel_x + RESPAWN_STATE_LEFT_COLUMN_X,
                    y + RESPAWN_STATE_VALUE_OFFSET_Y
                )
            )

            self.screen.blit(label_surface, label_rect)
            self.screen.blit(value_surface, value_rect)

        for index, (label, value) in enumerate(right_stats):
            y = (start_y + index * RESPAWN_STATE_STATS_LINE_SPACING)

            label_surface = self.text_font.render(label, True, RESPAWN_STATE_TEXT_COLOR)
            value_surface = self.text_font.render(str(value), True, RESPAWN_STATE_VALUE_COLOR)
            label_rect = label_surface.get_rect(center=(panel_x + RESPAWN_STATE_RIGHT_COLUMN_X, y))

            value_rect = value_surface.get_rect(
                center=(
                    panel_x + RESPAWN_STATE_RIGHT_COLUMN_X,
                    y + RESPAWN_STATE_VALUE_OFFSET_Y
                )
            )

            self.screen.blit(label_surface, label_rect)
            self.screen.blit(value_surface, value_rect)

        self.respawn_button.draw(self.screen)
        self.back_button.draw(self.screen)


    def format_time(self, seconds):
        seconds = int(seconds)

        minutes = seconds // 60
        seconds = seconds % 60

        return f"{minutes}:{seconds:02d}"

    def format_top_position(self, position):
        if position is None or position <= 0:
            return "00:00"

        return str(position)