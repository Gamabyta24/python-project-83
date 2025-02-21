### Hexlet tests and linter status:
[![Actions Status](https://github.com/Gamabyta24/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Gamabyta24/python-project-83/actions)

# Page Analyzer

![Flask](https://img.shields.io/badge/Flask-2.0.3-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)

## 📌 Описание проекта
**Page Analyzer** — это веб-приложение на Flask, которое позволяет проверять доступность сайтов, получать их статус-код HTTP и извлекать ключевые данные (h1, title, description). Проект выполнен в рамках обучения.

## 🎯 Функциональность
- Добавление сайта в базу данных
- Проверка доступности сайта (код ответа HTTP)
- Извлечение заголовков (h1, title, description)
- История проверок с датами и статусами
- Вывод информации в удобной таблице

## 🚀 Установка и запуск
### 📦 Установка зависимостей
```sh
make install
```

### ⚙️ Создание базы данных
Перед первым запуском нужно создать таблицы в PostgreSQL. Используйте SQL-скрипт:
```sh
psql -d <database_name> -f database.sql
```

### 🏃 Запуск проекта
```sh
make start
```
Приложение будет доступно по адресу: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🛠 Используемые технологии
- **Flask** — микрофреймворк для Python
- **PostgreSQL** — реляционная база данных
- **requests** — библиотека для работы с HTTP-запросами
- **BeautifulSoup4** — парсинг HTML
- **Bootstrap** — стилизация интерфейса


Link - https://python-project-83-1w4q.onrender.com