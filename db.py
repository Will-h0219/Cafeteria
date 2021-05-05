import sqlite3
from sqlite3 import Error

con = None #variable global para conexion

def get_db():
    try:
        con = sqlite3.connect('DB\cafeteriaDB.db')
        return con
    except :
        print('Error al conectar BD..')

def close_db():
    if con is not None: 
        con.close()