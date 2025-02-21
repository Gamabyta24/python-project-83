from page_analyzer.routes import app
from page_analyzer.models import create_tables

# drop_tables()
create_tables()

if __name__ == "__main__":
    app.run(debug=True)
