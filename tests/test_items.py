# Jalankan dari folder proyek: .venv/bin/python -m unittest discover -s tests -t . -v
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import config
from game import Game
from sprites import Basket, FallingItem, GoodFruit, RottenFruit


def _surface():
    return pygame.Surface((44, 44))


class FallingItemTest(unittest.TestCase):

    def setUp(self):
        self.basket = Basket([pygame.Surface((130, 80)) for _ in range(3)])

    def test_good_fruit_adds_points(self):
        GoodFruit(_surface(), 100, 3, 20).on_caught(self.basket)
        self.assertEqual(self.basket.score, 20)

    def test_rotten_fruit_takes_life(self):
        RottenFruit(_surface(), 100, 3).on_caught(self.basket)
        self.assertEqual(self.basket.lives, config.START_LIVES - 1)

    def test_base_class_must_be_overridden(self):
        with self.assertRaises(NotImplementedError):
            FallingItem(_surface(), 100, 3).on_caught(self.basket)

    def test_removed_after_leaving_screen(self):
        group = pygame.sprite.Group(GoodFruit(_surface(), 100, 10, 10))
        for _ in range(100):
            group.update()
        self.assertEqual(len(group), 0)

    def test_fractional_speed_accumulates(self):
        item = GoodFruit(_surface(), 100, 0.5, 10)
        start = item.rect.y
        for _ in range(10):
            item.update()
        self.assertEqual(item.rect.y - start, 5)


class GameLogicTest(unittest.TestCase):

    def setUp(self):
        # Tanpa pygame.quit() di antara tes: pygwidgets menyimpan cache font yang rusak setelah quit.
        self.game = Game()
        self.game.reset()  # langsung ke state PLAYING, melewati menu

    def _drop_on_basket(self, item):
        item.rect.center = self.game._basket.rect.center
        self.game._items.add(item)
        self.game._check_collisions()

    def test_catching_fruit(self):
        self._drop_on_basket(GoodFruit(_surface(), 0, 3, 10))
        self._drop_on_basket(RottenFruit(_surface(), 0, 3))
        self.assertEqual(self.game._basket.score, 10)
        self.assertEqual(self.game._basket.lives, config.START_LIVES - 1)
        self.assertEqual(len(self.game._items), 0)

    def test_spawns_over_time(self):
        for _ in range(config.BASE_SPAWN_INTERVAL * 3):
            self.game.update()
        self.assertGreater(len(self.game._items), 0)

    def test_difficulty_rises_with_level(self):
        easy = (self.game._fall_speed(), self.game._spawn_interval(), self.game._rotten_chance())
        self.game._basket.score = 120
        self.game.update()
        self.assertEqual(self.game._level, 3)
        self.assertGreater(self.game._fall_speed(), easy[0])
        self.assertLess(self.game._spawn_interval(), easy[1])
        self.assertGreater(self.game._rotten_chance(), easy[2])


if __name__ == "__main__":
    unittest.main()
