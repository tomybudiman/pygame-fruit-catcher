# Alat bantu (bukan bagian dari game): menggambar 3 frame keranjang lalu menyimpannya
# ke assets/images/. Jalankan sekali dari folder proyek: .venv/bin/python tools/buat_keranjang.py
import os

import pygame


class BasketArtist:
    """Menggambar frame keranjang: diam, goyang kiri, dan goyang kanan."""

    CANVAS = (130, 80)
    WOOD = (205, 150, 90)
    RIM = (170, 115, 60)
    OUTLINE = (60, 40, 25)
    TILT = 7  # derajat

    def __init__(self, out_dir):
        self._out_dir = out_dir

    def _draw_base(self):
        surf = pygame.Surface((120, 70), pygame.SRCALPHA)
        top_l, top_r, bot_r, bot_l = (8, 14), (112, 14), (96, 64), (24, 64)
        pygame.draw.polygon(surf, self.WOOD, [top_l, top_r, bot_r, bot_l])
        # Anyaman: garis horizontal mengikuti kemiringan sisi, garis vertikal dari atas ke bawah.
        for t in (0.35, 0.68):
            y = top_l[1] + (bot_l[1] - top_l[1]) * t
            x_l = top_l[0] + (bot_l[0] - top_l[0]) * t
            x_r = top_r[0] + (bot_r[0] - top_r[0]) * t
            pygame.draw.line(surf, self.OUTLINE, (x_l, y), (x_r, y), 2)
        for t in (0.25, 0.5, 0.75):
            x_top = top_l[0] + (top_r[0] - top_l[0]) * t
            x_bot = bot_l[0] + (bot_r[0] - bot_l[0]) * t
            pygame.draw.line(surf, self.OUTLINE, (x_top, top_l[1]), (x_bot, bot_l[1]), 2)
        pygame.draw.polygon(surf, self.OUTLINE, [top_l, top_r, bot_r, bot_l], 3)
        rim = pygame.Rect(3, 7, 114, 12)
        pygame.draw.rect(surf, self.RIM, rim, border_radius=6)
        pygame.draw.rect(surf, self.OUTLINE, rim, 3, border_radius=6)
        return surf

    def _on_canvas(self, surf):
        canvas = pygame.Surface(self.CANVAS, pygame.SRCALPHA)
        canvas.blit(surf, surf.get_rect(center=canvas.get_rect().center))
        return canvas

    def save_frames(self):
        base = self._draw_base()
        frames = [base, pygame.transform.rotate(base, self.TILT),
                  pygame.transform.rotate(base, -self.TILT)]
        os.makedirs(self._out_dir, exist_ok=True)
        for i, frame in enumerate(frames):
            path = os.path.join(self._out_dir, f"basket_{i}.png")
            pygame.image.save(self._on_canvas(frame), path)
            print("Tersimpan:", path)


BasketArtist(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "images")).save_frames()
