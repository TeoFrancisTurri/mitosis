from shared.protocol import (
    TYPE, SNAPSHOT, GAME_STATE, CLIENT_EVENT_MESSAGES
)

class ClientMessageHandler:
    def __init__(self, snapshot_manager, event_queue):
        self.snapshot_manager = snapshot_manager
        self.event_queue = event_queue

    def handle(self, message):
        message_type = message.get(TYPE)

        if message_type == GAME_STATE:
            self.handle_game_state(message)    

        elif message_type in CLIENT_EVENT_MESSAGES:
            self.event_queue.put(message)
            
        else:
            print(f"Mensaje desconocido del servidor: {message}")

    def handle_game_state(self, message):
        snapshot = message.get(SNAPSHOT)

        if snapshot is None:
            print("GAME_STATE sin snapshot")
            return

        self.snapshot_manager.update_snapshot(snapshot)