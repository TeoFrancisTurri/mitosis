from shared.protocol import CONNECT, PLAYER_INPUT, DISCONNECT, RESPAWN, SPLIT, EJECT, TYPE, USERNAME


class ServerMessageHandler:
    def __init__(self, client_handler):
        self.client_handler = client_handler

        self.handlers = {
            CONNECT: self.handle_connect,
            PLAYER_INPUT: self.handle_player_input,
            DISCONNECT: self.handle_disconnect,
            RESPAWN: self.handle_respawn,
            SPLIT: self.handle_split,
            EJECT: self.handle_eject,
        }

    def handle(self, message):
        message_type = message.get(TYPE)

        handler = self.handlers.get(message_type)

        if handler is not None:
            handler(message)

    def handle_connect(self, message):
        username = message.get(USERNAME)

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

    def handle_respawn(self, message):
        player = self.client_handler.player
        match = self.client_handler.match

        if player is None or match is None:
            return

        match.respawn_player(player)

    def handle_split(self, message):
        player = self.client_handler.player
        match = self.client_handler.match

        if player is None or match is None:
            return

        match.split_player(player)

    def handle_eject(self, message):
        player = self.client_handler.player
        match = self.client_handler.match

        if player is None or match is None:
            return

        match.eject_mass(player)