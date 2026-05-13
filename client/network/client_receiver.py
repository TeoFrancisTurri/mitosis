import json
import threading

from client.network.client_message_handler import ClientMessageHandler


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
        while self.running:
            try:
                data = self.client_socket.recv(4096)

                if not data:
                    print("Servidor desconectado")
                    break

                message = json.loads(
                    data.decode("utf-8")
                )

                self.message_handler.handle(
                    message
                )

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