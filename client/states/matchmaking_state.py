import pygame

from client.states.client_state import ClientState
from client.states.playing_state import PlayingState

from client.ui.button import Button

from shared.protocol.message_fields import (
	TYPE,
	PLAYER_ID,
	MESSAGE,
)

from shared.protocol.message_types import (
	MATCH_FOUND,
	ERROR,
	MATCH_CLOSED,
)


class MatchmakingState(ClientState):
	def __init__(self, game, username):
		super().__init__(game)

		self.username = username

		self.font = pygame.font.SysFont(None, 48)

		center_x = self.screen.get_width() // 2

		self.cancel_button = Button(
			rect=(center_x - 100, 350, 200, 60),
			text="Cancel",
			background_color=(200, 70, 70),
			hover_color=(230, 90, 90),
		)

	def enter(self):
		if not self.game.client.connected:
			connected = self.game.client.connect()

			if not connected:
				from client.states.connection_error_state import ConnectionErrorState
				self.game.change_state(
					ConnectionErrorState(
						self.game,
						"Could not connect to server",
					)
				)
				return

		self.game.client.send_connect(self.username)

	def handle_event(self, event):

		if self.cancel_button.is_clicked(event):
			self.cancel_matchmaking()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.cancel_matchmaking()

	def update(self, dt):
		while not self.game.event_queue.empty():
			event = self.game.event_queue.get()

			event_type = event.get(TYPE)

			if event_type == MATCH_FOUND:
				player_id = event.get(PLAYER_ID)

				self.game.change_state(
					PlayingState(
						self.game,
						player_id,
					)
				)

			elif event_type == ERROR:
				print(event.get(MESSAGE))
				self.go_to_main_menu()

			elif event_type == MATCH_CLOSED:
				print(event.get(MESSAGE))
				self.go_to_main_menu()

	def draw(self):
		self.screen.fill((25, 25, 25))

		text = self.font.render(
			"Buscando partida...",
			True,
			(255, 255, 255),
		)

		rect = text.get_rect(
			center=(
				self.screen.get_width() // 2,
				220,
			)
		)

		self.screen.blit(text, rect)

		self.cancel_button.draw(
			self.screen
		)

	def cancel_matchmaking(self):
		self.game.client.disconnect()

		self.go_to_main_menu()

	def go_to_main_menu(self):
		from client.states.main_menu_state import MainMenuState

		self.game.change_state(
			MainMenuState(self.game)
		)