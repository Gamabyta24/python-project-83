from urllib.parse import urlparse, urlunparse
import validators
def normalize_url(url):
    """
    Приводит URL к стандартному виду, убирая путь, параметры и фрагменты.

    Возвращает нормализованный URL в нижнем регистре.
    """
    parsed_url = urlparse(url)
    normalized_parsed_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, "", "", "", "")
    )
    return normalized_parsed_url.lower()


def validate(url):
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