import pygame
import random
import time
from persistence import save_score

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

font = pygame.font.SysFont(None, 30)


def run_game():
    clock = pygame.time.Clock()

    coins_collected = 0
    distance = 0
    score = 0

    ENEMY_SPEED_BASE = 3
    ENEMY_SPEED = ENEMY_SPEED_BASE

    active_power = None
    power_timer = 0

    freeze_until = 0
    spawn_lock_until = 0  # 👈 защита после repair

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # ---------- UI ----------
    def get_player_name(screen):
        name = ""
        while True:
            screen.fill((20, 20, 20))
            screen.blit(font.render("Enter name:", True, (255, 255, 255)), (150, 200))
            screen.blit(font.render(name, True, (0, 255, 0)), (150, 250))
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "Player"
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        return name if name else "Player"
                    elif e.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += e.unicode

    def wait_for_start(screen):
        while True:
            screen.fill((30, 30, 30))
            screen.blit(font.render("Press any key", True, (255, 255, 255)), (150, 300))
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                if e.type == pygame.KEYDOWN:
                    return True

    # ---------- PLAYER ----------
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.transform.scale(
                pygame.image.load("assets/bluecar.png"), (50, 50)
            )
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 500))
            self.speed = 5
            self.shield = False

        def update(self):
            if time.time() < freeze_until:
                return

            keys = pygame.key.get_pressed()
            spd = 7 if active_power == "nitro" else self.speed

            if keys[pygame.K_a]:
                self.rect.x -= spd
            if keys[pygame.K_d]:
                self.rect.x += spd
            if keys[pygame.K_w]:
                self.rect.y -= spd
            if keys[pygame.K_s]:
                self.rect.y += spd

            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # ---------- ENEMY ----------
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, group):
            super().__init__()
            self.group = group
            self.image = pygame.transform.scale(
                pygame.image.load("assets/redcar.png"), (50, 50)
            )
            self.rect = self.image.get_rect()
            self.respawn()

        def respawn(self):
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = random.randint(-300, -50)

        def update(self):
            self.rect.y += ENEMY_SPEED
            if self.rect.top > SCREEN_HEIGHT:
                self.respawn()

    class TrafficCar(Enemy):
        pass

    # ---------- COIN ----------
    class Coin(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.weight = random.randint(1, 3)
            size = 20 + self.weight * 5
            self.image = pygame.transform.scale(
                pygame.image.load("assets/coin.png"), (size, size)
            )
            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, SCREEN_WIDTH - size)
            self.rect.y = -size

        def update(self):
            self.rect.y += 3
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

    # ---------- OBSTACLE ----------
    class Obstacle(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            base = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(base, (255, 0, 0, 80), (25, 25), 25)

            icon = pygame.transform.scale(
                pygame.image.load("assets/oil.png"), (40, 40)
            )
            base.blit(icon, (5, 5))

            self.image = base
            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -50

        def update(self):
            self.rect.y += 4
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

    # ---------- POWERUP ----------
    class PowerUp(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.type = random.choice(["nitro", "repair", "shield"])

            colors = {
                "nitro": (0, 255, 255, 80),
                "repair": (255, 255, 0, 80),
                "shield": (0, 255, 0, 80)
            }

            base = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(base, colors[self.type], (25, 25), 25)

            icon = pygame.transform.scale(
                pygame.image.load(f"assets/{self.type}.png"), (30, 30)
            )
            base.blit(icon, (10, 10))

            self.image = base
            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -50
            self.spawn_time = time.time()

        def update(self):
            self.rect.y += 3
            if time.time() - self.spawn_time > 6:
                self.kill()

    # ---------- INIT ----------
    bg = pygame.transform.scale(
        pygame.image.load("assets/road.png"),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    traffic = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    enemy = Enemy(traffic)

    all_sprites = pygame.sprite.Group(player, enemy)

    username = get_player_name(screen)
    if not wait_for_start(screen):
        return

    running = True
    while running:
        now = time.time()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # ---------- PROGRESS (СЛОЖНОСТЬ) ----------
        ENEMY_SPEED = ENEMY_SPEED_BASE + distance * 0.01

        # ---------- SPAWN LOCK (после repair) ----------
        can_spawn = now > spawn_lock_until

        if can_spawn:
            if len(coins) < 5 and random.randint(1, 90) == 1:
                c = Coin()
                coins.add(c)
                all_sprites.add(c)

            if len(obstacles) < 3 and random.randint(1, 250) == 1:
                o = Obstacle()
                obstacles.add(o)
                all_sprites.add(o)

            if len(traffic) < 4 and random.randint(1, 200) == 1:
                t = TrafficCar(traffic)
                traffic.add(t)
                all_sprites.add(t)

            if len(powerups) < 2 and random.randint(1, 300) == 1:
                p = PowerUp()
                powerups.add(p)
                all_sprites.add(p)

        # ---------- UPDATE ----------
        screen.blit(bg, (0, 0))

        for s in list(all_sprites):
            s.update()
            screen.blit(s.image, s.rect)

        # ---------- COLLISIONS ----------
        hit_enemy = pygame.sprite.collide_rect(player, enemy)
        hit_traffic = pygame.sprite.spritecollide(player, traffic, False)

        if hit_enemy or hit_traffic:
            if player.shield:
                player.shield = False
                enemy.respawn()
                for t in hit_traffic:
                    t.respawn()
            else:
                running = False

        # OIL
        if pygame.sprite.spritecollide(player, obstacles, False):
            freeze_until = now + 0.7

        # COINS
        for c in pygame.sprite.spritecollide(player, coins, True):
            coins_collected += c.weight

        # POWERUPS
        for p in pygame.sprite.spritecollide(player, powerups, True):
            active_power = p.type
            power_timer = now

            if p.type == "repair":
                # 🔥 ПОЛНОЕ ОЧИЩЕНИЕ ВСЕГО С ЭКРАНА
                for group in [coins, obstacles, traffic, powerups]:
                    for sprite in group:
                        sprite.kill()

                enemy.respawn()

                freeze_until = 0
                spawn_lock_until = now + 1.5  # 👈 блок новых спавнов

            if p.type == "shield":
                player.shield = True

        # nitro timer
        if active_power == "nitro" and now - power_timer > 6:
            active_power = None

        # shield effect
        if player.shield:
            shield_img = pygame.transform.scale(
                pygame.image.load("assets/sphere.png"), (60, 60)
            )
            screen.blit(shield_img, (player.rect.x - 5, player.rect.y - 5))

        # ---------- SCORE ----------
        distance += 0.03
        score = coins_collected * 10 + int(distance)

        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Dist: {int(distance)}", True, (255, 255, 255)), (10, 40))

        pygame.display.update()
        clock.tick(60)

    save_score(username, score, distance)