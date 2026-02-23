import sqlite3

db_path="database/Database.db"

connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = connection.cursor()

cursor.execute("""
    DROP TABLE Friends
""")

connection.commit()