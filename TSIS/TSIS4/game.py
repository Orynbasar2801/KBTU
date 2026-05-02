import pygame
import random
import json
from db import save_game, get_best_score
from config import WIDTH, HEIGHT, CELL    


def load_settings():
    # Загружает пользовательские настройки из файла settings.json.
    # Если файл не найден или повреждён — возвращаем дефолтные значения,
    # чтобы игра запускалась даже без файла настроек.
    try:
        return json.load(open("settings.json"))
    except:
        return {"snake_color": [0, 200, 0], "grid": True, "sound": False}


def random_pos(exclude):
    # Генерирует случайную позицию на сетке, которая не совпадает ни с одной из переданных.
    # exclude — список занятых клеток (тело змейки, еда, препятствия и т.д.).
    # Крутится в цикле до тех пор, пока не найдёт свободное место.
    while True:
        p = (random.randrange(0, WIDTH, CELL),
             random.randrange(0, HEIGHT, CELL))
        if p not in exclude:
            return p


def run_game(username):
    # Основная функция игры. Запускает полный игровой цикл для конкретного игрока.
    # Возвращает кортеж с результатом: ("menu",) если игрок закрыл окно,
    # или ("gameover", score, level, best) когда игра заканчивается.

    settings = load_settings()  # читаем настройки — цвет змейки, сетка, звук

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)  # стандартный шрифт, размер 24

    # Змейка — список клеток от головы к хвосту. Начинаем с двух сегментов.
    snake = [(100, 100), (80, 100)]
    direction = (CELL, 0)   # изначально двигаемся вправо
    next_dir = direction    # следующий запланированный поворот (применяется в начале шага)

    # Цвета для иконок бафов в HUD — используются при отрисовке таймера баффа
    BUFF_COLORS = {
        "speed": (255, 255, 0),    # жёлтый — ускорение
        "slow": (255, 140, 0),     # оранжевый — замедление
        "shield": (0, 200, 255)    # голубой — щит
    }

    # Цвета всех игровых объектов на поле
    COLORS = {
        "snake": (0, 220, 0),
        "food": (255, 50, 50),        # красная еда — даёт очко
        "poison": (120, 0, 0),        # тёмно-красный яд — отнимает очко и укорачивает змейку
        "obstacle": (120, 120, 120),  # серые препятствия — появляются с 3-го уровня
        "power": (255, 255, 0)        # жёлтый — цвет бонуса (переопределяется ниже по типу)
    }

    # Цвета бонусных клеток на поле — совпадают с BUFF_COLORS для единообразия
    POWER_COLORS = {
        "speed": (255, 255, 0),    # жёлтый
        "slow": (255, 140, 0),     # оранжевый
        "shield": (0, 200, 255)    # голубой
    }

    buff_text = ""   # текст активного баффа, который показывается в HUD
    buff_end = 0     # время (в мс), когда текст баффа нужно убрать

    score = 0
    level = 1
    last_level = -1  # запоминаем счёт при последнем повышении уровня, чтобы не повышать его дважды

    best = get_best_score(username)  # лучший результат игрока из базы данных

    food = random_pos(snake)                    # случайная позиция еды, не на змейке
    poison = random_pos(snake + [food])         # яд — не на змейке и не на еде

    obstacles = []   # препятствия появятся позже, при достижении 3-го уровня

    power = None        # текущая позиция бонуса на поле (None = бонуса нет)
    power_type = None   # тип бонуса: "speed", "slow" или "shield"

    active_power = None  # какой бафф сейчас активен на змейке
    power_end = 0        # время окончания активного баффа

    buff_text = ""  # (повторная инициализация для читаемости — значение то же)
    buff_end = 0

    shield_active = False  # щит поглощает одно столкновение и исчезает

    # Ускорение не применяется мгновенно — есть задержка в 1 секунду после подбора
    pending_speed = False      # флаг: скорость подобрана, но ещё не активирована
    speed_trigger_time = 0     # момент времени, когда ускорение должно включиться

    def gen_obstacles():
        # Генерирует 5 препятствий, которые не перекрывают голову змейки
        # и появляются на достаточном расстоянии от неё (больше 3 клеток по каждой оси).
        obs = []
        head = snake[0]

        def safe(p):
            # Проверяем, что препятствие не слишком близко к голове змейки
            return abs(p[0] - head[0]) > CELL * 3 or abs(p[1] - head[1]) > CELL * 3

        for _ in range(5):
            while True:
                p = random_pos(snake + obs + [food, poison])
                if safe(p):
                    obs.append(p)
                    break

        return obs

    running = True

    while running:

        now = pygame.time.get_ticks()  # текущее время в миллисекундах с момента запуска pygame

        # Проверяем, не пора ли активировать отложенное ускорение
        if pending_speed and now >= speed_trigger_time:
            active_power = "speed"
            power_end = now + 6000   # ускорение работает 6 секунд
            buff_text = "SPEED"
            buff_end = power_end
            pending_speed = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return ("menu",)  # закрыл окно — возвращаемся в меню

            if e.type == pygame.KEYDOWN:
                nd = None
                if e.key == pygame.K_w: nd = (0, -CELL)   # вверх
                if e.key == pygame.K_s: nd = (0, CELL)    # вниз
                if e.key == pygame.K_a: nd = (-CELL, 0)   # влево
                if e.key == pygame.K_d: nd = (CELL, 0)    # вправо

                # Запрещаем разворот на 180° — нельзя сразу пойти в противоположную сторону
                if nd and nd != (-direction[0], -direction[1]):
                    next_dir = nd

        direction = next_dir
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])  # новая позиция головы

        # Столкновение с телом змейки или препятствием
        if head in snake or head in obstacles:
            if shield_active:
                shield_active = False  # щит поглощает удар и сгорает
            else:
                break  # конец игры

        # Выход за границы поля
        if head[0] < 0 or head[1] < 0 or head[0] >= WIDTH or head[1] >= HEIGHT:
            if shield_active:
                shield_active = False  # щит спасает один раз
                # Телепортируем голову обратно в ближайшую допустимую позицию у края
                head = (
                    max(0, min(head[0], WIDTH - CELL)),
                    max(0, min(head[1], HEIGHT - CELL))
                )
                snake[0] = head
            else:
                break  # конец игры

        snake.insert(0, head)  # добавляем новую голову в начало списка

        # Змейка съела еду — даём очко и спавним еду на новом месте
        if head == food:
            score += 1
            food = random_pos(snake + obstacles + [poison])

        elif head == poison:
            # Змейка наткнулась на яд — минус очко и минус два сегмента хвоста
            score = max(0, score - 1)
            snake = snake[:-2] if len(snake) > 2 else []
            poison = random_pos(snake + obstacles + [food])
            if len(snake) <= 1:
                break  # змейка стала слишком короткой — конец игры

        else:
            snake.pop()  # обычный шаг — убираем хвост, змейка не растёт

        # Каждые 5 очков — новый уровень. last_level защищает от повторного срабатывания
        if score % 5 == 0 and score != last_level:
            level += 1
            last_level = score

            if level >= 3:
                obstacles = gen_obstacles()  # начиная с 3-го уровня добавляем препятствия

        # Бонус исчезает сам через 8 секунд, если его не подобрали
        if power and now - power_spawn_time > 8000:
            power = None
            power_type = None

        # Спавним новый бонус, если на поле его сейчас нет и никакой бафф не активен
        if not power and not active_power:
            power = random_pos(snake + obstacles + [food, poison])
            power_type = random.choice(["speed", "slow", "shield"])
            power_spawn_time = now  # запоминаем время появления, чтобы потом убрать по таймеру

        # Змейка подобрала бонус
        if power and head == power:

            if power_type == "speed":
                # Ускорение не мгновенное — включится через 1 секунду (чтобы игрок успел подготовиться)
                pending_speed = True
                speed_trigger_time = now + 1000
                buff_text = "SPEED"
                buff_end = now + 6000

            elif power_type == "slow":
                active_power = "slow"
                power_end = now + 6000  # замедление на 6 секунд
                buff_text = "SLOW"
                buff_end = power_end

            elif power_type == "shield":
                shield_active = True
                buff_text = "SHIELD"
                buff_end = now + 6000  # визуальный таймер щита (сам щит живёт до первого удара)

            power = None  # бонус подобран — убираем с поля

        # Проверяем, не истёк ли активный бафф
        if active_power and now > power_end:
            active_power = None

        # Убираем текст баффа из HUD когда его время вышло
        if buff_text and now > buff_end:
            buff_text = ""

        # Рассчитываем текущую скорость (кадров в секунду)
        base = 8 + score // 10  # базовая скорость растёт по мере набора очков

        if active_power == "speed":
            speed_now = 10   # ускорение фиксирует скорость на 10 FPS
        elif active_power == "slow":
            speed_now = 5    # замедление снижает до 5 FPS
        else:
            speed_now = base # обычный режим

        # Отрисовка кадра
        screen.fill((0, 0, 0))  # очищаем экран чёрным фоном

        # Рисуем сетку, если она включена в настройках
        if settings["grid"]:
            for x in range(0, WIDTH, CELL):
                pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))

        # Рисуем тело змейки цветом из настроек пользователя
        for s in snake:
            pygame.draw.rect(screen, settings["snake_color"], (s[0], s[1], CELL, CELL))

        pygame.draw.rect(screen, COLORS["food"],     (food[0],   food[1],   CELL, CELL))
        pygame.draw.rect(screen, COLORS["poison"],   (poison[0], poison[1], CELL, CELL))

        for o in obstacles:
            pygame.draw.rect(screen, COLORS["obstacle"], (o[0], o[1], CELL, CELL))

        # Рисуем бонус нужным цветом в зависимости от его типа
        if power:
            color = POWER_COLORS.get(power_type, (255, 255, 255))
            pygame.draw.rect(screen, color, (power[0], power[1], CELL, CELL))

        # HUD — верхняя левая часть экрана
        x, y = 10, 10

        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (x, y))
        y += 20

        screen.blit(font.render(f"Best: {best}", True, (255, 255, 0)), (x, y))  # рекорд жёлтым
        y += 20

        y += 20  # пустая строка для отступа перед статусом щита

        shield_text = "YES" if shield_active else "NO"
        screen.blit(font.render(f"Shield: {shield_text}", True, (255, 255, 255)), (x, y))

        # Показываем активный бафф с обратным отсчётом в секундах
        if buff_text:
            remaining = max(0, (buff_end - now) // 1000)  # переводим мс в секунды
            color = BUFF_COLORS.get(buff_text.lower(), (255, 255, 255))
            screen.blit(
                font.render(f"{buff_text} ({remaining}s)", True, color),
                (10, 50)
            )

        # Предупреждение по центру экрана: ускорение вот-вот включится
        if pending_speed:
            warn = font.render("INCOMING SPEED", True, (255, 0, 0))
            screen.blit(warn, (WIDTH // 2 - 80, 10))

        pygame.display.flip()       # показываем готовый кадр
        clock.tick(speed_now)       # ждём следующего кадра согласно текущей скорости

    # Игра завершена — сохраняем результат и возвращаем данные для экрана "Game Over"
    save_game(username, score, level)
    return ("gameover", score, level, best)