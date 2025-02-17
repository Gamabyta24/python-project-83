from flask import Flask, render_template
from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Успешное подключение!", DATABASE_URL)
except Exception as ex:
    print("Can`t establish connection to database", ex)
sql = "SELECT * FROM test;"
cursor = conn.cursor()
cursor.execute(sql)
for row in cursor:
    print(row)
cursor.close()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
