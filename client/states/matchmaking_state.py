import pygame

from client.states import ClientState
from client.ui import Button

from shared.protocol import (
	TYPE,
	PLAYER_ID,
	MESSAGE,
	MATCH_FOUND,
	ERROR,
	DISCONNECT
)

from client.config.ui.connection_error_config import CONNECTION_ERROR_DEFAULT_MESSAGE

from client.config.ui.matchmaking_config import *

from client.network import connect


class MatchmakingState(ClientState):
	def __init__(self, game, username):
		super().__init__(game)

		self.username = username

		self.font = pygame.font.SysFont(
			None,
			MATCHMAKING_FONT_SIZE
		)

		center_x = self.screen.get_width() // 2

		self.cancel_button = Button(
			rect=(
				center_x - MATCHMAKING_CANCEL_BUTTON_WIDTH // 2,
				MATCHMAKING_CANCEL_BUTTON_Y,
				MATCHMAKING_CANCEL_BUTTON_WIDTH,
				MATCHMAKING_CANCEL_BUTTON_HEIGHT,
			),
			text=MATCHMAKING_CANCEL_BUTTON_TEXT,
			background_color=MATCHMAKING_CANCEL_BUTTON_COLOR,
			hover_color=MATCHMAKING_CANCEL_BUTTON_HOVER_COLOR,
		)
		
	def enter(self):
		if not self.game.client.connected:
			connected = self.game.client.connect()

			if not connected:
				from client.states import ConnectionErrorState
				self.game.change_state(ConnectionErrorState(self.game, CONNECTION_ERROR_DEFAULT_MESSAGE))
				return

		self.game.client.send(connect(self.username))

	def handle_event(self, event):

		if isinstance(event, pygame.event.Event):
			if self.cancel_button.is_clicked(event):
				self.cancel_matchmaking()
				return

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.cancel_matchmaking()
		else:
			event_type = event.get(TYPE)

			if event_type == MATCH_FOUND:
				from client.states import PlayingState
				player_id = event.get(PLAYER_ID)
				self.game.change_state(PlayingState(self.game, player_id))
				return

			super().handle_event(event)

	def update(self, dt):
		while not self.game.event_queue.empty():
			event = self.game.event_queue.get()

			event_type = event.get(TYPE)

			if event_type == MATCH_FOUND:
				from client.states import PlayingState
				player_id = event.get(PLAYER_ID)
				self.game.change_state(PlayingState(self.game,player_id))

			elif event_type in (ERROR, DISCONNECT):
				print(event.get(MESSAGE))
				self.go_to_main_menu()

	def draw(self):
		self.screen.fill(MATCHMAKING_BACKGROUND_COLOR)

		text = self.font.render(MATCHMAKING_TEXT, True, MATCHMAKING_TEXT_COLOR)

		rect = text.get_rect(center=(self.screen.get_width() // 2, MATCHMAKING_TEXT_Y))

		self.screen.blit(text, rect)

		self.cancel_button.draw(self.screen)

	def cancel_matchmaking(self):
		self.game.client.disconnect()
		self.go_to_main_menu()

	def go_to_main_menu(self):
		from client.states import MainMenuState
		self.game.change_state(MainMenuState(self.game))