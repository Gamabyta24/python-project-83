from flask import Flask, render_template, request, redirect, url_for, flash
import validators
from page_analyzer.models import create_tables, add_url, get_all_urls, get_url_by_id
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
            try:
                add_url(url)
                flash("URL успешно добавлен", "success")
                return redirect(url_for("show_urls"))
            except Exception as ex:
                flash("Этот URL уже существует", "warning", ex)

    return render_template("index.html", error=error)


@app.route("/urls")
def show_urls():
    urls = get_all_urls()
    return render_template("urls.html", urls=urls)


@app.route("/urls/<int:url_id>")
def show_url(url_id):
    url = get_url_by_id(url_id)
    if not url:
        flash("URL не найден", "danger")
        return redirect(url_for("show_urls"))

    return render_template("url_detail.html", url=url)
