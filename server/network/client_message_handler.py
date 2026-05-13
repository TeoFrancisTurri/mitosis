from shared.protocol.message_types import (
    CONNECT,
    PLAYER_INPUT,
    DISCONNECT,
)

from shared.protocol.message_fields import (
    TYPE,
    USERNAME,
)

from server.config.player_config import (
    PLAYER_DEFAULT_USERNAME
)


class ClientMessageHandler:
    def __init__(self, client_handler):
        self.client_handler = client_handler

        self.handlers = {
            CONNECT: self.handle_join,
            PLAYER_INPUT: self.handle_player_input,
            DISCONNECT: self.handle_disconnect,
        }

    def handle(self, message):
        message_type = message.get(TYPE)

        handler = self.handlers.get(message_type)

        if handler is not None:
            handler(message)

    def handle_join(self, message):
        username = message.get(USERNAME)

        if username is None or username.strip() == "":
            username = PLAYER_DEFAULT_USERNAME

        self.client_handler.match_manager.add_client(
            self.client_handler,
            username
        )

    def handle_player_input(self, message):
        player = self.client_handler.player

        if player is None:
            return

        player.update_input(message)

    def handle_disconnect(self, message):
        self.client_handler.disconnect()