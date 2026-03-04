"""Модуль для работы с базой данных результатов игры.

Предоставляет функции инициализации БД, сохранения и получения лучших результатов.
"""


import sqlite3
import datetime


DB_NAME = "results.db"


def init_db():
    """Создаёт таблицу Savegames, если она не существует."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Savegames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time REAL NOT NULL
            )
        """)


def save_result(total_time: float):
    """Сохраняет результат игры: текущую дату/время и время в секундах.

    :param total_time: общее время игры в секундах
    :type total_time: float
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Savegames (date, time) VALUES (?, ?)", (now, total_time))


def get_top_results(limit: int = 10):
    """Возвращает список лучших результатов, отсортированных по убыванию времени.

    :param limit: максимальное количество записей (по умолчанию 10)
    :type limit: int
    :return: список кортежей (дата, время)
    :rtype: list[tuple[str, float]]
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, time FROM Savegames ORDER BY time DESC LIMIT ?", (limit,))
        return cursor.fetchall()
