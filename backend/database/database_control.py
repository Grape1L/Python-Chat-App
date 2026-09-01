import sqlite3
from backend.models.user_models import UserRegister, UserResponse
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

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES Users(id),
                FOREIGN KEY (recipient_id) REFERENCES Users(id)
            )
        """)

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
        self.cursor.execute("SELECT id, username, email FROM Users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def get_user_by_username(self, username: str):
        self.cursor.execute("SELECT * FROM Users WHERE username = ? COLLATE NOCASE", (username,))
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
            SELECT u.id, u.username 
                FROM Friends f 
                JOIN Users u 
                    ON u.id = CASE
                        WHEN f.a_user_id = ? THEN f.b_user_id
                        ELSE f.a_user_id
                    END
                WHERE 
                    (f.a_user_id = ? OR f.b_user_id = ?) 
                    AND f.status = 'accepted'
        """,
        (user_id, user_id, user_id))

        return self.cursor.fetchall()
    
    def are_friends(self, user_a: int, user_b: int) -> bool:
        self.cursor.execute("""
            SELECT status FROM Friends 
            WHERE 
                (a_user_id = ? AND b_user_id = ?) OR (a_user_id = ? AND b_user_id = ?)
        """, (user_a, user_b, user_b, user_a))

        result = self.cursor.fetchone()
        if result is None:
            return False
        
        return result[0] == "accepted"
    


    def save_message(self, sender_id: int, recipient_id: int, content: str):
        self.cursor.execute("""
            INSERT INTO Messages (sender_id, recipient_id, content)
            VALUES (?, ?, ?)
        """, (sender_id, recipient_id, content))

        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_messages(self, requester_id: int, friend_id: int):
        self.cursor.execute("""
            SELECT m.sender_id, m.recipient_id, m.content, m.timestamp, u.username
            FROM Messages m
            JOIN Users u ON m.sender_id = u.id
            WHERE
                (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?)
                
         """, (requester_id, friend_id, friend_id, requester_id))
        
        return self.cursor.fetchall()




    def close(self):
        self.cursor.close()
        self.connection.close()