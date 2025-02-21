import psycopg2
from psycopg2.extras import RealDictCursor
from page_analyzer.config import Config
import requests
from bs4 import BeautifulSoup


def get_db_connection():
    """Создает соединение с БД."""
    return psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)


def get_url_by_name(url):
    """Возвращает запись из БД, если URL уже существует."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
            return cur.fetchone()  # Вернет None, если URL нет в базе


def drop_tables():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """DROP TABLE IF EXISTS urls;
                            DROP TABLE IF EXISTS url_checks;"""
            )
            conn.commit()


def create_tables():
    """Создает таблицы в БД."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            with open("database.sql", "r") as f:
                cur.execute(f.read())
            conn.commit()


def add_url(url):
    """Добавляет URL в БД, если его еще нет."""
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
    """Возвращает все URL из БД."""
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
    """Возвращает запись из БД по ID."""
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


def add_url_check(url_id):
    """Добавляет проверку URL в БД."""
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

            except requests.RequestException:
                return False


def get_checks_by_url(url_id):
    """Возвращает все проверки для указанного
    URL в порядке убывания даты создания."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC",
                (url_id,),
            )
            return cur.fetchall()


def get_last_check_date(url_id):
    """Возвращает дату последней проверки для указанного URL."""
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
