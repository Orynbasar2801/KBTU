import psycopg2
from config import DB_CONFIG  # настройки подключения к БД лежат отдельно в config.py


def connect():
    # Открывает новое соединение с базой данных, используя параметры из DB_CONFIG.
    # Вызывается в начале каждой функции — намеренно не держим одно соединение на всю программу.
    return psycopg2.connect(**DB_CONFIG)


def get_player_id(username):
    # Возвращает ID игрока по его нику.
    # Если такого игрока ещё нет в базе — автоматически создаёт его и возвращает новый ID.
    # Это называется "get or create" — не нужно регистрироваться отдельно перед игрой.
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    result = cur.fetchone()

    if result:
        # Игрок уже существует — просто берём его ID
        player_id = result[0]
    else:
        # Игрок новый — добавляем запись и сразу получаем присвоенный ID через RETURNING
        cur.execute(
            "INSERT INTO players(username) VALUES(%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()  # фиксируем нового игрока в базе

    cur.close()
    conn.close()
    return player_id


def save_game(username, score, level):
    # Сохраняет результат одной игровой сессии: кто играл, сколько очков набрал и до какого уровня дошёл.
    # Время окончания партии записывается автоматически на стороне базы (DEFAULT NOW()).
    conn = connect()
    cur = conn.cursor()

    # Получаем ID игрока (или создаём его, если играет впервые)
    player_id = get_player_id(username)

    cur.execute("""
        INSERT INTO game_sessions(player_id, score, level_reached)
        VALUES(%s, %s, %s)
    """, (player_id, score, level))

    conn.commit()  # без этого запись не сохранится в базе
    cur.close()
    conn.close()


def get_leaderboard():
    # Возвращает топ-10 лучших результатов среди всех игроков.
    # Результаты отсортированы по очкам от большего к меньшему.
    # JOIN нужен, чтобы вместо числового player_id вытащить читаемый username.
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, score, level_reached, played_at
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        ORDER BY score DESC
        LIMIT 10
    """)

    data = cur.fetchall()  # забираем сразу все 10 строк

    cur.close()
    conn.close()
    return data


def get_best_score(username):
    # Возвращает лучший (максимальный) счёт конкретного игрока за все его партии.
    # Если игрок ни разу не играл или такого ника нет — воз