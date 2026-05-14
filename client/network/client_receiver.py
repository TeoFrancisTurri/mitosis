import json
import threading

from client.network.client_message_handler import ClientMessageHandler
from shared.config.network_config import BUFFER_SIZE, ENCODING

class ClientReceiver(threading.Thread):
    def __init__(self, client_socket, snapshot_manager, event_queue):
        super().__init__(daemon=True)

        self.client_socket = client_socket

        self.message_handler = ClientMessageHandler(
            snapshot_manager,
            event_queue
        )

        self.running = True

    def run(self):
        buffer = ""
        while self.running:
            try:
                data = self.client_socket.recv(BUFFER_SIZE)

                if not data:
                    print("Servidor desconectado")
                    break

                buffer += data.decode(ENCODING)

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if not line:
                        continue

                    message = json.loads(line)

                    self.message_handler.handle(message)

            except json.JSONDecodeError:
                print("Mensaje inválido recibido")

            except OSError:
                print("Conexión cerrada")
                break

            except Exception as error:
                print(f"Error en ClientReceiver: {error}")
                break

        self.stop()

    def stop(self):
        self.running = False