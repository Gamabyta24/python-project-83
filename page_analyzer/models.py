import psycopg2
from psycopg2.extras import RealDictCursor
from page_analyzer.config import Config


# Функция для подключения к БД
def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)


# Функция для создания таблицы (исполняется один раз)
def create_tables():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("database.sql", "r") as f:
                cur.execute(f.read())
            conn.commit()


# Функция для добавления URL в БД
def add_url(url):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url,))
            conn.commit()
            return cur.fetchone()["id"]


# Функция для получения всех URL
def get_all_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls ORDER BY created_at DESC"
            )
            return cur.fetchall()


# Функция для поиска URL по ID
def get_url_by_id(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            return cur.fetchone()
