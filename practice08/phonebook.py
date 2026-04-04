import json
from connect import get_connection

# --- ЗАДАНИЕ 1: ПОИСК ---
def test_task1_search():
    print("\n[Тест 1] Поиск по паттерну:")
    conn = get_connection()
    cur = conn.cursor()
    # Пробуем найти по имени и по части номера
    queries = ['Aliya', '707', 'Bolatov']
    for i, q in enumerate(queries, 1):
        cur.execute("SELECT * FROM search_contacts(%s);", (q,))
        print(f"  1.{i} Результат для '{q}': {cur.fetchall()}")
    cur.close()
    conn.close()

# --- ЗАДАНИЕ 2: ВСТАВКА/ОБНОВЛЕНИЕ ---
def test_task2_upsert():
    print("\n[Тест 2] Вставка и обновление (Upsert):")
    conn = get_connection()
    cur = conn.cursor()
    # 2.1 Новая запись
    cur.execute("CALL upsert_contact('Dmitry', 'Test', '87001112233');")
    print("  2.1 Контакт Dmitry добавлен.")
    # 2.2 Обновление телефона для того же имени
    cur.execute("CALL upsert_contact('Dmitry', 'Test', '87779990000');")
    print("  2.2 Телефон для Dmitry обновлен.")
    conn.commit()
    cur.close()
    conn.close()

# --- ЗАДАНИЕ 3: МАССОВАЯ ВСТАВКА (JSON) ---
def test_task3_bulk():
    print("\n[Тест 3] Массовая вставка с валидацией:")
    conn = get_connection()
    cur = conn.cursor()
    data = [
        {"first_name": "Valid1", "last_name": "User", "phone_number": "12345"},
        {"first_name": "Invalid1", "last_name": "User", "phone_number": "ABC-123"} # Ошибка
    ]
    cur.execute("CALL insert_many_contacts(%s, NULL);", (json.dumps(data),))
    incorrect = cur.fetchone()[0]
    print(f"  3.1 Список некорректных записей: {incorrect}")
    conn.commit()
    cur.close()
    conn.close()

# --- ЗАДАНИЕ 4: ПАГИНАЦИЯ ---
def test_task4_pagination():
    print("\n[Тест 4] Пагинация (LIMIT/OFFSET):")
    conn = get_connection()
    cur = conn.cursor()
    # Берем по 2 записи
    cur.execute("SELECT * FROM get_contacts_paginated(2, 0);")
    print(f"  4.1 Первая страница (2 записи): {cur.fetchall()}")
    cur.execute("SELECT * FROM get_contacts_paginated(2, 2);")
    print(f"  4.2 Вторая страница (отступ 2): {cur.fetchall()}")
    cur.close()
    conn.close()

# --- ЗАДАНИЕ 5: УДАЛЕНИЕ ---
def test_task5_delete():
    print("\n[Тест 5] Удаление данных:")
    conn = get_connection()
    cur = conn.cursor()
    # Удаляем по имени или номеру
    cur.execute("CALL delete_contact('Dmitry');")
    print("  5.1 Запрос на удаление 'Dmitry' выполнен.")
    cur.execute("CALL delete_contact('12345');")
    print("  5.2 Запрос на удаление номера '12345' выполнен.")
    conn.commit()
    cur.close()
    conn.close()

# --- ГЛАВНЫЙ ЗАПУСК ---
if __name__ == "__main__":
    
    test_task1_search()
    test_task2_upsert()
    test_task3_bulk()
    test_task4_pagination()
    test_task5_delete()
    
    print("\nПрограмма завершена. Выбери нужный тест в коде.")