from shared.protocol.message_fields import TYPE, PLAYER_ID, MESSAGE, SNAPSHOT
from shared.protocol.message_types import MATCH_FOUND, MATCH_CLOSED, GAME_STATE, ERROR


class ClientMessageHandler:
    def __init__(self, snapshot_manager, event_queue):
        self.snapshot_manager = snapshot_manager
        self.event_queue = event_queue

        self.handlers = {
            MATCH_FOUND: self.handle_match_found,
            MATCH_CLOSED: self.handle_match_closed,
            GAME_STATE: self.handle_game_state,
            ERROR: self.handle_error,
        }

    def handle(self, message: dict):
        message_type = message.get(TYPE)

        handler = self.handlers.get(message_type)

        if handler is None:
            print(f"Mensaje desconocido del servidor: {message}")
            return

        handler(message)

    def handle_match_found(self, message):
        self.event_queue.put({
            TYPE: MATCH_FOUND,
            PLAYER_ID: message.get(PLAYER_ID),
        })

    def handle_match_closed(self, message):
        self.event_queue.put({
            TYPE: MATCH_CLOSED,
            MESSAGE: message.get(MESSAGE),
        })

    def handle_game_state(self, message):
        snapshot = message.get(SNAPSHOT)

        if snapshot is None:
            return

        self.snapshot_manager.update_snapshot(snapshot)
    def handle_error(self, message):
        self.event_queue.put({
            TYPE: ERROR,
            MESSAGE: message.get(MESSAGE),
        })