import sqlite3
from models.user_models import UserRegister, UserResponse
from datetime import date

class DB:
    def __init__(self, db_path="database/Database.db"):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT UNIQUE, 
                email TEXT, 
                password TEXT, 
                birthdate DATE, 
                creation_date DATE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Friends (
                friendship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL,
                a_user_id INTEGER NOT NULL,
                b_user_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('pending','accepted','declined','blocked')),
                creation_date DATE,
                            
                UNIQUE(a_user_id, b_user_id),
                            
                FOREIGN KEY (a_user_id) REFERENCES Users(id),
                FOREIGN KEY (b_user_id) REFERENCES Users(id)
            )
        """)
        # Create messages table and other

        self.connection.commit()

    def get_users(self):
        
        self.cursor.execute("""
            SELECT id, username, email FROM Users
        """)
        
        return self.cursor.fetchall()

    def add_user(self, user: UserRegister) -> int:
        self.cursor.execute("""
            INSERT INTO Users (username, email, password, birthdate, creation_date)
            VALUES (?, ?, ?, ?, ?)
            """, 
            (
                user.username,
                user.email,
                user.password,
                user.birthdate,
                date.today().isoformat()
            )
        )
        self.connection.commit()

        return self.cursor.lastrowid

    def get_user_by_id(self, user_id: int):
        if self.cursor.execute("SELECT id, username, email FROM Users WHERE id = ?", (user_id,)) != None:
            return self.cursor.fetchone()
        return None

    def get_user_by_username(self, username: str):
        self.cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        return self.cursor.fetchone()
    
    def add_friend(self, user_a: int, user_b: int, requester_id: int):
        self.cursor.execute("""
            SELECT requester_id, status FROM Friends WHERE a_user_id = ? AND b_user_id = ?
            """, 
            (user_a, user_b,)
        )

        result = self.cursor.fetchone()
        if result:
            if result[0] == requester_id or result[1] == "accepted":
                return result
            else:
                self.cursor.execute("""
                        UPDATE Friends SET status = ? 
                        WHERE a_user_id = ? AND b_user_id = ?
                    """, 
                    ("accepted", user_a, user_b)
                )

                self.connection.commit()
                return ["Friend request accepted"]

        self.cursor.execute("""
            INSERT INTO Friends (requester_id, a_user_id, b_user_id, status, creation_date)
            VALUES (?,?,?,?,?)
            """, 
            (
                requester_id,
                user_a,
                user_b,
                "pending",
                date.today().isoformat()
            )
        )

        self.connection.commit()
        return ["Friend request sent"]
    
    def get_users_friends(self, user_id: int):
        self.cursor.execute("""
            SELECT * FROM Friends WHERE a_user_id = ? OR b_user_id = ? AND status = ?
        """,
        (user_id, user_id, "accepted",))

        return self.cursor.fetchall()


    def close(self):
        self.cursor.close()
        self.connection.close()