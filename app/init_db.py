# import sqlite3
# from pathlib import Path
# from app.config.settings import settings

# # Resolve project root (one level above /app)
# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# # Path to SQL schema file
# SQL_PATH = PROJECT_ROOT / "data" / "data.sql"

# def extract_sqlite_path(url: str) -> Path:
#     """
#     Convert sqlite:///./GLH.db → PROJECT_ROOT / GLH.db
#     """
#     raw = url.replace("sqlite:///", "")  # ./GLH.db
#     return (PROJECT_ROOT / raw).resolve()

# def init_db():
#     db_path = extract_sqlite_path(settings.APP_DATABASE_URL)

#     print(f"Using database path: {db_path}")

#     # Ensure DB file exists
#     if not db_path.exists():
#         print("Database file does not exist. Creating it...")
#         db_path.touch()

#     # Connect and load schema
#     conn = sqlite3.connect(str(db_path))
#     cursor = conn.cursor()

#     with open(SQL_PATH, "r") as f:
#         sql = f.read()

#     cursor.executescript(sql)
#     conn.commit()
#     conn.close()

#     print("Database initialized successfully!")

#     print("Executing SQL:")
#     print(sql)


# if __name__ == "__main__":
#     init_db()