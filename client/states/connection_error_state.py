import pygame

from client.states.client_state import ClientState
from client.ui.button import Button


class ConnectionErrorState(ClientState):
    def __init__(self, game, message):
        super().__init__(game)

        self.message = message

        self.title_font = pygame.font.SysFont(None, 56)
        self.message_font = pygame.font.SysFont(None, 32)

        center_x = self.screen.get_width() // 2

        self.back_button = Button(
            rect=(center_x - 100, 360, 200, 60),
            text="Back",
            background_color=(80, 160, 255),
            hover_color=(100, 180, 255),
        )

    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            self.go_back()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.go_back()

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((30, 30, 30))

        title = self.title_font.render(
            "Connection Error",
            True,
            (255, 80, 80),
        )

        title_rect = title.get_rect(
            center=(
                self.screen.get_width() // 2,
                180,
            )
        )

        self.screen.blit(title, title_rect)

        message = self.message_font.render(
            self.message,
            True,
            (220, 220, 220),
        )

        message_rect = message.get_rect(
            center=(
                self.screen.get_width() // 2,
                250,
            )
        )

        self.screen.blit(message, message_rect)

        self.back_button.draw(
            self.screen
        )

    def go_back(self):
        from client.states.main_menu_state import MainMenuState

        self.game.change_state(
            MainMenuState(self.game)
        )