# Jalankan dari folder proyek: .venv/bin/python -m unittest discover -s tests -t . -v
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import config
from game import Game
from sprites import GoodFruit


class GameStateTest(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def _click(self, button):
        # TextButton baru "terklik" setelah hover -> tekan -> lepas di dalam tombol.
        pos = button.getRect().center
        for event_type, extra in ((pygame.MOUSEMOTION, {"rel": (0, 0), "buttons": (0, 0, 0)}),
                                  (pygame.MOUSEBUTTONDOWN, {"button": 1}),
                                  (pygame.MOUSEBUTTONUP, {"button": 1})):
            self.game.handle_event(pygame.event.Event(event_type, pos=pos, **extra))

    def test_starts_in_menu_and_start_button_plays(self):
        self.assertEqual(self.game._state, Game.STATE_MENU)
        self._click(self.game._start_button)
        self.assertEqual(self.game._state, Game.STATE_PLAYING)

    def test_win_then_retry_resets_everything(self):
        self._click(self.game._start_button)
        for _ in range(config.BASE_SPAWN_INTERVAL * 2):
            self.game.update()
        self.game._basket.score = config.WIN_SCORE
        self.game.update()
        self.assertEqual(self.game._state, Game.STATE_GAME_OVER)
        self.assertTrue(self.game._won)

        self._click(self.game._retry_button)
        self.assertEqual(self.game._state, Game.STATE_PLAYING)
        self.assertEqual(self.game._basket.score, 0)
        self.assertEqual(self.game._basket.lives, config.START_LIVES)
        self.assertEqual(self.game._level, 1)
        self.assertEqual(len(self.game._items), 0)

    def test_lose_then_menu(self):
        self._click(self.game._start_button)
        self.game._basket.lives = 0
        self.game.update()
        self.assertEqual(self.game._state, Game.STATE_GAME_OVER)
        self.assertFalse(self.game._won)
        self._click(self.game._menu_button)
        self.assertEqual(self.game._state, Game.STATE_MENU)

    def test_escape_returns_to_menu(self):
        self._click(self.game._start_button)
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(self.game._state, Game.STATE_MENU)

    def test_hidden_buttons_ignore_clicks(self):
        # Di menu, klik di posisi tombol ULANGI tidak boleh memulai ulang apa pun.
        self._click(self.game._retry_button)
        self.assertEqual(self.game._state, Game.STATE_MENU)

    def test_nothing_moves_outside_playing(self):
        self.game._items.add(GoodFruit(pygame.Surface((44, 44)), 100, 5, 10))
        y = list(self.game._items)[0].rect.y
        self.game.update()
        self.assertEqual(list(self.game._items)[0].rect.y, y)

    def test_sounds_and_music_loaded(self):
        for name in ("catch_good", "catch_rotten", "win", "lose"):
            self.assertIsNotNone(self.game._assets._sounds[name], name)
        self.assertTrue(pygame.mixer.music.get_busy())


if __name__ == "__main__":
    unittest.main()
