from datetime import datetime


def get_recipes_by_category(cnx, category_id):
    cursor = cnx.cursor()
    _query = "SELECT * FROM recipe WHERE category_id = (%s) ORDER BY id"
    cursor.execute(_query, (category_id,))
    recipes = cursor.fetchall()
    recipes_list = []
    for recipe in recipes:
        recipes_list.append(
            {'category_id': recipe[6], 'created_at': recipe[3], 'deleted_at': recipe[4], 'description': recipe[2],
             'id': recipe[0], 'name': recipe[1], 'state_id': recipe[7], 'user_id': recipe[5]})
    cursor.close()
    return recipes_list


def insert_recipe_by_category(cnx, request_data, logged_in_user, category_id):
    try:
        cursor = cnx.cursor()
        _query = "INSERT INTO recipe(name, description, created_at, user_id, category_id, state_id)values (%s,%s,%s,%s,%s,1)"
        cursor.execute(_query, (request_data['name'], request_data['description'], datetime.now(), logged_in_user['id'], category_id))
        cnx.commit()
        new_recipe = {'category_id': category_id, 'description': request_data['description'], 'id': cursor.lastrowid,
                      'name': request_data['name'], 'state_id': 1, 'user_id': logged_in_user['id']}
        cursor.close()
        return new_recipe
    except Exception as e:

        cnx.rollback()
        print(e)
        raise e


def get_recipe_by_id(cnx, recipe_id):
    cursor = cnx.cursor()
    _query = "SELECT * FROM recipe WHERE id = (%s)"
    cursor.execute(_query, (recipe_id,))
    recipe = cursor.fetchone()
    cursor.close()
    if recipe is None:
        raise Exception('Recipe not found')
    return {'id': recipe[0], 'name': recipe[1], 'description': recipe[2], 'created_at': recipe[3],
            'deleted_at': recipe[4], 'user_id': recipe[5], 'category_id': recipe[6], 'state_id': recipe[7]}


def update_recipe_by_id(cnx, recipe, request_data, logged_in_user):
    try:
        if logged_in_user['id'] != recipe['user_id'] and logged_in_user['role'] != 4:
            raise Exception('You are not authorized to update this recipe')
        else:
            cursor = cnx.cursor()
            _query = "UPDATE recipe SET name = (%s), description = (%s) WHERE id = (%s)"
            cursor.execute(_query, (request_data['name'], request_data['description'], recipe['id']))
            cnx.commit()
            cursor.close()
    except Exception as e:
        cnx.rollback()
        print(e)
        raise e


def delete_recipe_by_id(cnx, recipe_id, recipe, logged_in_user):
    try:
        if logged_in_user['id'] != recipe['user_id'] and logged_in_user['role'] != 4:
            print(logged_in_user['id'])
            print(recipe['user_id'])
            raise Exception('You are not authorized to delete this recipe')
        else:
            cursor = cnx.cursor()
            _query = "DELETE FROM recipe WHERE id = (%s)"
            cursor.execute(_query, (recipe_id,))
            cnx.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows

    except Exception as e:
        cnx.rollback()
        print(e)
        raise e
