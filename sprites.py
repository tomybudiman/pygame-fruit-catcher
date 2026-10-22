import pygame

import config


class Basket(pygame.sprite.Sprite):
    """Keranjang pemain: bergerak kiri/kanan di dalam layar, beranimasi, dan menyimpan skor serta nyawa."""

    # Urutan frame saat bergerak: goyang kiri, diam, goyang kanan, diam.
    _WALK_CYCLE = (1, 0, 2, 0)

    def __init__(self, frames):
        super().__init__()
        self._frames = frames
        self._frame_index = 0
        self._cycle_pos = 0
        self._anim_timer = 0
        self._direction = 0
        self.image = self._frames[0]
        self.rect = self.image.get_rect(
            midbottom=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - config.GROUND_HEIGHT))
        # Nilai awal lewat property supaya langsung tervalidasi.
        self.speed = config.BASKET_SPEED
        self.lives = config.START_LIVES
        self.score = 0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if not 0 < value <= config.MAX_BASKET_SPEED:
            raise ValueError(f"Kecepatan harus lebih dari 0 dan maksimal {config.MAX_BASKET_SPEED}, bukan {value}")
        self._speed = value

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        if not 0 <= value <= config.START_LIVES:
            raise ValueError(f"Nyawa harus antara 0 dan {config.START_LIVES}, bukan {value}")
        self._lives = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if value < 0:
            raise ValueError(f"Skor tidak boleh negatif, bukan {value}")
        self._score = value

    def move(self, direction):
        """direction: -1 ke kiri, 0 diam, 1 ke kanan."""
        self._direction = direction
        self.rect.x += direction * self._speed
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, config.WINDOW_WIDTH)

    def update(self):
        if self._direction == 0:
            self._frame_index = 0
            self._cycle_pos = 0
            self._anim_timer = 0
        else:
            self._anim_timer += 1
            if self._anim_timer >= config.BASKET_ANIM_DELAY:
                self._anim_timer = 0
                self._cycle_pos = (self._cycle_pos + 1) % len(self._WALK_CYCLE)
            self._frame_index = self._WALK_CYCLE[self._cycle_pos]
        self.image = self._frames[self._frame_index]

    def add_score(self, points):
        self.score += points

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1


class FallingItem(pygame.sprite.Sprite):
    """Dasar semua objek yang jatuh dari atas layar dan dibuang saat keluar layar."""

    CATCH_SOUND = None

    def __init__(self, image, x, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, 0))
        self._y = float(self.rect.y)  # posisi pecahan, karena Rect hanya menyimpan bilangan bulat
        self._speed = speed

    def update(self):
        self._y += self._speed
        self.rect.y = int(self._y)
        if self.rect.top > config.WINDOW_HEIGHT:
            self.kill()

    def on_caught(self, player):
        """Efek saat tertangkap keranjang. Wajib di-override oleh turunan."""
        raise NotImplementedError


class GoodFruit(FallingItem):
    """Buah segar: menambah skor saat tertangkap."""

    CATCH_SOUND = "catch_good"

    def __init__(self, image, x, speed, points):
        super().__init__(image, x, speed)
        self._points = points

    def on_caught(self, player):
        player.add_score(self._points)


class RottenFruit(FallingItem):
    """Buah busuk: mengurangi satu nyawa saat tertangkap."""

    CATCH_SOUND = "catch_rotten"

    def on_caught(self, player):
        player.lose_life()
