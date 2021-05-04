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
        access_code TEXT DEFAULT NULL,
        is_finished boolean DEFAULT false,
        is_in_force boolean DEFAULT false,
        force_date date DEFAULT NULL,
        last_event TEXT DEFAULT NULL,
        last_event_date date,         
        first_decision TEXT DEFAULT NULL,
        first_decision_date date DEFAULT NULL,
        apell_decision TEXT DEFAULT NULL,
        apell_decision_date date DEFAULT NULL,
        kas_decision TEXT DEFAULT NULL,
        kas_decision_date date DEFAULT NULL,
        is_mot_dec_required boolean DEFAULT false,
        is_mot_dec boolean DEFAULT false,
        mot_dec_date date DEFAULT NULL);''')
    conn.commit()
    conn.close()

def add_case(item_text):
    conn = create_connection()
    cur = conn.cursor()
    td = datetime.today()
    sql = "INSERT INTO cases (case_number, last_event_date) VALUES (%s, %s)"
    cur.execute(sql, (item_text, td))
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
    cur.execute("SELECT case_number FROM cases")
    cases = cur.fetchall()
    conn.commit()
    conn.close()
    return cases

def get_case_id(case_number):
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT case_id FROM cases WHERE case_number = (%s)"
    cur.execute(sql, (case_number,))
    case_id = cur.fetchone()
    conn.commit()
    conn.close()
    return case_id

def update_case_id(case_id, case_number):
    conn = create_connection()
    cur = conn.cursor()
    sql = "UPDATE cases SET case_id = (%s) WHERE case_number = (%s)"
    cur.execute(sql, (case_id, case_number))
    conn.commit()
    conn.close()

def case_is_finished_or_not(case_number, is_finished):
    conn = create_connection()
    cur = conn.cursor()
    sql = "UPDATE cases SET is_finished = (%s) WHERE case_number = (%s)"
    cur.execute(sql, (case_number, is_finished))
    conn.commit()
    conn.close()

def get_last_event_date(case_number):
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT last_event_date FROM cases WHERE case_number = (%s)"
    cur.execute(sql, (case_number,))
    last_event_date = cur.fetchone()
    conn.commit()
    conn.close()
    return last_event_date


