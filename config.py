# Semua angka penyetelan game dikumpulkan di sini supaya mudah di-tuning.

TITLE = "Fruit Catcher"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Warna (R, G, B)
SKY_BLUE = (170, 214, 245)
GROUND_BROWN = (196, 168, 118)
TEXT_DARK = (40, 40, 40)
TITLE_RED = (214, 69, 65)

GROUND_HEIGHT = 35

# Keranjang
BASKET_SPEED = 7          # piksel per frame
MAX_BASKET_SPEED = 15
BASKET_ANIM_DELAY = 6     # ganti frame animasi tiap 6 frame game
START_LIVES = 3

# Buah: (nama gambar, poin)
FRESH_FRUITS = (("apple", 10), ("orange", 10), ("banana", 20))
SPAWN_MARGIN = 30         # jarak minimal buah dari tepi layar

# Skor dan level
WIN_SCORE = 300
POINTS_PER_LEVEL = 50

# Kesulitan per level (nilai level 1, lalu perubahan tiap naik satu level)
BASE_FALL_SPEED = 3.0     # piksel per frame
FALL_SPEED_STEP = 0.6
BASE_SPAWN_INTERVAL = 60  # frame (60 = 1 detik)
SPAWN_INTERVAL_STEP = 6
MIN_SPAWN_INTERVAL = 20
BASE_ROTTEN_CHANCE = 0.25
ROTTEN_CHANCE_STEP = 0.04
MAX_ROTTEN_CHANCE = 0.5

# HUD dan layar
HUD_FONT_SIZE = 30
WIN_GREEN = (46, 140, 70)
BUTTON_UP = (255, 236, 175)
BUTTON_OVER = (255, 222, 130)
BUTTON_DOWN = (235, 195, 90)
BUTTON_SIZE = (220, 60)
