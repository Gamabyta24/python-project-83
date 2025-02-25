import psycopg2
from psycopg2.extras import RealDictCursor
from page_analyzer.config import Config


def get_db_connection():
    """Создает соединение с БД."""
    return psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)


def get_url_by_name(url):
    """Возвращает запись из БД, если URL уже существует."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
            return cur.fetchone()  # Вернет None, если URL нет в базе


def add_url(url):
    """Добавляет URL в БД, если его еще нет."""
    existing_url = get_url_by_name(url)
    valid_url = url.lower()
    if existing_url:
        return existing_url["id"]  # Если URL уже есть, просто возвращаем его id
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id", (valid_url,)
            )
            conn.commit()
            return cur.fetchone()["id"]


def get_url_by_id(url_id):
    """Возвращает запись из БД по ID."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            return cur.fetchone()


def get_content():
    """
    Получает список URL-адресов с последними проверками.

    Создает временное `filter`, содержит id URL и максимальный id проверки.
    Затем извлекает данные из таблицы `urls`, дополняя их информацией
    о последней проверке из `url_checks`.

    Возвращает список словарей с данными URL и последней проверки.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curr:
            curr.execute(
                """
                    DROP VIEW IF EXISTS filter;

                    CREATE VIEW filter AS
                    SELECT url_id, MAX(id) AS max_id FROM url_checks
                    GROUP BY url_id;

                    SELECT urls.id,
                        name,
                        max_id,
                        status_code,
                        url_checks.created_at
                    FROM urls
                    LEFT JOIN filter
                    ON urls.id = filter.url_id
                    LEFT JOIN url_checks
                    ON url_checks.id = filter.max_id
                    ORDER BY url_checks.created_at DESC, name;"""
            )
            result = curr.fetchall()
            return result


def get_url_checks(url_id):
    """
    Возвращает список проверок для указанного URL.

    Данные берутся из таблицы `url_checks`, сортируются по id.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, status_code,
                h1,
                title,
                description,
                created_at FROM url_checks
                WHERE url_id = %s ORDER BY id DESC
                """,
                (url_id,),
            )
            return cur.fetchall()


def add_check(url_id, status_code, title, h1, content):
    """
    Добавляет новую запись о проверке URL в базу данных.

    Записывает `url_id`, HTTP-статус, заголовок h1, title и описание.
    """
    with get_db_connection() as conn:
        with conn.cursor() as curr:
            curr.execute(
                """
                    INSERT INTO url_checks (
                        url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s);
                        """,
                (url_id, status_code, h1, title, content),
            )


def get_id(url):
    """
    Ищет ID переданного URL в таблице `urls`.

    Если URL найден, возвращает его ID. Если нет – возвращает None.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curr:
            curr.execute("SELECT id FROM urls WHERE name = %s", (url,))
            result = curr.fetchone()

            if result is None:
                return None

            return result.get("id")
