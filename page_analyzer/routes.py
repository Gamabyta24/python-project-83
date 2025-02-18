from flask import Flask, render_template, request, redirect, url_for, flash
import validators
from page_analyzer.models import (
    create_tables,
    add_url,
    get_all_urls,
    get_url_by_id,
    get_url_by_name,
    get_url_checks,
    add_url_check,
    get_last_check_date,
)
from page_analyzer.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Создаём таблицы при старте
create_tables()


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        url = request.form.get("url").strip()

        if not url or not validators.url(url) or len(url) > 255:
            error = "Введите корректный URL (до 255 символов)"
        else:
            existing_url = get_url_by_name(url)
            if existing_url:  # Если URL уже есть в БД
                flash("Этот URL уже существует", "warning")
            else:
                add_url(url)
                flash("URL успешно добавлен", "success")

            return redirect(url_for("show_urls"))

    return render_template("index.html", error=error)


@app.route("/urls")
def show_urls():
    urls = get_all_urls()
    for url in urls:
        url["last_check_date"] = get_last_check_date(
            url["id"]
        )  # Получаем дату последней проверки
    return render_template("urls.html", urls=urls)


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

    # Добавляем запись в таблицу url_checks с минимальными данными
    try:
        add_url_check(url_id)  # Функция для добавления записи в таблицу проверок
        flash("Проверка добавлена", "success")
    except Exception as ex:
        flash(f"Ошибка при добавлении проверки: {ex}", "danger")

    # Перенаправляем на страницу с деталями сайта
    return redirect(url_for("show_url", url_id=url_id))
