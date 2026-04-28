import pygame
import math

pygame.init()
WIDTH, HEIGHT = 900, 600
TOOLBAR_WIDTH = 200
DRAW_WIDTH = WIDTH - TOOLBAR_WIDTH
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 24)

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK = (100, 100, 100)
BLACK = (0, 0, 0)

# Список доступных цветов для выбора
palette = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), 
    (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 128)
]
current_color = BLACK
mode = "brush"

canvas = pygame.Surface((DRAW_WIDTH, HEIGHT))
canvas.fill(WHITE)
drawing = False

# Кнопки инструментов
buttons = {
    "brush": pygame.Rect(DRAW_WIDTH + 20, 50, 160, 30),
    "rect": pygame.Rect(DRAW_WIDTH + 20, 90, 160, 30),
    "circle": pygame.Rect(DRAW_WIDTH + 20, 130, 160, 30),
    "square": pygame.Rect(DRAW_WIDTH + 20, 170, 160, 30),
    "right_tri": pygame.Rect(DRAW_WIDTH + 20, 210, 160, 30),
    "eq_tri": pygame.Rect(DRAW_WIDTH + 20, 250, 160, 30),
    "rhombus": pygame.Rect(DRAW_WIDTH + 20, 290, 160, 30),
}

def draw_ui():
    # Фон панели управления
    pygame.draw.rect(screen, (220, 220, 220), (DRAW_WIDTH, 0, TOOLBAR_WIDTH, HEIGHT))
    
    # Рисуем кнопки инструментов
    for tool, rect in buttons.items():
        pygame.draw.rect(screen, DARK if mode == tool else GRAY, rect)
        text = font.render(tool.replace("_", " ").capitalize(), True, BLACK)
        screen.blit(text, (rect.x + 5, rect.y + 5))
    
    # РАЗДЕЛ: ВЫБОР ЦВЕТОВ (ПАЛИТРА)
    start_y = 350
    label = font.render("Select Color:", True, BLACK)
    screen.blit(label, (DRAW_WIDTH + 20, start_y))
    
    for i, color in enumerate(palette):
        # Рисуем квадраты палитры в 2 ряда
        rect = pygame.Rect(DRAW_WIDTH + 20 + (i % 4) * 40, start_y + 30 + (i // 4) * 40, 35, 35)
        pygame.draw.rect(screen, color, rect)
        # Если цвет выбран — рисуем обводку
        if current_color == color:
            pygame.draw.rect(screen, BLACK, rect, 2)

running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1. Проверка клика по инструментам
            for tool, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    mode = tool
            
            # 2. Проверка клика по палитре цветов
            start_y = 350
            for i, color in enumerate(palette):
                color_rect = pygame.Rect(DRAW_WIDTH + 20 + (i % 4) * 40, start_y + 30 + (i // 4) * 40, 35, 35)
                if color_rect.collidepoint(event.pos):
                    current_color = color

            # 3. Рисование фигур
            if mx < DRAW_WIDTH:
                drawing = True
                if mode == "rect": pygame.draw.rect(canvas, current_color, (mx, my, 80, 50), 2)
                elif mode == "square": pygame.draw.rect(canvas, current_color, (mx, my, 50, 50), 2)
                elif mode == "circle": pygame.draw.circle(canvas, current_color, (mx, my), 30, 2)
                elif mode == "right_tri":
                    pygame.draw.polygon(canvas, current_color, [(mx, my), (mx, my + 50), (mx + 50, my + 50)], 2)
                elif mode == "eq_tri":
                    h = int((math.sqrt(3)/2) * 50)
                    pygame.draw.polygon(canvas, current_color, [(mx, my), (mx - 25, my + h), (mx + 25, my + h)], 2)
                elif mode == "rhombus":
                    pygame.draw.polygon(canvas, current_color, [(mx, my - 30), (mx + 20, my), (mx, my + 30), (mx - 20, my)], 2)

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        if event.type == pygame.MOUSEMOTION and drawing and mx < DRAW_WIDTH:
            if mode == "brush":
                pygame.draw.circle(canvas, current_color, (mx, my), 5)

    screen.fill(GRAY)
    screen.blit(canvas, (0, 0))
    draw_ui()
    pygame.display.update()

pygame.quit()