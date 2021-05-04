import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ['DATABASE_URL']

def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        print("Connection to PostgreSQL DB successful")
    except psycopg2.OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def create_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS cases
        (case_number TEXT,
        case_id TEXT DEFAULT NULL,
        last_event_date date);''')
    conn.commit()
    conn.close()

def add_case(item_text):
    conn = create_connection()
    cur = conn.cursor()
    td = datetime.today()
    sql = "INSERT INTO cases (case_number, case_id, last_event_date) VALUES (%s, %s, %s)"
    cur.execute(sql, (item_text, None, td))
    conn.commit()
    conn.close()

def delete_all_cases():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cases ")
    conn.commit()
    conn.close()

def delete(case_number):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cases WHERE case_number = (%s)",
                         (case_number,))
    conn.commit()
    conn.close()

def get_cases():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cases")
    cases = cur.fetchall()
    conn.commit()
    conn.close()
    return cases

