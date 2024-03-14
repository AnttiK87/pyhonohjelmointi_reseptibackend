from datetime import datetime


# db query for getting all recipes in specific category
def get_recipes_by_category(cnx, category_id):

    cursor = cnx.cursor() # Create a cursor
    query = "SELECT * FROM recipe WHERE category_id = (%s) ORDER BY id" # SQL query
    cursor.execute(query, (category_id,)) # Execute the query with parameter
    recipes = cursor.fetchall() # Fetch all results
    recipes_list = [] # Initialize a list for recipes
    for recipe in recipes:     # loop recipes
        # Create a dictionary
        recipes_list.append({
            'id': recipe[0],
            'name': recipe[1],
            'description': recipe[2],
            'created_at': recipe[3],
            'deleted_at': recipe[4],
            'user_id': recipe[5],
            'category_id': recipe[6],
            'state_id': recipe[7]
        })
    cursor.close() # Close the cursor
    return recipes_list # Return the recipes

# db query for adding recipe in specific category
def insert_recipe_by_category(cnx, request_data, logged_in_user, category_id):
    try:
        cursor = cnx.cursor()
        _query = "INSERT INTO recipe(name, description, created_at, user_id, category_id, state_id)values (%s,%s,%s,%s,%s,1)"
        cursor.execute(_query, (request_data['name'], request_data['description'], datetime.now(), logged_in_user['id'], category_id)) # Execute the query with the given data
        cnx.commit() # save the changes to the database
        # Create a dictionary for new recipe
        new_recipe = {
            'category_id': category_id,
            'description': request_data['description'],
            'id': cursor.lastrowid,
            'name': request_data['name'],
            'state_id': 1,
            'user_id': logged_in_user['id']}
        cursor.close()
        return new_recipe
    except Exception as e:
        cnx.rollback() # reverse in case of an error
        print(e)
        raise e

# db query for getting recipe by id
def get_recipe_by_id(cnx, recipe_id):
    cursor = cnx.cursor()
    _query = "SELECT * FROM recipe WHERE id = (%s)"
    cursor.execute(_query, (recipe_id,))
    recipe = cursor.fetchone()
    cursor.close()
    if recipe is None:
        raise Exception('Recipe not found')
    return {'id': recipe[0],
            'name': recipe[1],
            'description': recipe[2],
            'created_at': recipe[3],
            'deleted_at': recipe[4],
            'user_id': recipe[5],
            'category_id': recipe[6],
            'state_id': recipe[7]}

# db query for changing recipe by id
def update_recipe_by_id(cnx, recipe, request_data, logged_in_user):
    try:
        if logged_in_user['id'] != recipe['user_id'] and logged_in_user['role'] != 4: # condition who can change the recipe
            raise Exception('You are not authorized to update this recipe') # if condition is not met show error message
        else:
            # else allow changes to be made
            cursor = cnx.cursor()
            _query = "UPDATE recipe SET name = (%s), description = (%s) WHERE id = (%s)"
            cursor.execute(_query, (request_data['name'], request_data['description'], recipe['id']))
            cnx.commit()
            cursor.close()
    except Exception as e:
        cnx.rollback()
        print(e)
        raise e

# db query for deleting recipe by id
def delete_recipe_by_id(cnx, recipe_id, recipe, logged_in_user):
    try:
        if logged_in_user['id'] != recipe['user_id'] and logged_in_user['role'] != 4:
            # print(logged_in_user['id']) # for debugging
            # print(recipe['user_id']) # for debugging
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
