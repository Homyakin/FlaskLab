import sqlite3


conn = sqlite3.connect('../app/data/data.db')
cur = conn.cursor()


def get(field1: str, field2: str):
    """

    :param field1: имя поля 1
    :param field2: имя поля
    :return: список из бд
    """

    cur.execute(f'''
    SELECT {field1}, {field2} FROM INFO;
    ''')

    return cur.fetchall()


def insert(data: dict):
    """

    :param data: словарь с данными
    :return: сообщение об успехе с описание ошибки в случае отказа
    """

    sql = '''
    BEGIN TRANSACTION;
    INSERT INTO INFO(EmploymentField, 
                     EmploymentStatus, 
                     Gender, 
                     LanguageAtHome, 
                     JobWherePref, 
                     SchoolDegree,
                     Income) VALUES(?,?,?,?,?,?,?);
                     
    COMMIT;
    '''

    cur.execute(sql)


def close():
    cur.close()
    conn.close()
