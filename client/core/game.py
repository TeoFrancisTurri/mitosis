from queue import Queue

import pygame

from client.config.client_settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from client.states.main_menu_state import MainMenuState
from client.network.client import Client
from client.camera.camera import Camera
from client.managers.snapshot_manager import SnapshotManager

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

            for event in pygame.event.get():
                self.state_changed = False

                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.state.handle_event(event)

                if self.state_changed:
                    break
     
            self.state.update(dt)
            self.state.draw()

            pygame.display.flip()

        pygame.quit()
