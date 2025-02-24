from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
import requests
import validators
from page_analyzer.models import (
    add_url,
    get_url_by_id,
    get_url_checks,
    get_db_connection,
)
from page_analyzer.config import Config
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from psycopg2.extras import RealDictCursor


app = Flask(__name__)
app.config.from_object(Config)


def normalized_url(url):
    parsed_url = urlparse(url)
    normalized_parsed_url = parsed_url._replace(
        path="", params="", query="", fragment=""
    ).geturl()
    return normalized_parsed_url.lower()


def is_validate(url):
    errors = {}
    is_valid = validators.url(url)
    if not is_valid:
        errors["name"] = "Некорректный URL"
    if len(url) > 255:
        errors["name"] = "Слишком длинный адрес"
    return errors


def get_id(url):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curr:
            curr.execute("SELECT id FROM urls WHERE name = %s", (url,))
            result = curr.fetchone()  # Может быть None, если записи нет

            if result is None:
                return None  # Обрабатываем случай, когда URL отсутствует

            return result.get("id")


def add_check(url_id, status_code, title, h1, content):
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


def find_seo(url):
    text = requests.get(url["name"]).text
    soup = BeautifulSoup(text, "lxml")
    h1 = None
    title = None
    meta = None
    content = None
    try:
        h1 = soup.h1.text
    except Exception:
        pass
    try:
        title = soup.title.text
    except Exception:
        pass
    meta = soup.select('meta[name="description"]')
    for attr in meta:
        content = attr.get("content")
    return {"title": title, "h1": h1, "content": content}


def get_content():
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


@app.route("/")
def index_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template("index.html", messages=messages)


@app.post("/urls")
def new_record():
    url = request.form.to_dict()
    error = is_validate(url["url"])
    if error:
        flash(error["name"], "alert-danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template("index.html", url=url["url"], messages=messages), 422
    normalize_url = normalized_url(url["url"])
    page_id = get_id(normalize_url)
    if page_id:
        flash("Страница уже существует", "alert-info")
        return redirect(url_for("site_page", id=page_id), code=302)
    else:
        url["id"] = add_url(normalize_url)
        flash("Страница успешно добавлена", "alert-success")
        return redirect(url_for("site_page", id=url["id"]), code=302)


@app.route("/urls/<int:id>")
def site_page(id):
    page = get_url_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    checks = get_url_checks(id)
    return render_template("url_detail.html", page=page, rows=checks, messages=messages)


@app.post("/urls/<id>/checks")
def check_page(id):
    url = get_url_by_id(id)
    try:
        req = requests.get(url["name"])
        req.raise_for_status()
    except Exception:
        flash("Произошла ошибка при проверке", "alert-danger")
        return redirect(url_for("site_page", id=id), code=302)
    status_code = req.status_code
    seo = find_seo(url)
    add_check(id, status_code, seo["title"], seo["h1"], seo["content"])
    flash("Страница успешно проверена", "alert-success")
    return redirect(url_for("site_page", id=id), code=302)


@app.route("/urls")
def all_pages():
    list_pages = get_content()
    messages = get_flashed_messages(with_categories=True)
    return render_template("urls.html", messages=messages, rows=list_pages)
