import threading

class SnapshotManager:
    def __init__(self):
        self.snapshot = None

        self.lock = threading.Lock()

    def update_snapshot(self, snapshot):
        with self.lock:
            self.snapshot = snapshot

    def get_snapshot(self):
        with self.lock:
            return self.snapshot