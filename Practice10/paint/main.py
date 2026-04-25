import pygame

pygame.init()

# ---------------- НАСТРОЙКИ ----------------
WIDTH, HEIGHT = 900, 600
TOOLBAR_WIDTH = 200
DRAW_WIDTH = WIDTH - TOOLBAR_WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint with UI")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

colors = [BLACK, RED, GREEN, BLUE]
current_color = BLACK

# Режимы
mode = "brush"

brush_size = 5

# Холст
canvas = pygame.Surface((DRAW_WIDTH, HEIGHT))
canvas.fill(WHITE)

drawing = False
last_pos = None

# ---------------- КНОПКИ ----------------
def draw_button(rect, text, active):
    pygame.draw.rect(screen, DARK if active else GRAY, rect)
    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x + 10, rect.y + 10))

# позиции кнопок
buttons = {
    "brush": pygame.Rect(DRAW_WIDTH + 20, 50, 160, 40),
    "rect": pygame.Rect(DRAW_WIDTH + 20, 100, 160, 40),
    "circle": pygame.Rect(DRAW_WIDTH + 20, 150, 160, 40),
    "eraser": pygame.Rect(DRAW_WIDTH + 20, 200, 160, 40),
}

# ---------------- GAME LOOP ----------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------- КЛИК --------
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Проверка кнопок инструментов
            for tool, rect in buttons.items():
                if rect.collidepoint(mx, my):
                    mode = tool

            # Проверка палитры
            for i, color in enumerate(colors):
                rect = pygame.Rect(DRAW_WIDTH + 20 + i*40, 300, 30, 30)
                if rect.collidepoint(mx, my):
                    current_color = color

            # Если клик в зоне рисования
            if mx < DRAW_WIDTH:
                drawing = True
                last_pos = event.pos

                # СРАЗУ рисуем фигуру (по условию)
                if mode == "rect":
                    pygame.draw.rect(canvas, current_color,
                                     (mx, my, 50, 50), 2)

                elif mode == "circle":
                    pygame.draw.circle(canvas, current_color,
                                       (mx, my), 25, 2)

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos

            if mx < DRAW_WIDTH:
                if mode == "brush":
                    pygame.draw.line(canvas, current_color, last_pos, (mx, my), brush_size)

                elif mode == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, (mx, my), brush_size * 2)

                last_pos = (mx, my)

    # ---------------- ОТРИСОВКА ----------------
    screen.fill(GRAY)

    # Холст
    screen.blit(canvas, (0, 0))

    # Правая панель
    pygame.draw.rect(screen, (220, 220, 220), (DRAW_WIDTH, 0, TOOLBAR_WIDTH, HEIGHT))

    # Кнопки инструментов
    draw_button(buttons["brush"], "Brush", mode == "brush")
    draw_button(buttons["rect"], "Rectangle", mode == "rect")
    draw_button(buttons["circle"], "Circle", mode == "circle")
    draw_button(buttons["eraser"], "Eraser", mode == "eraser")

    # Палитра цветов
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (DRAW_WIDTH + 20 + i*40, 300, 30, 30))

    # Текущий цвет
    pygame.draw.rect(screen, current_color, (DRAW_WIDTH + 20, 350, 60, 30))
    text = font.render("Color", True, BLACK)
    screen.blit(text, (DRAW_WIDTH + 90, 355))

    pygame.display.update()
    clock.tick(60)

pygame.quit()