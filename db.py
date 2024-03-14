import contextlib
import mysql.connector


# pari tapaa miten yhteyden voi tehdä alempi parempi
# def connect_to_dbx():
#     cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
#     return cnx

@contextlib.contextmanager
def connect_to_db():
    cnx = None
    # Try to make connection to db
    try:
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
        yield cnx
    # Error message if connection fails
    except mysql.connector.Error:
        print("Error while connecting to db")
        yield None
    # Close connection
    finally:
        if cnx is not None:
            cnx.close()
