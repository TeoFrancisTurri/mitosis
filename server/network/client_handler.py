import json

from server.network.client_message_handler import ClientMessageHandler
from shared.config.network_config import ENCODING, BUFFER_SIZE

class ClientHandler:
    def __init__(self, client_socket, address, match_manager, server):
        self.client_socket = client_socket
        self.address = address
        self.match_manager = match_manager
        self.server = server

        self.player = None
        self.match = None

        self.connected = True

        self.message_handler = ClientMessageHandler(self)

    def run(self):
        print(f"Cliente conectado: {self.address}")

        try:
            while self.connected:
                data = self.client_socket.recv(BUFFER_SIZE)

                if not data:
                    print(f"Cliente cerró conexión: {self.address}")
                    break

                try:
                    message = json.loads(data.decode(ENCODING))

                except json.JSONDecodeError:
                    print(f"JSON inválido recibido de {self.address}")
                    continue

                self.message_handler.handle(message)

        except ConnectionResetError:
            print(f"Conexión reseteada por cliente: {self.address}")

        except ConnectionError:
            print(f"Error de conexión con cliente: {self.address}")

        except OSError as error:
            print(f"Error de socket con {self.address}: {error}")

        except Exception as error:
            print(f"Error inesperado con {self.address}: {error}")

        finally:
            self.disconnect()

    def send(self, message):
        if not self.connected:
            print(f"No se pudo enviar mensaje, cliente desconectado: {self.address}")
            return

        try:
            data = (json.dumps(message) + "\n").encode(ENCODING)
            print(data)
            self.client_socket.sendall(data)

        except OSError as error:
            print(f"Error enviando mensaje a {self.address}: {error}")
            self.disconnect()

    def disconnect(self):
        if not self.connected:
            return

        self.connected = False

        print(f"Cliente desconectado: {self.address}")

  
        self.match_manager.remove_client(self)
        self.server.remove_client(self)

        try:
            self.client_socket.close()

        except OSError as error:
            print(f"Error cerrando socket de {self.address}: {error}")