import pygame
import json
from game import run_game        # основная игровая функция из game.py
from db import get_leaderboard   # получение таблицы рекордов из базы данных

pygame.init()

screen = pygame.display.set_mode((400, 400))
font = pygame.font.SysFont(None, 28)  

# Доступные цвета змейки — игрок выбирает один из четырёх в настройках
COLORS = [
    [0, 200, 0],     # зелёный (по умолчанию)
    [255, 50, 50],   # красный
    [50, 150, 255],  # синий
    [255, 255, 0]    # жёлтый
]


def draw(t, x, y, c=(255, 255, 255)):
    # Вспомогательная функция: рисует текст t в позиции (x, y) заданным цветом c.
    # Белый цвет по умолчанию — не нужно каждый раз его указывать.
    screen.blit(font.render(t, True, c), (x, y))


def load_settings():
    # Загружает настройки из файла settings.json.
    # Если файл не существует или сломан — возвращаем безопасные дефолтные значения.
    try:
        return json.load(open("settings.json"))
    except:
        return {"snake_color": [0, 200, 0], "grid": True, "sound": False}


def save_settings(d):
    # Сохраняет текущие настройки в settings.json.
    # Вызывается когда игрок нажимает Enter в меню настроек.
    json.dump(d, open("settings.json", "w"))


settings = load_settings()

# Текущее состояние программы — определяет, что сейчас показывается на экране.
# Возможные значения: "menu", "input", "leaderboard", "settings", "gameover"
state = "menu"

username = ""     # имя игрока, которое он вводит перед началом игры
game_data = None  # результаты последней игры — приходят из run_game() как кортеж
color_index = 0   # индекс выбранного цвета змейки в списке COLORS

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()  

        if e.type == pygame.KEYDOWN:

            # Главное меню — выбор раздела цифрами
            if state == "menu":
                if e.key == pygame.K_1:
                    state = "input"        # переходим к вводу имени перед игрой
                if e.key == pygame.K_2:
                    state = "leaderboard"  # открываем таблицу рекордов
                if e.key == pygame.K_3:
                    state = "settings"     # открываем настройки
                if e.key == pygame.K_4:
                    exit()                 # выход из программы

            # Ввод имени — обычный текстовый ввод с поддержкой Backspace
            elif state == "input":
                if e.key == pygame.K_RETURN:
                    # Имя введено — запускаем игру и ждём её завершения.
                    # run_game возвращает кортеж ("gameover", ...) или ("menu", ).
                    game_data = run_game(username)
                    state = game_data[0]  # первый элемент — следующее состояние
                elif e.key == pygame.K_BACKSPACE:
                    username = username[:-1]  # стираем последний символ
                else:
                    username += e.unicode  # добавляем введённый символ к имени

            # Таблица рекордов — только выход по Q
            elif state == "leaderboard":
                if e.key == pygame.K_q:
                    state = "menu"

            # Настройки — переключение сетки, выбор цвета, сохранение
            elif state == "settings":

                if e.key == pygame.K_g:
                    # Переключаем отображение сетки на поле
                    settings["grid"] = not settings["grid"]

                # Клавиши 1-4 выбирают цвет змейки из списка COLORS
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    color_index = e.key - pygame.K_1  # K_1=0, K_2=1 и т.д.
                    settings["snake_color"] = COLORS[color_index]

                if e.key == pygame.K_RETURN:
                    save_settings(settings)  # записываем изменения в файл
                    state = "menu"           # и возвращаемся в главное меню

            # Экран конца игры — рестарт или выход
            elif state == "gameover":
                if e.key == pygame.K_r:
                    state = "input"  # начать заново — возвращаемся к вводу имени
                    username = ""    # очищаем имя, чтобы ввести заново
                if e.key == pygame.K_q:
                    exit()

    # Отрисовка текущего экрана
    screen.fill((0, 0, 0))  # каждый кадр начинаем с чёрного фона

    if state == "menu":
        # Четыре пункта меню, каждый своим цветом для визуального разделения
        draw("1 - PLAY",        140, 120, (0, 255, 0))
        draw("2 - LEADERBOARD", 110, 160, (255, 255, 0))
        draw("3 - SETTINGS",    120, 200, (0, 150, 255))
        draw("4 - QUIT",        140, 240, (255, 80, 80))

    elif state == "input":
        draw("ENTER NAME:", 120, 120)
        draw(username,      120, 160)  # показываем что уже напечатано

    elif state == "leaderboard":
        draw("LEADERBOARD (Q to exit)", 70, 40, (255, 255, 0))

        data = get_leaderboard()  # запрашиваем топ-10 из базы данных
        y = 80
        for i, r in enumerate(data):
            # r — кортеж (username, score, level_reached, played_at)
            draw(f"{i+1}. {r[0]} {r[1]} lvl:{r[2]}", 30, y)
            y += 25  # каждая строка чуть ниже предыдущей

    elif state == "settings":
        draw("SETTINGS", 160, 40)

        draw("G - grid toggle", 100, 120)
        draw(f"Grid: {settings['grid']}", 100, 150)  # текущее состояние сетки

        draw("1-4 - snake color", 100, 200)

        # Рисуем четыре цветных квадрата для выбора цвета змейки.
        # Вокруг выбранного — белая рамка толщиной 2 пикселя.
        for i, c in enumerate(COLORS):
            pygame.draw.rect(screen, c, (100 + i * 40, 250, 30, 30))
            if settings["snake_color"] == c:
                pygame.draw.rect(screen, (255, 255, 255), (100 + i * 40, 250, 30, 30), 2)

        draw("ENTER - SAVE & BACK", 80, 320)

    elif state == "gameover":
        # Распаковываем результаты игры — первый элемент ("gameover") нам здесь не нужен
        _, score, level, best = game_data

        draw("GAME OVER",      140, 80,  (255, 0, 0))
        draw(f"SCORE: {score}", 120, 140)
        draw(f"LEVEL: {level}", 120, 180)
        draw(f"BEST: {best}",   120, 220)  # лучший результат игрока за все партии

        draw("R - RESTART", 120, 280, (0, 255, 0))
        draw("Q - QUIT",    120, 310, (255, 80, 80))

    pygame.display.flip()  # показываем готовый кадр на экране