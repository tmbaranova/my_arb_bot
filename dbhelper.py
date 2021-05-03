import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("Connection to PostgreSQL DB successful")
    except psycopg2.OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def create_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS cases
        (case_number TEXT);''')
    conn.commit()
    conn.close()

def add_case(item_text):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO cases (case_number) VALUES (%s)",
                         (item_text,))
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
    cases = cur.execute(
            "SELECT case_number FROM cases")
    return [x[0] for x in cases]

