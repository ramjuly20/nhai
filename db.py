import mysql.connector

def connection():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='ram',
        database='nhai'
    ) 
    return db


