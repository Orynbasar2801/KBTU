import pygame
import random

pygame.init()
WIDTH, HEIGHT = 400, 400
CELL_SIZE = 20
WHITE, GREEN, RED, BLACK, GOLD = (255, 255, 255), (0, 200, 0), (200, 0, 0), (0, 0, 0), (255, 215, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

snake = [(100, 100), (80, 100), (60, 100)]
direction = (20, 0)
score, speed = 0, 8

def generate_food():
    # Генерация с разным весом (1 или 3)
    x = random.randrange(0, WIDTH, CELL_SIZE)
    y = random.randrange(0, HEIGHT, CELL_SIZE)
    weight = 3 if random.random() > 0.8 else 1
    return {"pos": (x, y), "weight": weight, "spawn_time": pygame.time.get_ticks()}

food = generate_food()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # УПРАВЛЕНИЕ: Убрана проверка (direction != противоположное), 
        # теперь змейка может врезаться в саму себя при резком развороте.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: direction = (0, -20)
            elif event.key == pygame.K_s: direction = (0, 20)
            elif event.key == pygame.K_a: direction = (-20, 0)
            elif event.key == pygame.K_d: direction = (20, 0)

    # Исчезновение еды по таймеру (5 сек)
    if pygame.time.get_ticks() - food["spawn_time"] > 5000:
        food = generate_food()

    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    
    # ПРОВЕРКА СТОЛКНОВЕНИЯ: С границами ИЛИ с самим собой
    if (head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake):
        running = False # Игра окончена, если змейка "вырезалась" в себя

    snake.insert(0, head)

    if head == food["pos"]:
        score += food["weight"]
        food = generate_food()
        if score % 5 == 0: speed += 1
    else:
        # Убираем хвост, только если не съели еду
        if len(snake) > 1:
            snake.pop()

    screen.fill(BLACK)
    for seg in snake:
        pygame.draw.rect(screen, GREEN, (seg[0], seg[1], CELL_SIZE, CELL_SIZE))
    
    f_color = GOLD if food["weight"] == 3 else RED
    pygame.draw.rect(screen, f_color, (food["pos"][0], food["pos"][1], CELL_SIZE, CELL_SIZE))

    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    pygame.display.update()
    clock.tick(speed)

pygame.quit()