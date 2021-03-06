import os
import psycopg2
from psycopg2.extensions import AsIs
from datetime import datetime, date

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
        finished_date timestamp DEFAULT NULL,
        is_in_force boolean DEFAULT false,
        force_date timestamp DEFAULT NULL,
        last_event TEXT DEFAULT NULL,
        last_event_date timestamp,         
        first_decision TEXT DEFAULT NULL,
        first_decision_date timestamp DEFAULT NULL,
        apell_decision TEXT DEFAULT NULL,
        apell_decision_date timestamp DEFAULT NULL,
        kas_decision TEXT DEFAULT NULL,
        kas_decision_date timestamp DEFAULT NULL,
        is_in_apell boolean DEFAULT false,
        is_in_kas boolean DEFAULT false);''')
    conn.commit()
    conn.close()

def add_case(item_text):
    conn = create_connection()
    cur = conn.cursor()
    td = datetime(2018, 1, 1)
    # td = date.today()
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
    cur.execute("SELECT case_number FROM cases where is_finished = false ORDER BY last_event_date")
    cases = cur.fetchall()
    conn.commit()
    conn.close()
    return cases


def case_is_finished_or_not(case_number, is_finished):
    conn = create_connection()
    cur = conn.cursor()
    sql = "UPDATE cases SET is_finished = (%s) WHERE case_number = (%s)"
    cur.execute(sql, (case_number, is_finished))
    conn.commit()
    conn.close()

def update_row(row, date, case_number):
    conn = create_connection()
    cur = conn.cursor()
    sql = "UPDATE cases SET %s = (%s) WHERE case_number = (%s)"
    cur.execute(sql, (AsIs(row), date, case_number))
    conn.commit()
    conn.close()

def get_row(row, case_number):
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT %s FROM cases WHERE case_number = (%s)"
    cur.execute(sql, (AsIs(row), case_number))
    get_row_data = cur.fetchone()
    conn.commit()
    conn.close()
    return get_row_data


def select_first():
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT case_number FROM cases WHERE is_in_apell = false AND is_finished = false AND force_date IS NULL"
    cur.execute(sql)
    cases_in_first = cur.fetchall()
    conn.commit()
    conn.close()
    return cases_in_first


def select_apell():
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT case_number FROM cases WHERE is_in_apell = true AND is_finished = false AND force_date IS NULL"
    cur.execute(sql)
    cases_in_apell = cur.fetchall()
    conn.commit()
    conn.close()
    return cases_in_apell


def select_in_force():
    conn = create_connection()
    cur = conn.cursor()
    sql = "SELECT case_number FROM cases WHERE is_finished = false AND force_date IS NOT NULL"
    cur.execute(sql)
    cases_in_force = cur.fetchall()
    conn.commit()
    conn.close()
    return cases_in_force
