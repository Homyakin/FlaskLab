import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('./app/data/data.db')
        self.cur = self.conn.cursor()

    def get(self, field1: str, field2: str):
        """

        :param field1: имя поля1
        :param field2: имя поля2
        :return: список из бд
        """

        self.cur.execute(f'''
        SELECT {field1}, {field2} FROM INFO;
        ''')

        return self.cur.fetchall()

    def insert(self, data: dict):
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

        self.cur.execute(sql)

    def __del__(self):
        self.cur.close()
        self.conn.close()
