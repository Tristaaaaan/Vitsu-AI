import sqlite3
import bcrypt


class Database:
    def __init__(self):

        self.data_con = sqlite3.connect('user.db')
        self.users = self.data_con.cursor()
        self.create_user_database()

    def create_user_database(self):
        # Creating Database

        self.users.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            username TEXT NOT NULL,
            salt TEXT NOT NULL,
            passw_hashed TEXT NOT NULL,
            PRIMARY KEY(user_id AUTOINCREMENT))
            """)

        self.data_con.commit()

    def storeAcc(self, username, passw):

        # Encode a passw
        password = passw.encode('utf-8')

        # Generate a salt
        salt = bcrypt.gensalt()

        # Encrypt
        encrypt_passw = bcrypt.hashpw(password, salt)

        self.users.execute("INSERT into users (username, salt, passw_hashed) values(?, ?, ?)", (
            username,
            salt,
            encrypt_passw
        ))

        self.data_con.commit()

    def locateUsername(self, username):

        self.users.execute(
            "SELECT username FROM users WHERE username = ?", (username,))

        usernamesdb = (res[0] for res in self.users.fetchall())

        if username in usernamesdb:
            return True
        return False

    def locateAcc(self, username, passw):

        self.users.execute(
            "SELECT salt, passw_hashed FROM users WHERE username = ?", (username,))

        # Storing the hashed password [1] and salt [0]
        data = self.users.fetchone()

        # Generating a hash of the entered password using the stored salt
        user_password = bcrypt.hashpw(passw.encode('utf-8'), data[0])

        # Matching the hashed entered password to the stored hashed password
        if user_password == data[1]:
            return True
        return False

    def allAcc(self):

        self.users.execute("SELECT * FROM users")

        data = self.users.fetchall()

        return data

    def removeAcc(self, userid):

        self.users.execute("DELETE FROM users WHERE user_id = ?", (userid,))

        self.data_con.commit()

    def close_connection(self):

        self.users.close()

        self.data_con.close()
