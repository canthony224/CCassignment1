from flask import g
import sqlite3



def setup():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("setting up database")
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR, first_name VARCHAR, last_name VARCHAR, password, VARCHAR);')
    print("setup complete")

def open_db_connection():
    g.conn = sqlite3.connect('users.db')
    g.cursor = g.conn.cursor()


def close_db_connection():
    g.cursor.close()


def find_user(email):
    query = """
    SELECT * from users
    WHERE email = ?
    """
    args = (email,)
    #print("finding user",email,query,args)
    g.cursor.execute(query, args)
    fetched = g.cursor.fetchone()
    if fetched == None: 
        return None

    myresult = { 'id':fetched[0],
                'email': fetched[1],
                'first_name': fetched[2],
                'last_name': fetched[3],
                }
    return myresult


def create_user(email, first_name, last_name, password):

    query = '''
    INSERT INTO users (email, first_name, last_name, password)
    VALUES (?,?,?,?)
    '''
    args = (email,first_name,last_name,password)
    g.cursor.execute(query, args)
    g.conn.commit()
    return g.cursor.rowcount

def authenticate(email,password): #add any oter features here too
    # check for empty values?
    #mycursor = mydb.cursor(pymysql.cursors.DictCursor)
    query = """SELECT * FROM users WHERE
            email = ? AND password = ?;"""
    values = (email,password)
    g.cursor.execute(query, values)
    fetched = g.cursor.fetchone()
    if fetched == None: 
        return [False,'badboi']

    myresult = { 'id':fetched[0],
                'email': fetched[1],
                'first_name': fetched[2],
                'last_name': fetched[3],
                }
    print("fetched",myresult)
    if myresult != None:
        return [True,myresult]
    else:
        return [False,'badboi']



setup()