# from flask import Flask, render_template , request , redirect , flash , url_for
# from dotenv import load_dotenv
# import os
# import psycopg2
# import validators

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")


# try:
#     conn = psycopg2.connect(DATABASE_URL)
#     print("Успешное подключение!", DATABASE_URL)
# except Exception as ex:
#     print("Can`t establish connection to database", ex)
# sql = "SELECT * FROM test;"
# cursor = conn.cursor()
# cursor.execute(sql)
# for row in cursor:
#     print(row)
# cursor.close()


# app = Flask(__name__)
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# def get_db_connection():
#     return psycopg2.connect(DATABASE_URL)

# #создаем локально таблицу
# with get_db_connection() as conn:
#     with conn.cursor() as cur:
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS urls (
#                 id SERIAL PRIMARY KEY,
#                 name VARCHAR(255) UNIQUE NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#         """)
#         conn.commit()


# @app.route("/", methods=["GET","POST"])
# def index():
#     error = None
#     if request.method == "POST":
#         url = request.form.get("url").strip()

#         if not url or not validators.url(url) or len(url) > 255:
#             error = "Введите корректный URL (до 255 символов)"
#         else:
#             with get_db_connection() as conn:
#                 with conn.cursor() as cur:
#                     cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
#                     existing_url = cur.fetchone()

#                     if existing_url:
#                         flash("Этот URL уже добавлен", "warning")
#                     else:
#                         cur.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
#                         conn.commit()
#                         flash("URL успешно добавлен", "success")
#                     return redirect(url_for("show_urls"))

#     return render_template("index.html", error=error)
# @app.route("/urls")
# def show_urls():
#     with get_db_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT id, name, created_at FROM urls ORDER BY created_at DESC")
#             urls = cur.fetchall()
#     return render_template("urls.html", urls=urls)

# if __name__ == "__main__":
#     app.run(debug=True)
from page_analyzer.routes import app

if __name__ == "__main__":
    app.run(debug=True)
