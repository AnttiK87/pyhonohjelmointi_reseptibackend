def get_categories(cnx):
    cursor = cnx.cursor()
    _query = "SELECT * FROM categories ORDER BY id"
    cursor.execute(_query)
    categories = cursor.fetchall()
    categories_list = []
    for category in categories:
        categories_list.append({'id': category[0], 'name': category[1]})
    cursor.close()
    return categories_list
    # tämän "with" jälkeen palatan palataan db.py:n ja suoritetaan finally


def get_category_by_id(cnx, category_id):
    cursor = cnx.cursor()
    _query = "SELECT id, name FROM categories WHERE id = (%s)"
    # jos tuplessa on ainoastaan yksi elementti, pitää laittaa pilkku loppuun
    cursor.execute(_query, (category_id,))
    category = cursor.fetchone()
    cursor.close()
    if category is None:
        raise Exception('Category not found')
    return {'id': category[0], 'name': category[1]}

def update_category_by_id(cnx, category, request_data):
    try:
        cursor = cnx.cursor()
        _query = "UPDATE categories SET name = (%s) WHERE id = (%s)"
        cursor.execute(_query, (request_data['name'], category['id']))
        cnx.commit()
        cursor.close()
    except Exception as e:
        cnx.rollback()
        print(e)
        raise e

def delete_category_by_id(cnx, category_id):
    try:
        cursor = cnx.cursor()
        _query = "DELETE FROM categories WHERE id = (%s)"
        cursor.execute(_query, (category_id,))
        cnx.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows
    except Exception as e:
        cnx.rollback()
        print(e)
        raise e

def insert_category(cnx, request_data):
    try:
        cursor = cnx.cursor()
        _query = "INSERT INTO categories(name) VALUES ((%s))"
        cursor.execute(_query, (request_data['name'],))
        #jokainen muokkaava kysely pitää vahvistaa (commit)
        cnx.commit()
        new_category = {'id': cursor.lastrowid, 'name': request_data['name']}
        cursor.close()
        return new_category
    except Exception as e:
    # jos jokin kyselyssä menee pieleen, pakitetaan takaisin, jotta data pysyy ajantasalla ja oikeana
        cnx.rollback()
        print(e)
        raise e

