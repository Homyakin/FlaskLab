import sqlite3
from sqlite3 import Error


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect('app/data/data.db')
    except Error as e:
        print(e)

    return conn


def get(conn, fields):
    """
    :param conn: connection to database
    :param fields: list of fields to get
    :return: list of tuples with data from db
    """
    cur = conn.cursor()
    cur.execute(f'''
    SELECT {', '.join(fields)} FROM INFO;
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
    INSERT INTO INFO(CityPopulation,
                    EmploymentField,
                    EmploymentStatus,
                    Gender,
                    HasDebt,
                    LanguageAtHome,
                    JobPref,
                    JobWherePref,
                    SchoolDegree,
                    MaritalStatus,
                    Income) VALUES(?,?,?,?,?,?,?,?,?,?,?);
    '''

    cur.execute(sql, list(data.values()))
    return cur.lastrowid
