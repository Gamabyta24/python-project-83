from urllib.parse import urlparse, urlunparse
import validators
from bs4 import BeautifulSoup
import requests


def normalized_url(url):
    """
    Приводит URL к стандартному виду, убирая путь, параметры и фрагменты.

    Возвращает нормализованный URL в нижнем регистре.
    """
    parsed_url = urlparse(url)
    normalized_parsed_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, "", "", "", "")
    )
    return normalized_parsed_url.lower()


def is_validate(url):
    """
    Проверяет корректность переданного URL.

    Возвращает словарь ошибок, если URL некорректен или превышает 255 символов.
    """
    errors = {}
    is_valid = validators.url(url)
    if not is_valid:
        errors["name"] = "Некорректный URL"
    if len(url) > 255:
        errors["name"] = "Слишком длинный адрес"
    return errors


def find_seo(url):
    """
    Выполняет HTTP-запрос к переданному URL и анализирует HTML-код.

    Извлекает заголовок h1, title и meta-описание (description).

    Возвращает словарь с найденными значениями.
    """
    text = requests.get(url["name"]).text
    soup = BeautifulSoup(text, "lxml")
    h1 = soup.h1.text if soup.h1 else ""
    title = soup.title.text if soup.title else ""
    meta = soup.select('meta[name="description"]')
    content = meta[0].get("content") if meta and meta[0].get("content") else ""
    return {"title": title, "h1": h1, "content": content}
