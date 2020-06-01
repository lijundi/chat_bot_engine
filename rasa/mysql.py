# @Time : 2020/4/6 20:18 
# @Author : lijundi
# @File : mysql.py 
# @Software: PyCharm
import pymysql


class MySql:
    def __init__(self, host, user, password, port, database):
        self.mysql = pymysql.connect(host=host, user=user, password=password, port=port, database=database, charset='utf8')

    def close(self):
        self.mysql.close()

    def inquire_all(self, sql):
        cursor = self.mysql.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results

    def inquire_one(self, sql):
        cursor = self.mysql.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result

