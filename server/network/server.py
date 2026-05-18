import socket
import threading

from server.network.client_handler import ClientHandler
from server.matchmaking.match_manager import MatchManager
from shared.config import HOST, PORT


class Server:
    def __init__(self):
        self.host = HOST
        self.port = PORT

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.running = False

        self.client_handlers = []
        self.lock = threading.Lock()

        self.match_manager = MatchManager()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        self.running = True

        print(f"Servidor escuchando en {self.host}:{self.port}")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()

                print(f"Cliente conectado: {address}")

                client_handler = ClientHandler(
                    client_socket,
                    address,
                    self.match_manager,
                    self
                )

                client_thread = threading.Thread(
                    target=client_handler.run,
                    daemon=True
                )

                with self.lock:
                    self.client_handlers.append(client_handler)

                client_thread.start()

            except OSError:
                break

            except Exception as error:
                print(f"Error aceptando cliente: {error}")

        self.stop()

    def remove_client(self, client_handler):
        with self.lock:
            if client_handler in self.client_handlers:
                self.client_handlers.remove(client_handler)

    def stop(self):
        if not self.running:
            return

        self.running = False

        print("Cerrando servidor...")

        self.match_manager.stop()

        with self.lock:
            client_handlers = list(self.client_handlers)
            self.client_handlers.clear()

        for client_handler in client_handlers:
            client_handler.disconnect()

        self.server_socket.close()

        print("Servidor detenido")