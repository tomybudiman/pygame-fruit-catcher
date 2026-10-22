# Jalankan dari folder proyek: .venv/bin/python -m unittest discover -s tests -t . -v
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import config
from sprites import Basket


class BasketTest(unittest.TestCase):

    def setUp(self):
        frames = [pygame.Surface((130, 80)) for _ in range(3)]
        self.basket = Basket(frames)

    # --- property dan validasi (bagian Tomy) ---

    def test_speed_valid(self):
        self.basket.speed = config.MAX_BASKET_SPEED
        self.assertEqual(self.basket.speed, config.MAX_BASKET_SPEED)

    def test_speed_invalid(self):
        for value in (0, -3, config.MAX_BASKET_SPEED + 1):
            with self.assertRaises(ValueError, msg=f"speed = {value}"):
                self.basket.speed = value

    def test_lives_invalid(self):
        for value in (-1, config.START_LIVES + 1):
            with self.assertRaises(ValueError, msg=f"lives = {value}"):
                self.basket.lives = value

    def test_score_invalid(self):
        with self.assertRaises(ValueError):
            self.basket.score = -10

    # --- perilaku ---

    def test_add_score_and_lose_life(self):
        self.basket.add_score(20)
        self.basket.add_score(10)
        self.assertEqual(self.basket.score, 30)
        for _ in range(config.START_LIVES + 2):
            self.basket.lose_life()
        self.assertEqual(self.basket.lives, 0)

    def test_stays_inside_window(self):
        for _ in range(500):
            self.basket.move(-1)
        self.assertEqual(self.basket.rect.left, 0)
        for _ in range(500):
            self.basket.move(1)
        self.assertEqual(self.basket.rect.right, config.WINDOW_WIDTH)

    def test_animation(self):
        seen = set()
        for _ in range(config.BASKET_ANIM_DELAY * 4):
            self.basket.move(1)
            self.basket.update()
            seen.add(self.basket._frame_index)
        self.assertEqual(seen, {0, 1, 2})
        self.basket.move(0)
        self.basket.update()
        self.assertEqual(self.basket._frame_index, 0)


if __name__ == "__main__":
    unittest.main()
