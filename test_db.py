import pymysql
import sys

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Test123#',
        database='erp',
        port=3306
    )
    print("Connection successful!")
    connection.close()
except pymysql.MySQLError as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)
