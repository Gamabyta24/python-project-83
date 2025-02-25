from page_analyzer.routes import app
from page_analyzer.utility_bd import create_tables

create_tables()

if __name__ == "__main__":
    app.run(debug=True)
