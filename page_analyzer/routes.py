from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
import validators
from page_analyzer.models import (
    add_url,
    get_all_urls,
    get_url_by_id,
    get_url_by_name,
    get_url_checks,
    add_url_check,
    get_last_check_date,
)
from page_analyzer.config import Config
from urllib.parse import urlparse

app = Flask(__name__)
app.config.from_object(Config)

# Создаём таблицы при старте


# @app.route("/", methods=["GET", "POST"])
# def index():
#     url_id = None
#     messages = get_flashed_messages(with_categories=True)
#     if request.method == "POST":
#         url = request.form.get("url").strip()

#         if not url or not validators.url(url) or len(url) > 255:
#             flash("Некорректный URL", "danger")
#             return render_template("index.html")
#         else:
#             existing_url = get_url_by_name(url)
#             if existing_url:  # Если URL уже есть в БД
#                 url_id = existing_url["id"]
#                 flash("Страница уже существует", "info")
#             else:
#                 url_id = add_url(url)
#                 flash("Страница успешно добавлена", "success")

#             return redirect(url_for("show_url", url_id=url_id))


#     return render_template("index.html",messages=messages)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url").strip()

        if not url or not validators.url(url) or len(url) > 255:
            flash("Некорректный URL", "danger")
            return render_template(
                "index.html"
            )  # Просто рендерим страницу, без вызова get_flashed_messages()

        existing_url = get_url_by_name(url)
        if existing_url:
            flash("Страница уже существует", "info")
            return redirect(url_for("show_url", url_id=existing_url["id"]))

        url_id = add_url(url)
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("show_url", url_id=url_id))

    return render_template("index.html")


# @app.route("/urls")
# def show_urls():
#     urls = get_all_urls()
#     for url in urls:
#         url["last_check_date"] = get_last_check_date(url["id"])
#         url_checks = get_url_checks(url["id"])
#         last_check = url_checks[0] if url_checks else None
#         url["last_status_code"] = last_check["status_code"] if last_check else None
#         # Получаем дату последней проверки
#     return render_template("urls.html", urls=urls)


@app.route("/urls/<int:url_id>")
def show_url(url_id):
    url = get_url_by_id(url_id)
    url_checks = get_url_checks(url_id)
    if not url:
        flash("URL не найден", "danger")
        return redirect(url_for("show_urls"))

    return render_template("url_detail.html", url=url, url_checks=url_checks)


@app.route("/urls/<int:url_id>/checks", methods=["POST"])
def add_check(url_id):
    # Проверяем, существует ли сайт с данным url_id
    url = get_url_by_id(url_id)
    if not url:
        flash("Сайт не найден", "danger")
        return redirect(url_for("show_url", url_id=url_id))
    success = add_url_check(url_id)
    if success:
        flash("Страница успешно проверена", "success")
    else:
        flash("Произошла ошибка при проверке", "danger")

    # Перенаправляем на страницу с деталями сайта
    return redirect(url_for("show_url", url_id=url_id))


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


@app.post("/urls")
def new_record():
    url = request.form.to_dict()
    error = is_validate(url["url"])
    if error:
        flash(error["name"], "alert-danger")
        messages = get_flashed_messages(with_categories=True)
        return (
            render_template("index.html", url=url["url"], messages=messages),
            422,
        )
    normalize_url = normalized_url(url["url"])
    page_id = get_url_by_name(normalize_url)
    if page_id:
        flash("Страница уже существует", "alert-info")
        return redirect(url_for("site_page", id=page_id), code=302)
    else:
        url["id"] = add_url(normalize_url)
        flash("Страница успешно добавлена", "alert-success")
        return redirect(url_for("show_url", id=url["id"]), code=302)


@app.route("/urls")
def all_pages():
    list_pages = get_all_urls()
    messages = get_flashed_messages(with_categories=True)
    for url in list_pages:
        url["last_check_date"] = get_last_check_date(url["id"])
        url_checks = get_url_checks(url["id"])
        last_check = url_checks[0] if url_checks else None
        url["last_status_code"] = last_check["status_code"] if last_check else None
    return render_template("urls.html", messages=messages, urls=list_pages)
