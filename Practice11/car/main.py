import pygame
import random

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
timer = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

coins_collected = 0
ENEMY_SPEED = 3  # Начальная скорость врага

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("bluecar.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_w]: self.rect.move_ip(0, -5)
        if pressed_keys[pygame.K_s]: self.rect.move_ip(0, 5)
        if pressed_keys[pygame.K_d]: self.rect.move_ip(5, 0)
        if pressed_keys[pygame.K_a]: self.rect.move_ip(-5, 0)

        # Ограничение движения границами экрана
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("redcar.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
        self.rect.y = -100

    def update(self):
        # Движение с учетом глобальной скорости ENEMY_SPEED
        self.rect.move_ip(0, ENEMY_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -100

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Генерация случайного веса от 1 до 5
        self.weight = random.randint(1, 5)
        self.image = pygame.image.load("coin.png")
        # Визуально увеличиваем монету в зависимости от веса
        size = 20 + self.weight * 5
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - size)
        self.rect.y = -size

    def update(self):
        self.rect.move_ip(0, 4)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player = Player()
enemy = Enemy()
all_sprites = pygame.sprite.Group(player, enemy)
coins = pygame.sprite.Group()

background = pygame.image.load("road.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # Спавн монет
    if random.randint(1, 40) == 1:
        new_coin = Coin()
        all_sprites.add(new_coin)
        coins.add(new_coin)

    DISPLAY.blit(background, (0, 0))

    for sprite in all_sprites:
        sprite.update()
        DISPLAY.blit(sprite.image, sprite.rect)

    # Столкновение с врагом
    if pygame.sprite.collide_rect(player, enemy):
        running = False

    # Сбор монет с учетом их веса
    collected = pygame.sprite.spritecollide(player, coins, True)
    for c in collected:
        coins_collected += c.weight
        # Увеличиваем скорость врага за каждые 10 очков
        if coins_collected // 10 >= (coins_collected - c.weight) // 10:
             ENEMY_SPEED += 0.5 

    text = font.render(f"Coins: {coins_collected}", True, (255, 255, 255))
    DISPLAY.blit(text, (SCREEN_WIDTH - 120, 10))
    pygame.display.update()
    timer.tick(60)

pygame.quit()