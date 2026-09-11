"""
Safe, idempotent database migration for Expense X-Ray.
- Adds 'user' table if it doesn't exist.
- Adds 'user_id' column to 'expense' table if it doesn't exist.
- Adds 'user_id' column to 'goal' table if it doesn't exist.
- Adds 'monthly_income' column to 'user' table if it doesn't exist.
- Never drops tables or deletes rows.
- Safe to run multiple times.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'expense.db')

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols

def table_exists(cursor, table):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None

def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create 'user' table if not exists
    if not table_exists(cursor, 'user'):
        print("Creating 'user' table...")
        cursor.execute("""
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_xray_id TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                monthly_income REAL DEFAULT 0.0
            )
        """)
        print("  'user' table created.")
    else:
        print("'user' table already exists — skipping.")
        # Ensure monthly_income column exists on existing user table
        if not column_exists(cursor, 'user', 'monthly_income'):
            print("  Adding 'monthly_income' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN monthly_income REAL DEFAULT 0.0")
            print("  'monthly_income' column added.")
        else:
            print("  'monthly_income' column already exists.")

    # 1b. Add 'name' column to 'user' table if not exists
    if table_exists(cursor, 'user'):
        if not column_exists(cursor, 'user', 'name'):
            print("  Adding 'name' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN name TEXT")
            print("  'name' column added.")
        else:
            print("  'name' column already exists.")

    # 2. Add 'user_id' to 'expense' table if not exists
    if table_exists(cursor, 'expense'):
        if not column_exists(cursor, 'expense', 'user_id'):
            print("Adding 'user_id' column to 'expense' table...")
            cursor.execute("ALTER TABLE expense ADD COLUMN user_id INTEGER REFERENCES user(id)")
            print("  'user_id' column added to 'expense'. Existing rows have NULL user_id (preserved).")
        else:
            print("'expense.user_id' already exists — skipping.")
    else:
        print("WARNING: 'expense' table not found — skipping user_id migration for expenses.")

    # 3. Add 'user_id' to 'goal' table if not exists
    if table_exists(cursor, 'goal'):
        if not column_exists(cursor, 'goal', 'user_id'):
            print("Adding 'user_id' column to 'goal' table...")
            cursor.execute("ALTER TABLE goal ADD COLUMN user_id INTEGER REFERENCES user(id)")
            print("  'user_id' column added to 'goal'. Existing rows have NULL user_id (preserved).")
        else:
            print("'goal.user_id' already exists — skipping.")
    else:
        print("WARNING: 'goal' table not found — skipping user_id migration for goals.")

    conn.commit()
    conn.close()
    print("\nMigration complete. All existing data preserved.")

if __name__ == '__main__':
    run_migrations()
