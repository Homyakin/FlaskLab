import sqlite3
import os
from sqlite3 import Error


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + '\\app\\data\\data.db')
    except Error as e:
        print(e)

    return conn


def get(conn, field1: str, field2: str):
    """
    :param conn: connection to database
    :param field1: имя поля 1
    :param field2: имя поля
    :return: list of tuples with data from db
    """
    cur = conn.cursor()
    cur.execute(f'''
    SELECT {field1}, {field2} FROM INFO;
    ''')

    return cur.fetchall()


def insert(conn, data: dict):
    """
    :param conn: connection to database
    :param data: словарь с данными
    :return: last row id
    """

    cur = conn.cursor()

    sql = '''
    INSERT INTO INFO(EmploymentField, 
                     EmploymentStatus, 
                     Gender, 
                     LanguageAtHome, 
                     JobWherePref, 
                     SchoolDegree,
                     Income) VALUES(?,?,?,?,?,?,?);
                     
    '''

    cur.execute(sql, list(data.values()))
    return cur.lastrowid
