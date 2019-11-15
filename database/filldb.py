import pandas as pd
import sqlite3


data = pd.read_csv('../app/data/data.csv')
data = data[['CityPopulation', 'EmploymentField',
             'EmploymentStatus', 'Gender',
             'HasDebt', 'LanguageAtHome',
             'JobPref', 'JobWherePref',
             'SchoolDegree', 'MaritalStatus',
             'Income']]
data = data[data['Gender'].isin(['male', 'female'])]
data.dropna(inplace=True)

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


def create_database():
    try:
        conn = sqlite3.connect('../app/data/data.db')
        cursor = conn.cursor()

        cursor.executescript("""
        BEGIN TRANSACTION;
            CREATE TABLE INFO (
                ID integer primary key autoincrement,
                CityPopulation TEXT,
                EmploymentField TEXT,
                EmploymentStatus TEXT,
                Gender TEXT,
                HasDebt INTEGER,
                LanguageAtHome TEXT,
                JobPref TEXT,
                JobWherePref TEXT,
                SchoolDegree TEXT,
                MaritalStatus TEXT,
                Income REAL
            );

        COMMIT;
        """)
        conn.commit()
    except sqlite3.Error as e:
        print('DB Error: ' + str(e))
    finally:
        cursor.close()
        conn.close()


def insert_to_database(table, sql):
    try:
        conn = sqlite3.connect('../app/data/data.db')
        cursor = conn.cursor()
        cursor.executemany(sql, table)
        conn.commit()
    except sqlite3.Error as e:
        print('DB Error: ' + str(e))
    finally:
        cursor.close()
        conn.close()


create_database()
insert_to_database(data.values, sql)
