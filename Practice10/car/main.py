import pygame
import random

# Инициализация pygame
pygame.init()

# Размер экрана
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# FPS
timer = pygame.time.Clock()

# Шрифт для текста
font = pygame.font.SysFont(None, 30)

# Счетчик монет
coins_collected = 0


# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("bluecar.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def update(self):
        pressed_keys = pygame.key.get_pressed()

        # Движение
        if pressed_keys[pygame.K_w]:
            self.rect.move_ip(0, -5)
        if pressed_keys[pygame.K_s]:
            self.rect.move_ip(0, 5)
        if pressed_keys[pygame.K_d]:
            self.rect.move_ip(5, 0)
        if pressed_keys[pygame.K_a]:
            self.rect.move_ip(-5, 0)

        # Ограничение по экрану
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("redcar.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()

        # Появляется сверху (НЕ на игроке)
        self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
        self.rect.y = -100

    def update(self):
        # Движение вниз
        self.rect.move_ip(0, 3)

        # Если ушёл вниз — снова сверху
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -100

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ---------------- COIN ----------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("coin.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()

        # Случайная позиция
        self.rect.x = random.randint(0, SCREEN_WIDTH - 30)
        self.rect.y = -30

    def update(self):
        # Падает вниз
        self.rect.move_ip(0, 4)

        # Удаляется если вышла за экран
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Создание окна
DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Создание объектов
player = Player()
enemy = Enemy()

all_sprites = pygame.sprite.Group()
coins = pygame.sprite.Group()

all_sprites.add(player, enemy)

# Фон
background = pygame.image.load("road.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))


# ---------------- GAME LOOP ----------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Случайный спавн монет
    if random.randint(1, 40) == 1:
        coin = Coin()
        all_sprites.add(coin)
        coins.add(coin)

    # Рисуем фон
    DISPLAY.blit(background, (0, 0))

    # Обновление и отрисовка
    for sprite in all_sprites:
        sprite.update()
        sprite.draw(DISPLAY)

    # Столкновение с врагом
    if pygame.sprite.collide_rect(player, enemy):
        DISPLAY.fill((255, 0, 0))
        running = False

    # Сбор монет
    collected = pygame.sprite.spritecollide(player, coins, True)
    coins_collected += len(collected)

    # Отображение счёта
    text = font.render(f"Coins: {coins_collected}", True, (255, 255, 255))
    DISPLAY.blit(text, (SCREEN_WIDTH - 120, 10))

    pygame.display.update()
    timer.tick(60)

pygame.quit()