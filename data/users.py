import datetime
import uuid
import jwt
from passlib.hash import pbkdf2_sha512 as pl

SECRET = 'nvaonvaoivnafinvmpaoskf+we9i@£{$[€[{[[{€$€GSBTBRHYNB5W4Q34R5rf£${£€$€]$[£{$€49jfmrioamvpoiah3r8hfenIDSC'

# db query for adding user
def register(cnx, reg_body):
    try:
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO users (username, password, auth_role_id) VALUES (%s, %s, %s)',
                       (reg_body['username'], pl.hash(reg_body['password']), 1))
        cnx.commit()
        user = {'id': cursor.lastrowid, 'username': reg_body['username']}
        cursor.close()
        return user
    except Exception as e:
        cnx.rollback()
        raise e

# db query for logging user in by checking username and password and then giving user access token
def login(cnx, reg_body):
    try:
        cursor = cnx.cursor()
        cursor.execute('SELECT * FROM users WHERE username = (%s)', (reg_body['username'],))
        user = cursor.fetchone()
        if user is None:
            raise Exception('User not found!')
        cursor.close()

        passwor_correct = pl.verify(reg_body['password'], user[2])
        if not passwor_correct:
            raise Exception('User not found!')

        sub = str(uuid.uuid4())

        cursor = cnx.cursor()
        cursor.execute('UPDATE users SET access_jti = %s WHERE username = %s', (sub, reg_body['username']))
        cnx.commit()

        # encode luo payloadista (dictionary) access_token_jwt
        access_token = jwt.encode({'sub': sub,
                                   'iat': datetime.datetime.now(datetime.UTC),
                                   'nbf': datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=10)},
                                  SECRET)

        return access_token
    except Exception as e:
        cnx.rollback()
        raise e

# db query for logging user out by removing access token
def logout(cnx, logged_in_user):
    try:
        cursor = cnx.cursor()
        cursor.execute('UPDATE users SET access_jti = NULL WHERE id = (%s)', (logged_in_user['id'],))
        cnx.commit()
        cursor.close()
    except Exception as e:
        cnx.rollback()
        raise e

# db query for getting logged in user
def get_logged_in_user(cnx, sub):
    cursor = cnx.cursor()
    cursor.execute('SELECT id, username, auth_role_id FROM users WHERE access_jti = (%s)', (sub,))
    user = cursor.fetchone()
    if user is None:
        raise Exception('User not found!')
    return {'id': user[0], 'username': user[1], 'role': user[2]}

# db query for deleting user
def remove_user_by_id(cnx, user_id):
    cursor = None
    try:
        cursor = cnx.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise e
    finally:
        if cursor is not None:
            cursor.close()
