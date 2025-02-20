import psycopg2
from psycopg2.extras import RealDictCursor
from page_analyzer.config import Config
import requests
from bs4 import BeautifulSoup


# Функция для подключения к БД
def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)


def get_url_by_name(url):
    """Возвращает запись из БД, если URL уже существует."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
            return cur.fetchone()  # Вернет None, если URL нет в базе


# Функция для создания таблицы (исполняется один раз)
def create_tables():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("database.sql", "r") as f:
                cur.execute(f.read())
            conn.commit()


# Функция для добавления URL в БД
def add_url(url):
    existing_url = get_url_by_name(url)
    if existing_url:
        return existing_url["id"]  # Если URL уже есть, просто возвращаем его id
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url,))
            conn.commit()
            return cur.fetchone()["id"]


# Функция для получения всех URL
def get_all_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT urls.id, urls.name, urls.created_at,
                       (SELECT created_at FROM url_checks
                        WHERE url_checks.url_id = urls.id
                        ORDER BY created_at DESC
                        LIMIT 1) AS last_check
                FROM urls ORDER BY urls.created_at DESC
                """
            )
            return cur.fetchall()


# Функция для поиска URL по ID
def get_url_by_id(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            return cur.fetchone()


def get_url_checks(url_id):
    """Возвращает список проверок для указанного URL."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, status_code, h1, title, description, created_at FROM url_checks
                WHERE url_id = %s ORDER BY created_at DESC
                """,
                (url_id,),
            )
            return cur.fetchall()


# def add_url_check(url_id):
#     with get_db_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#                 """
#                 INSERT INTO url_checks (url_id, status_code, h1, title, description)
#                 VALUES (%s, NULL, NULL, NULL, NULL)
#                 RETURNING id, created_at
#             """,
#                 (url_id,),
#             )
#             conn.commit()
#             return cur.fetchone()
#   # Возвращаем id и created_at новой проверки
def add_url_check(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Получаем URL по ID
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            url_row = cur.fetchone()

            if not url_row:
                return None  # Если URL не найден

            url = url_row["name"]

            try:
                # Выполняем HTTP-запрос
                response = requests.get(url, timeout=5)
                response.raise_for_status()  # Вызывает исключение при ошибке HTTP

                status_code = response.status_code

                # Парсим HTML-страницу
                soup = BeautifulSoup(response.text, "html.parser")

                h1 = soup.h1.text.strip() if soup.h1 else None
                title = soup.title.text.strip() if soup.title else None
                description = None

                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    description = meta_desc["content"].strip()

                # Добавляем данные в таблицу url_checks
                cur.execute(
                    """
                    INSERT INTO url_checks (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (url_id, status_code, h1, title, description),
                )
                conn.commit()
                return True
                # return cur.fetchone()  # Возвращает ID и дату создания проверки

            except requests.RequestException:
                return False


def get_checks_by_url(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC",
                (url_id,),
            )
            return cur.fetchall()


def get_last_check_date(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT created_at FROM url_checks WHERE url_id = %s ORDER BY created_at DESC LIMIT 1
            """,
                (url_id,),
            )
            row = cur.fetchone()
            return row["created_at"] if row else None
