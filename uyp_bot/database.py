import re
from datetime import datetime
import sqlite3
from settings import FILENAME_DB

class Connection:
    def __init__(self):
        # python-telegram-bot uses threading, does not play well w/ sqlite3
        self.conn = sqlite3.connect(FILENAME_DB, check_same_thread=False)
        self.curs = self.conn.cursor()
        # code is after url, so IntegrityError prioritise code before url
        #   when both fail UNIQUE constraint
        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS mods (
                url         TEXT NOT NULL UNIQUE,
                code        TEXT NOT NULL PRIMARY KEY, 
                renew_date  TEXT NOT NULL, 
                remove_date TEXT NOT NULL, 
                admin       TEXT NOT NULL);
        ''')
        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id          TEXT NOT NULL PRIMARY KEY, 
                state       TEXT,
                code_temp   TEXT,
                msg_temp    TEXT);
        ''')
        self.conn.commit()

    def get_mod(self, mod):
        self.curs.execute('''
            SELECT * FROM mods WHERE code = ?;
            ''', (mod,) 
        )
        return self.curs.fetchone()

    def get_users_mods(self, user):
        self.curs.execute('''
            SELECT * FROM mods WHERE admin = ?;
            ''', (user,)
        )
        return self.curs.fetchall()

    def get_mods_reg(self, regex):
        reg = re.compile(regex)
        self.curs.execute('SELECT * FROM mods;')
        mods = self.curs.fetchall()
        return tuple(filter(
            lambda x: reg.search(x[1]), mods))  # tuple of tuples

    def get_user(self, user):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        row = self.curs.fetchone()
        # if user not exist, create
        if row is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?);
                ''', (user, None, None, None)
            )
            self.conn.commit()
            return (user, None, None, None)
        else:
            return row

    def update_user(self, user, state, code_temp, msg_temp):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        # if user not exist, create
        if self.curs.fetchone() is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?);
                ''', (user, state, code_temp, msg_temp)
            )
        else:
            self.curs.execute('''
                UPDATE users SET state = ?, code_temp = ?, msg_temp = ?
                WHERE id = ?;''', (state, code_temp, msg_temp, user)
            )
        self.conn.commit()

    def update_mod(self, url, code, renew_date, remove_date, admin):
        self.curs.execute('SELECT * FROM mods WHERE code = ?;', (code,))
        # if user not exist, create
        if self.curs.fetchone() is None:
            self.curs.execute('''
                INSERT INTO mods VALUES (?, ?, ?, ?, ?);
                ''', (url, code, renew_date, remove_date, admin)
            )
        else:
            self.curs.execute('''
                UPDATE mods SET 
                url = ?, renew_date = ?, remove_date = ?, admin = ?
                WHERE code = ?;''', 
                (url, renew_date, remove_date, admin, code)
            )
        self.conn.commit()

    def add_mod(self, url, code, renew_date, remove_date, admin):
        self.curs.execute('''
            INSERT INTO mods VALUES (?, ?, ?, ?, ?);
            ''', (url, code, renew_date, remove_date, admin)
        )
        self.conn.commit()

    def add_user(self, user):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        # only INSERT if not exist
        if self.curs.fetchone() is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?);
                ''', (user, None, None, None)
            )
            self.conn.commit()

    def delete_mod(self, mod):
        self.curs.execute('''
            DELETE FROM mods WHERE code = ?;
            ''', (mod,)
        )
        self.conn.commit()
