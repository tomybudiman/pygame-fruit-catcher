import os
import sys

import pygame


def path_aset(relatif):
    """Path absolut ke berkas aset, baik saat dijalankan sebagai .py maupun .exe."""
    base = getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relatif)


class AssetManager:
    """Memuat gambar dan suara satu kali, lalu menyimpannya untuk dipakai ulang."""

    def __init__(self):
        self._images = {}
        self._sounds = {}

    def load_image(self, name, relatif, size=None):
        try:
            image = pygame.image.load(path_aset(relatif)).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"[AssetManager] Gagal memuat gambar '{relatif}': {e}", file=sys.stderr)
            # Kotak pengganti supaya game tetap jalan dan aset yang hilang terlihat jelas.
            image = pygame.Surface(size or (40, 40))
            image.fill((255, 0, 255))
        if size is not None:
            image = pygame.transform.smoothscale(image, size)
        self._images[name] = image
        return image

    def get_image(self, name):
        return self._images[name]

    def load_sound(self, name, relatif):
        try:
            sound = pygame.mixer.Sound(path_aset(relatif))
        except (pygame.error, FileNotFoundError) as e:
            print(f"[AssetManager] Gagal memuat suara '{relatif}': {e}", file=sys.stderr)
            sound = None
        self._sounds[name] = sound
        return sound

    def play_sound(self, name):
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self, relatif, loops=-1):
        try:
            pygame.mixer.music.load(path_aset(relatif))
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"[AssetManager] Gagal memutar musik '{relatif}': {e}", file=sys.stderr)

    def stop_music(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
