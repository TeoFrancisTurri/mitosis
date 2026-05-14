import json
import socket

from client.network.client_receiver import ClientReceiver
from client.config.client_network_config import HOST

from shared.config.network_config import (
    PORT,
    ENCODING,
)

from shared.protocol.message_types import (
    CONNECT,
    DISCONNECT,
)

from shared.protocol.message_fields import (
    TYPE,
    USERNAME,
)


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
            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

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

    def send_connect(self, username):
        self.send({
            TYPE: CONNECT,
            USERNAME: username,
        })

    def send_disconnect(self):
        self.send({
            TYPE: DISCONNECT,
        })

    def send(self, message):
        if not self.connected:
            return

        try:
            data = (json.dumps(message) + "\n").encode(ENCODING)
            self.socket.sendall(data)

        except OSError as error:
            print(f"Error enviando mensaje: {error}")

            self.disconnect()

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.send_disconnect()

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