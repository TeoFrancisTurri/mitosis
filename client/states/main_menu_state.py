import pygame

from client.states.client_state import ClientState
from client.states.matchmaking_state import MatchmakingState

from client.config.client_settings import DEFAULT_USERNAME, WINDOW_TITLE
from client.ui.button import Button
from client.ui.text_input import TextInput


class MainMenuState(ClientState):
    def __init__(self, game):
        super().__init__(game)

        center_x = self.screen.get_width() // 2

        self.title_font = pygame.font.SysFont(None, 72)

        self.username_input = TextInput(
            rect=(center_x - 150, 220, 300, 50),
            placeholder="Username",
        )

        self.play_button = Button(
            rect=(center_x - 100, 310, 200, 60),
            text="Play",
            background_color=(80, 160, 255),
            hover_color=(110, 180, 255),
        )

        self.exit_button = Button(
            rect=(center_x - 100, 390, 200, 60),
            text="Exit",
            background_color=(200, 80, 80),
            hover_color=(220, 100, 100),
        )

    def handle_event(self, event):
        self.username_input.handle_event(event)

        if self.play_button.is_clicked(event):
            username = self.username_input.text.strip()

            if username == "":
                username = DEFAULT_USERNAME

            self.game.username = username

            self.game.change_state(MatchmakingState(self.game, username))

        if self.exit_button.is_clicked(event):
            self.game.running = False

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((245, 245, 245))

        title_surface = self.title_font.render(
            WINDOW_TITLE,
            True,
            (30, 30, 30)
        )

        title_rect = title_surface.get_rect(
            center=(self.screen.get_width() // 2, 130)
        )

        self.screen.blit(title_surface, title_rect)

        self.username_input.draw(self.screen)
        self.play_button.draw(self.screen)
        self.exit_button.draw(self.screen)