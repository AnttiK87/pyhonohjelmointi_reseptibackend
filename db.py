import contextlib

import mysql.connector


# pari tapaa miten yhteyden voi tehdä alempi parempi
def connect_to_dbx():
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
    return cnx


# funktio joka yieldaa on "generaattori"
@contextlib.contextmanager
def connect_to_db():
    cnx = None
    try:
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
        yield cnx
    except mysql.connector.Error:
        print("Error while connecting to db")
        yield None
    finally:
        # finally suoritetaan jokatapauksessa virheen hallinnan tuloksesta riippumatta
        if cnx is not None:
            cnx.close()
