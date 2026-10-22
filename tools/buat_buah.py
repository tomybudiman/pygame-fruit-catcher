# Alat bantu (bukan bagian dari game): menggambar apel, jeruk, pisang, dan buah busuk
# lalu menyimpannya ke assets/images/. Jalankan sekali: .venv/bin/python tools/buat_buah.py
import os

import pygame


class FruitArtist:
    """Menggambar sprite buah berukuran 44x44 dengan latar transparan."""

    SIZE = (44, 44)
    OUTLINE = (40, 40, 40)
    LEAF = (90, 170, 70)
    STEM = (110, 70, 40)
    CLEAR = (0, 0, 0, 0)

    def __init__(self, out_dir):
        self._out_dir = out_dir

    def _canvas(self):
        return pygame.Surface(self.SIZE, pygame.SRCALPHA)

    def _round_fruit(self, color, with_leaf):
        surf = self._canvas()
        pygame.draw.circle(surf, self.OUTLINE, (22, 26), 17)
        pygame.draw.circle(surf, color, (22, 26), 15)
        pygame.draw.circle(surf, (255, 255, 255, 120), (16, 20), 4)  # kilau
        if with_leaf:
            pygame.draw.line(surf, self.STEM, (22, 11), (24, 4), 3)
            pygame.draw.ellipse(surf, self.LEAF, (25, 3, 12, 7))
            pygame.draw.ellipse(surf, self.OUTLINE, (25, 3, 12, 7), 1)
        return surf

    def apple(self):
        return self._round_fruit((214, 69, 65), with_leaf=True)

    def orange(self):
        surf = self._round_fruit((240, 160, 40), with_leaf=False)
        pygame.draw.circle(surf, self.LEAF, (22, 10), 3)
        return surf

    def banana(self):
        # Bulan sabit: lingkaran kuning yang bagian atasnya "dihapus" lingkaran transparan.
        surf = self._canvas()
        pygame.draw.circle(surf, self.OUTLINE, (22, 18), 20)
        pygame.draw.circle(surf, (245, 205, 50), (22, 18), 18)
        pygame.draw.circle(surf, self.CLEAR, (22, 10), 18)
        pygame.draw.circle(surf, self.STEM, (4, 17), 3)
        pygame.draw.circle(surf, self.STEM, (40, 17), 3)
        return surf

    def rotten(self):
        surf = self._round_fruit((115, 125, 65), with_leaf=False)
        pygame.draw.circle(surf, (80, 75, 40), (30, 32), 4)
        pygame.draw.circle(surf, (80, 75, 40), (14, 33), 3)
        for cx in (16, 28):  # mata "x x"
            pygame.draw.line(surf, self.OUTLINE, (cx - 3, 21), (cx + 3, 27), 2)
            pygame.draw.line(surf, self.OUTLINE, (cx - 3, 27), (cx + 3, 21), 2)
        return surf

    def save_all(self):
        os.makedirs(self._out_dir, exist_ok=True)
        for name in ("apple", "orange", "banana", "rotten"):
            path = os.path.join(self._out_dir, f"{name}.png")
            pygame.image.save(getattr(self, name)(), path)
            print("Tersimpan:", path)


FruitArtist(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "images")).save_all()
