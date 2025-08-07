import sqlite3
import os

def initialize_db():
    db_path = "/data/subscriptions.db"
    os.makedirs("/data", exist_ok=True)

    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE "subscriptions" (
                "id" INTEGER NOT NULL,
                "email" TEXT NOT NULL UNIQUE,
                "locations" TEXT,
                "fromdate" DATETIME,
                "todate" DATETIME,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized.")
    else:
        print("Database already exists.")
