import pygame
import random

pygame.init()

# ---------------- НАСТРОЙКИ ----------------
WIDTH = 400
HEIGHT = 400
CELL_SIZE = 20

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# Окно
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# ---------------- ЗМЕЙКА ----------------
snake = [(100, 100), (80, 100), (60, 100)]
direction = (20, 0)

# Флаг для ограничения поворотов
change_direction = False

# ---------------- ЕДА ----------------
def generate_food():
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        
        # Не спавнится на змейке
        if (x, y) not in snake:
            return (x, y)

food = generate_food()

# ---------------- СЧЕТ ----------------
score = 0
level = 1
speed = 8

# ---------------- GAME LOOP ----------------
running = True
while running:
    change_direction = False  # сброс каждый кадр

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------- УПРАВЛЕНИЕ WASD --------
        if event.type == pygame.KEYDOWN and not change_direction:
            if event.key == pygame.K_w and direction != (0, 20):
                direction = (0, -20)
                change_direction = True

            elif event.key == pygame.K_s and direction != (0, -20):
                direction = (0, 20)
                change_direction = True

            elif event.key == pygame.K_a and direction != (20, 0):
                direction = (-20, 0)
                change_direction = True

            elif event.key == pygame.K_d and direction != (-20, 0):
                direction = (20, 0)
                change_direction = True

    # ---------------- ДВИЖЕНИЕ ----------------
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    snake.insert(0, new_head)

    # ---------------- СТОЛКНОВЕНИЕ С ГРАНИЦАМИ ----------------
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        running = False

    # ---------------- СТОЛКНОВЕНИЕ С СОБОЙ ----------------
    if new_head in snake[1:]:
        running = False

    # ---------------- ЕДА ----------------
    if new_head == food:
        score += 1
        food = generate_food()

        # Новый уровень каждые 3 очка
        if score % 3 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    # ---------------- ОТРИСОВКА ----------------
    screen.fill(BLACK)

    # Рисуем змейку
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    # Рисуем еду
    pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))

    # Текст
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (300, 10))

    pygame.display.update()
    clock.tick(speed)

pygame.quit()