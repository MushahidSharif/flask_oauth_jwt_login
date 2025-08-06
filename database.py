import os
from typing import TypedDict
import json

class User(TypedDict):
    username: str
    password: str
    address: str
    phone: str


"""
This is database layer. It provides function to access database. For now we are just saving and loading signup users
in a text file.  
"""

class Database():
    def __init__(self):
        pass

    def create_user(self, user: User):
        str_json = json.dumps(user)
        db_file = './db/mydb.db'
        with open(db_file, 'a') as dbfile:
            dbfile.write(str_json + '\n')

    def get_all_users(self):
        user_dict = {}
        db_file = './db/mydb.db'
        if os.path.exists(db_file):
            with open(db_file, 'r') as dbfile:
                for user_line in dbfile:
                    user = json.loads(user_line)
                    user_dict[user['username']] = user

        return user_dict


    def get_login_result(self, username, password):

        all_users = self.get_all_users()
        if username not in all_users:
            return False, 'User does not exist.'
        else:
            db_user_data = all_users[username]
            if db_user_data["password"] != password:
                return False, 'Invalid username or password'
            else:
                return True, 'Login Successful'

    def add_google_login_in_db(self, username):

        all_users = self.get_all_users()
        if username not in all_users:
            user = User(username= username, password='', address='', phone='')

            str_json = json.dumps(user)
            db_file = './db/mydb.db'
            with open(db_file, 'a') as dbfile:
                dbfile.write(str_json + '\n')

