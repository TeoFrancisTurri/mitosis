from server.match.match import Match


class MatchManager:
    def __init__(self):
        self.match = Match(match_id=1)
        self.match.start()

    def add_client(self, client_handler, username):
        self.match.add_client(client_handler, username)

    def remove_client(self, client_handler):
        if client_handler.match is not None:
            client_handler.match.remove_client(client_handler)

    def stop(self):
        self.match.stop()