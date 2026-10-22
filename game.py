import random

import pygame
import pygwidgets

import config
from aset import AssetManager
from sprites import Basket, GoodFruit, RottenFruit


class BaseGame:
    """Kerangka umum game: membuka jendela, menjalankan game loop, dan menutup jendela."""

    def __init__(self, title, size, fps):
        pygame.init()
        self._window = pygame.display.set_mode(size)
        pygame.display.set_caption(title)
        self._clock = pygame.time.Clock()
        self._fps = fps
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self._handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self._clock.tick(self._fps)
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            else:
                self.handle_event(event)

    def handle_event(self, event):
        """Dipanggil untuk setiap event selain QUIT. Di-override oleh turunan."""

    def update(self):
        """Logika per frame. Di-override oleh turunan."""

    def draw(self):
        """Menggambar satu frame. Di-override oleh turunan."""
        self._window.fill((0, 0, 0))


class Game(BaseGame):
    """Fruit Catcher: mengatur state, objek permainan, dan tampilan."""

    STATE_MENU = "MENU"
    STATE_PLAYING = "PLAYING"
    STATE_GAME_OVER = "GAME_OVER"

    def __init__(self):
        super().__init__(config.TITLE, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), config.FPS)
        self._assets = AssetManager()
        self._load_assets()
        self._basket_frames = [self._assets.get_image(f"basket_{i}") for i in range(3)]
        self._items = pygame.sprite.Group()
        self._create_hud()
        self._create_menu_screen()
        self._create_end_screen()
        self._won = False
        self.reset()
        self._state = self.STATE_MENU
        self._assets.play_music("assets/sounds/music.wav")  # -1: diulang terus selama program berjalan

    def reset(self):
        """Mengembalikan skor, nyawa, level, dan objek jatuh ke awal, lalu mulai bermain."""
        self._basket = Basket(self._basket_frames)
        self._items.empty()
        self._level = 1
        self._spawn_timer = 0
        self._state = self.STATE_PLAYING

    def _load_assets(self):
        for i in range(3):
            self._assets.load_image(f"basket_{i}", f"assets/images/basket_{i}.png")
        for name, _ in config.FRESH_FRUITS:
            self._assets.load_image(name, f"assets/images/{name}.png")
        self._assets.load_image("rotten", "assets/images/rotten.png")
        for name in ("catch_good", "catch_rotten", "win", "lose"):
            self._assets.load_sound(name, f"assets/sounds/{name}.wav")

    def _create_hud(self):
        # Widget dibuat sekali; setiap frame cukup setValue() (tidak menggambar ulang jika teks sama).
        size, color = config.HUD_FONT_SIZE, config.TEXT_DARK
        self._score_text = pygwidgets.DisplayText(self._window, (20, 15), fontSize=size, textColor=color)
        self._level_text = pygwidgets.DisplayText(self._window, (340, 15), fontSize=size, textColor=color)
        self._lives_text = pygwidgets.DisplayText(self._window, (640, 15), fontSize=size, textColor=color)

    def _centered_text(self, y, value, size, color=config.TEXT_DARK):
        return pygwidgets.DisplayText(self._window, (0, y), value, fontSize=size, textColor=color,
                                      width=config.WINDOW_WIDTH, justified="center")

    def _button(self, center_x, y, text):
        width, height = config.BUTTON_SIZE
        return pygwidgets.TextButton(self._window, (center_x - width // 2, y), text,
                                     width=width, height=height, fontSize=36,
                                     upColor=config.BUTTON_UP, overColor=config.BUTTON_OVER,
                                     downColor=config.BUTTON_DOWN)

    def _create_menu_screen(self):
        self._menu_title = self._centered_text(110, "FRUIT CATCHER", 80, config.TITLE_RED)
        self._menu_subtitle = self._centered_text(190, "Tangkap buah segar, hindari yang busuk!", 30)
        self._menu_controls = self._centered_text(
            420, "Kontrol: panah kiri/kanan atau A/D   |   Esc: kembali ke menu", 24)
        self._start_button = self._button(config.WINDOW_WIDTH // 2, 320, "MULAI")

    def _create_end_screen(self):
        self._win_title = self._centered_text(110, "Selamat, Kamu Menang!", 64, config.WIN_GREEN)
        self._lose_title = self._centered_text(110, "GAME OVER", 80, config.TITLE_RED)
        self._final_score_text = self._centered_text(200, "", 40)
        self._final_lives_text = self._centered_text(250, "", 28)
        self._retry_button = self._button(config.WINDOW_WIDTH // 2 - 130, 320, "ULANGI")
        self._menu_button = self._button(config.WINDOW_WIDTH // 2 + 130, 320, "MENU")

    # --- kesulitan berdasarkan level ---

    def _fall_speed(self):
        return config.BASE_FALL_SPEED + (self._level - 1) * config.FALL_SPEED_STEP

    def _spawn_interval(self):
        interval = config.BASE_SPAWN_INTERVAL - (self._level - 1) * config.SPAWN_INTERVAL_STEP
        return max(interval, config.MIN_SPAWN_INTERVAL)

    def _rotten_chance(self):
        chance = config.BASE_ROTTEN_CHANCE + (self._level - 1) * config.ROTTEN_CHANCE_STEP
        return min(chance, config.MAX_ROTTEN_CHANCE)

    # --- logika permainan ---

    def _spawn_item(self):
        x = random.randint(config.SPAWN_MARGIN, config.WINDOW_WIDTH - config.SPAWN_MARGIN)
        speed = self._fall_speed()
        if random.random() < self._rotten_chance():
            item = RottenFruit(self._assets.get_image("rotten"), x, speed)
        else:
            name, points = random.choice(config.FRESH_FRUITS)
            item = GoodFruit(self._assets.get_image(name), x, speed, points)
        self._items.add(item)

    def _check_collisions(self):
        for item in list(self._items):
            if self._basket.rect.colliderect(item.rect):
                item.on_caught(self._basket)  # polimorfisme: GoodFruit menambah skor, RottenFruit mengurangi nyawa
                self._assets.play_sound(item.CATCH_SOUND)
                item.kill()

    def _end_game(self, won):
        self._won = won
        self._final_score_text.setValue(f"Skor akhir: {self._basket.score}")
        self._final_lives_text.setValue(f"Sisa nyawa: {self._basket.lives}" if won else "")
        self._assets.play_sound("win" if won else "lose")
        self._state = self.STATE_GAME_OVER

    # --- event, update, draw (override dari BaseGame) ---

    def handle_event(self, event):
        # Hanya widget di layar yang sedang tampil yang menerima event.
        if self._state == self.STATE_MENU:
            if self._start_button.handleEvent(event):
                self.reset()
        elif self._state == self.STATE_PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._state = self.STATE_MENU
        elif self._state == self.STATE_GAME_OVER:
            if self._retry_button.handleEvent(event):
                self.reset()
            if self._menu_button.handleEvent(event):
                self._state = self.STATE_MENU

    def update(self):
        if self._state != self.STATE_PLAYING:
            return
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1
        self._basket.move(direction)
        self._basket.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self._spawn_interval():
            self._spawn_timer = 0
            self._spawn_item()
        self._items.update()
        self._check_collisions()
        self._level = 1 + self._basket.score // config.POINTS_PER_LEVEL

        self._score_text.setValue(f"Skor: {self._basket.score}")
        self._level_text.setValue(f"Level: {self._level}")
        self._lives_text.setValue(f"Nyawa: {self._basket.lives}")

        if self._basket.score >= config.WIN_SCORE:
            self._end_game(won=True)
        elif self._basket.lives == 0:
            self._end_game(won=False)

    def draw(self):
        self._window.fill(config.SKY_BLUE)
        if self._state == self.STATE_PLAYING:
            self._items.draw(self._window)
        # Tanah digambar setelah buah supaya buah yang lolos tampak masuk ke balik tanah.
        ground = pygame.Rect(0, config.WINDOW_HEIGHT - config.GROUND_HEIGHT,
                             config.WINDOW_WIDTH, config.GROUND_HEIGHT)
        pygame.draw.rect(self._window, config.GROUND_BROWN, ground)

        if self._state == self.STATE_MENU:
            self._draw_menu()
        elif self._state == self.STATE_PLAYING:
            self._draw_playing()
        else:
            self._draw_end()

    def _draw_menu(self):
        self._menu_title.draw()
        self._menu_subtitle.draw()
        for i, (name, _) in enumerate(config.FRESH_FRUITS):
            image = self._assets.get_image(name)
            self._window.blit(image, image.get_rect(center=(200 + i * 200, 270)))
        self._start_button.draw()
        self._menu_controls.draw()

    def _draw_playing(self):
        self._window.blit(self._basket.image, self._basket.rect)
        self._score_text.draw()
        self._level_text.draw()
        self._lives_text.draw()

    def _draw_end(self):
        (self._win_title if self._won else self._lose_title).draw()
        self._final_score_text.draw()
        self._final_lives_text.draw()
        self._retry_button.draw()
        self._menu_button.draw()
