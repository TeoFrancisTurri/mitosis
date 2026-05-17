import pygame

from client.config.ui.main_menu_config import *

from client.states import ClientState, MatchmakingState

from client.config import DEFAULT_USERNAME, WINDOW_TITLE
from client.ui import Button, TextInput

class MainMenuState(ClientState):
    def __init__(self, game):
        super().__init__(game)

        center_x = self.screen.get_width() // 2

        self.title_font = pygame.font.SysFont(
            None,
            MAIN_MENU_TITLE_FONT_SIZE
        )

        self.username_input = TextInput(
            rect=(
                center_x - MAIN_MENU_USERNAME_INPUT_WIDTH // 2,
                MAIN_MENU_USERNAME_INPUT_Y,
                MAIN_MENU_USERNAME_INPUT_WIDTH,
                MAIN_MENU_USERNAME_INPUT_HEIGHT,
            ),
            placeholder=MAIN_MENU_USERNAME_PLACEHOLDER,
        )

        self.play_button = Button(
            rect=(
                center_x - MAIN_MENU_BUTTON_WIDTH // 2,
                MAIN_MENU_PLAY_BUTTON_Y,
                MAIN_MENU_BUTTON_WIDTH,
                MAIN_MENU_BUTTON_HEIGHT,
            ),
            text=MAIN_MENU_PLAY_BUTTON_TEXT,
            background_color=MAIN_MENU_PLAY_BUTTON_COLOR,
            hover_color=MAIN_MENU_PLAY_BUTTON_HOVER_COLOR,
        )

        self.exit_button = Button(
            rect=(
                center_x - MAIN_MENU_BUTTON_WIDTH // 2,
                MAIN_MENU_EXIT_BUTTON_Y,
                MAIN_MENU_BUTTON_WIDTH,
                MAIN_MENU_BUTTON_HEIGHT,
            ),
            text=MAIN_MENU_EXIT_BUTTON_TEXT,
            background_color=MAIN_MENU_EXIT_BUTTON_COLOR,
            hover_color=MAIN_MENU_EXIT_BUTTON_HOVER_COLOR,
        )

    def handle_event(self, event):
        if not isinstance(event, pygame.event.Event):
            return
        
        self.username_input.handle_event(event)

        if self.play_button.is_clicked(event):
            username = self.username_input.text.strip()

            if username == "":
                username = DEFAULT_USERNAME

            self.game.username = username
            self.game.change_state(MatchmakingState(self.game, username))

        elif self.exit_button.is_clicked(event):
            self.game.running = False

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(MAIN_MENU_BACKGROUND_COLOR)

        title_surface = self.title_font.render(WINDOW_TITLE, True, MAIN_MENU_TITLE_FONT_SIZE)

        title_rect = title_surface.get_rect(
            center=(self.screen.get_width() // 2, MAIN_MENU_TITLE_Y)
        )

        self.screen.blit(title_surface, title_rect)

        self.username_input.draw(self.screen)
        self.play_button.draw(self.screen)
        self.exit_button.draw(self.screen)