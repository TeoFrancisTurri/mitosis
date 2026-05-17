import json
import socket

from client.network import ClientReceiver
from shared.config import PORT, ENCODING
from client.config import HOST
from client.network.server_messages import disconnect
 

class Client:
    def __init__(self, snapshot_manager, event_queue):
        self.snapshot_manager = snapshot_manager
        self.event_queue = event_queue
        self.socket = None
        self.receiver = None

        self.connected = False

    def connect(self):
        if self.connected:
            return True

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.connect((HOST, PORT))

            self.receiver = ClientReceiver(
                self.socket,
                self.snapshot_manager,
                self.event_queue,
            )

            self.receiver.start()

            self.connected = True

            print("Conectado al servidor")

            return True

        except ConnectionRefusedError:
            print("Servidor no disponible")

        except OSError as error:
            print(f"Error conectando: {error}")

        self.connected = False

        return False

    def send(self, message):
        if not self.connected:
            return

        try:
            data = (json.dumps(message) + "\n").encode(ENCODING)
            self.socket.sendall(data)

        except OSError as error:
            print(f"Error enviando mensaje: {error}")

            self.disconnect()

    def disconnect(self, notify_server=True):
        if not self.connected:
            return

        if notify_server:
            try:
                self.send(disconnect())

            except Exception:
                pass

        try:
            if self.receiver is not None:
                self.receiver.stop()

        except Exception:
            pass

        try:
            if self.socket is not None:
                self.socket.close()

        except OSError:
            pass

        self.socket = None
        self.receiver = None

        self.connected = False

        print("Cliente desconectado")