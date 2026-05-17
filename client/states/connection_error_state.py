import pygame

from client.states import ClientState
from client.ui import Button

from client.config.ui.connection_error_config import *

class ConnectionErrorState(ClientState):
    def __init__(self, game, message):
        super().__init__(game)

        self.message = message

        self.title_font = pygame.font.SysFont(None, CONNECTION_ERROR_TITLE_FONT_SIZE)
        self.message_font = pygame.font.SysFont(None, CONNECTION_ERROR_MESSAGE_FONT_SIZE)

        center_x = self.screen.get_width() // 2

        self.back_button = Button(
            rect=(
                center_x - CONNECTION_ERROR_BACK_BUTTON_WIDTH // 2,
                CONNECTION_ERROR_BACK_BUTTON_Y,
                CONNECTION_ERROR_BACK_BUTTON_WIDTH,
                CONNECTION_ERROR_BACK_BUTTON_HEIGHT,
            ),
            text=CONNECTION_ERROR_BACK_BUTTON_TEXT,
            background_color=CONNECTION_ERROR_BACK_BUTTON_BACKGROUND_COLOR,
            hover_color=CONNECTION_ERROR_BACK_BUTTON_HOVER_COLOR,
        )

    def handle_event(self, event):

        if isinstance(event, pygame.event.Event):
            if self.back_button.is_clicked(event):
                self.go_back()


    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(
            CONNECTION_ERROR_BACKGROUND_COLOR
        )

        title = self.title_font.render(
            CONNECTION_ERROR_TITLE,
            True,
            CONNECTION_ERROR_TITLE_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                self.screen.get_width() // 2,
                CONNECTION_ERROR_TITLE_Y,
            )
        )

        self.screen.blit(title, title_rect)

        message = self.message_font.render(
            self.message,
            True,
            CONNECTION_ERROR_MESSAGE_COLOR,
        )

        message_rect = message.get_rect(
            center=(
                self.screen.get_width() // 2,
                CONNECTION_ERROR_MESSAGE_Y,
            )
        )

        self.screen.blit(message, message_rect)

        self.back_button.draw(self.screen)

    def go_back(self):
        from client.states.main_menu_state import MainMenuState

        self.game.change_state(MainMenuState(self.game))