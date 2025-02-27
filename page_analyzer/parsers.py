from bs4 import BeautifulSoup
import requests


def find_seo(url):
    """
    Выполняет HTTP-запрос к переданному URL и анализирует HTML-код.

    Извлекает заголовок h1, title и meta-описание (description).

    Возвращает словарь с найденными значениями.
    """
    soup = BeautifulSoup(url, "lxml")
    h1 = soup.h1.text if soup.h1 else ""
    title = soup.title.text if soup.title else ""
    meta = soup.select('meta[name="description"]')
    content = meta[0].get("content") if meta and meta[0].get("content") else ""
    return {"title": title, "h1": h1, "content": content}
