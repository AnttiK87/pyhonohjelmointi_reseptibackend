import jwt
from flask import Flask, jsonify, request

import data.categories
import data.recipes
import data.users
from db import connect_to_db

webserver = Flask(__name__)


# palautetaan data tietokannasta html tiedoston categories.html ul listassa
# käytetään huonompaa yhteyden muodostusta.
# http://localhost:3000/categories
# @webserver.route('/categories')
# def categories():
#     try:
#         cnx = connect_to_dbx()
#         # ajattele kursoria kirjanmerkkinä, joka kulkee sivujen läpi (osoitin missä ollaan menossa)
#         cursor = cnx.cursor()
#         _query = "SELECT * FROM categories"
#         cursor.execute(_query)
#         # fetchall hakee kaikki rivit jotka kysely tuottaa
#         categories = cursor.fetchall()
#
#         cursor.close()
#         cnx.close()
#         return render_template('categories.html', rows=categories)
#     except Exception as e:
#         return render_template('error.html', str(e))

def get_db_connection(route_handler):
    def wrapper(*args, **kwargs):
        # with blockia voidaan käyttää, kun contextlib.contexmanager dekoraattori on käytössä
        # db.py tiedoston connect_to_db tiedoston yläpuolella
        with connect_to_db() as cnx:  # cnx on yieldattu yhteys
            return route_handler(cnx, *args, **kwargs)

    return wrapper


def require_login(route_handler):
    def wrapper(cnx, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return jsonify({'err': 'Unauthorized'}), 401

            token_parts = auth_header.split(' ')
            if len(token_parts) != 2:
                return jsonify({'err': 'Unauthorized'}), 401

            if token_parts[0] != 'Bearer':
                return jsonify({'err': 'Unauthorized'}), 401

            token = token_parts[1]
            payload = jwt.decode(token, data.users.SECRET, algorithms=['HS256'])

            logged_in_user = data.users.get_logged_in_user(cnx, payload['sub'])
            return route_handler(cnx, logged_in_user, *args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({'err': 'Unauthorized'}), 401

    return wrapper


def require_role(role_id):
    def decorator(route_handler):
        def wrapper(cnx, logged_in_user, *args, **kwargs):
            if logged_in_user['role'] == role_id:
                return route_handler(cnx, logged_in_user, *args, **kwargs)
            raise Exception('Forbidden')

        return wrapper

    return decorator


@webserver.route('/api/account')
@get_db_connection
@require_login
def get_account(logged_in_user):
    return jsonify({'account': logged_in_user})

@webserver.route('/api/register', methods=['POST'])
@get_db_connection
def register(cnx):
    try:
        reg_body = request.get_json()
        user = data.users.register(cnx, reg_body)
        return jsonify(user)
    except Exception as e:
        return jsonify({'err': str(e)}), 500
@webserver.route('/api/login', methods=['POST'])
@get_db_connection
def login(cnx):
    try:
        reg_body = request.get_json()
        access_token = data.users.login(cnx, reg_body)
        return jsonify({'access_token': access_token})
    except Exception as e:
        return jsonify({'err': str(e)}), 500


@webserver.route('/api/logout', methods=['POST'], endpoint='logout')
@get_db_connection
@require_login
def logout(cnx, logged_in_user):
    try:
        data.users.logout(cnx, logged_in_user)
        return "logged out", 200
    except Exception as e:
        return jsonify({'err': str(e)}), 500


# palautetaan data tietokannasta json datana
# http://localhost:3000/api/categories
# Kaikkien tietueiden haku ja uuden lisääminen
@webserver.route('/api/categories', methods=['POST', 'GET'])
@get_db_connection
def categories_handler(cnx):
    if request.method == 'GET':

        try:
            categories = data.categories.get_categories(cnx)
            return jsonify(categories)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            reg_body = request.get_json()
            category = data.categories.insert_category(cnx, reg_body)
            return jsonify(category)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# http://localhost:3000/api/categories/id
# haku, poisto ja muokkaus id:n mukaan
@webserver.route('/api/categories/<category_id>', methods=['GET', 'PUT', 'DELETE'])
@get_db_connection
def category_handler(cnx, category_id):
    if request.method == 'GET':
        try:
            category = data.categories.get_category_by_id(cnx, category_id)
            return jsonify({'category': category})
        except Exception as e:
            return jsonify({'error': str(e)}), 404
    elif request.method == 'PUT':
        try:
            reg_body = request.get_json()
            category = data.categories.get_category_by_id(cnx, category_id)
            data.categories.update_category_by_id(cnx, category, reg_body)
            return jsonify({'category': {
                'id': category['id'],
                'name': reg_body['name']
            }})
        except Exception as e:
            return jsonify({'error': str(e)}), 404
    elif request.method == 'DELETE':
        try:
            affected_rows = data.categories.delete_category_by_id(cnx, category_id)
            if affected_rows == 0:
                return jsonify({'error': 'Category not found'}), 404
            else:
                return "Deleted successfully", 200
        except Exception as e:
            return jsonify({'error': str(e)}), 404


@webserver.route('/api/categories/<category_id>/recipes', methods=['POST', 'GET'])
@get_db_connection
def recipes_handler(cnx, category_id):
    if request.method == 'GET':

        try:
            recipes = data.recipes.get_recipes_by_category(cnx, category_id)
            return jsonify(recipes)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            reg_body = request.get_json()
            recipe = data.recipes.insert_recipe_by_category(cnx, reg_body, category_id)
            return jsonify(recipe)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@webserver.route('/api/recipes/<recipe_id>', methods=['GET', 'PUT', 'DELETE'])
@get_db_connection
def recipe_handler(cnx, recipe_id):
    if request.method == 'GET':
        try:
            recipe = data.recipes.get_recipe_by_id(cnx, recipe_id)
            return jsonify({'recipe': recipe})
        except Exception as e:
            return jsonify({'error': str(e)}), 404
    elif request.method == 'PUT':
        try:
            reg_body = request.get_json()
            recipe = data.recipes.get_recipe_by_id(cnx, recipe_id)
            data.recipes.update_recipe_by_id(cnx, recipe, reg_body)
            return jsonify({'recipe': {
                'category_id': recipe['category_id'],
                'created_at': recipe['created_at'],
                'deleted_at': recipe['deleted_at'],
                'description': reg_body['description'],
                'id': recipe['id'],
                'name': reg_body['name'],
                'state_id': recipe['state_id'],
                'user_id': recipe['user_id'],
            }})
        except Exception as e:
            return jsonify({'error': str(e)}), 404
    elif request.method == 'DELETE':
        try:
            affected_rows = data.recipes.delete_recipe_by_id(cnx, recipe_id)
            if affected_rows == 0:
                return jsonify({'error': 'Category not found'}), 404
            else:
                return "Deleted successfully", 200
        except Exception as e:
            return jsonify({'error': str(e)}), 404


@webserver.route('/api/users/<user_id>', methods=['DELETE'], endpoint='delete_user')
@get_db_connection
@require_login
@require_role(4)
def delete_user(cnx, user_id):
    try:
        data.users.remove_user_by_id(cnx, user_id)
        return ""
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# tämä ehto estää Flask-webserverin käynnistymisen, jos main tuodaan/importataan toiseen scriptiin
# webserverin on tarkoitus käynnistyä vain silloin kun main.py suoritetaan python-komennolla
if __name__ == '__main__':  # muista että ehtolauseen ehto loppuu kaksoispisteeseen
    webserver.run(port=3000)
