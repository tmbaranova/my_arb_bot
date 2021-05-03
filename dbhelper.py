import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRESQL_CONNECTION_STRING = os.getenv('DATABASE_URL')

class DBHelper:
    def __init__(self):
        self.conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        self.cur = self.conn.cursor()
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS cases
            (id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            case_number TEXT);''')

        self.conn.commit()
        self.conn.close()

    def add_case(self, item_text):
        self.conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        self.cur = self.conn.cursor()
        self.cur.execute("INSERT INTO cases (case_number) VALUES (?)",
                         (item_text,))
        self.conn.commit()
        self.conn.close()

    def delete_all_cases(self):
        self.conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        self.cur = self.conn.cursor()
        self.cur.execute("DELETE FROM cases ")
        self.conn.commit()
        self.conn.close()

    def delete(self, case_number):
        self.conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        self.cur = self.conn.cursor()
        self.cur.execute("DELETE FROM cases WHERE case_number = (?)",
                         (case_number,))
        self.conn.commit()
        self.conn.close()

    def get_cases(self):
        self.conn = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
        self.cur = self.conn.cursor()
        return [x[0] for x in self.cur.execute(
            "SELECT case_number FROM cases")]

