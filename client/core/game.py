from queue import Queue

import pygame

from client.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from client.states import MainMenuState
from client.network import Client
from client.camera import Camera
from client.managers import SnapshotManager

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        pygame.key.set_repeat(400, 40)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.event_queue = Queue()
        self.snapshot_manager = SnapshotManager()

        self.client = Client(
            self.snapshot_manager,
            self.event_queue
        )

        self.state_changed = False
        self.state = MainMenuState(self)
        self.state.enter()

    def change_state(self, new_state):
        self.state.exit()
        self.state = new_state
        self.state.enter()
        self.state_changed = True

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)

            self.handle_pygame_events()
            self.handle_network_events()

            self.state.update(dt)
            self.state.draw()

            pygame.display.flip()

        pygame.quit()


    def handle_pygame_events(self):
        for event in pygame.event.get():
            self.state_changed = False

            if event.type == pygame.QUIT:
                self.running = False
                return

            self.state.handle_event(event)

            if self.state_changed:
                return
            
    def handle_network_events(self):
        while not self.event_queue.empty():
            self.state_changed = False

            event = self.event_queue.get()

            self.state.handle_event(event)

            if self.state_changed:
                return