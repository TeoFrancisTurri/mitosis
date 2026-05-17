import pygame

from shared.protocol import TYPE, DISCONNECT, MESSAGE
from client.config.ui.connection_error_config import CONNECTION_ERROR_DEFAULT_MESSAGE

class ClientState:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        if not isinstance(event, pygame.event.Event):
            if event.get(TYPE) == DISCONNECT:
                self.handle_server_disconnect(event)

    def handle_server_disconnect(self, event):
        from client.states.connection_error_state import ConnectionErrorState
        self.game.client.disconnect(notify_server=False)
        self.game.change_state(ConnectionErrorState(self.game, CONNECTION_ERROR_DEFAULT_MESSAGE))

    def update(self, dt):
        pass

    def draw(self):
        pass
