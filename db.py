import sqlite3

DB_NAME= "database.db"

def get_db_connection():
    conn= sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn= get_db_connection()
    cursor= conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            balance INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.commit()
    conn.close()