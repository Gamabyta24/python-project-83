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
from page_analyzer.utility_bd import (
    add_url,
    get_url_by_id,
    get_url_checks,
    get_id,
    get_content,
    add_check,
)
from page_analyzer.utility_check import is_validate, normalized_url, find_seo
from page_analyzer.config import Config


app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def index_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template("index.html", messages=messages)


@app.post("/urls")
def create_new_url():
    url = request.form.to_dict()
    error = is_validate(url["url"])
    if error:
        flash(error["name"], "alert-danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            "index.html",
            url=url["url"],
            messages=messages
            ), 422
    normalize_url = normalized_url(url["url"])
    page_id = get_id(normalize_url)
    if page_id:
        flash("Страница уже существует", "alert-info")
        return redirect(url_for("site_page", id=page_id), code=302)
    url["id"] = add_url(normalize_url)
    flash("Страница успешно добавлена", "alert-success")
    return redirect(url_for("site_page", id=url["id"]), code=302)


@app.route("/urls/<int:id>")
def site_page(id):
    page = get_url_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    checks = get_url_checks(id)
    return render_template(
        "url_detail.html",
        page=page, rows=checks,
        messages=messages
        )


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
