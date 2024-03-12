from passlib.hash import pbkdf2_sha512 as pl

def register(cnx, reg_body):
    try:
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO users (username, password, auth_role_id) VALUES (%s, %s, %s)',
                        (reg_body['username'], pl.hash(reg_body['password']), 1))
        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise e