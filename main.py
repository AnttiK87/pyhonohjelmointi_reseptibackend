from flask import Flask, render_template, jsonify, request

import data.categories
import data.recipes
import data.users
from db import connect_to_dbx, connect_to_db

webserver = Flask(__name__)


# palautetaan data tietokannasta html tiedoston categories.html ul listassa
# käytetään huonompaa yhteyden muodostusta ja
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

@webserver.route('/api/register', methods=['POST'])
def register():
    with connect_to_dbx() as cnx:
        try:
            reg_body = request.get_json()
            user = data.users.register(cnx, reg_body)
            return jsonify(user)
        except Exception as e:
            return jsonify({'err': str(e)}), 500


# palautetaan data tietokannasta json datana
# http://localhost:3000/api/categories
# Kaikkien tietueiden haku ja uuden lisääminen
@webserver.route('/api/categories', methods=['POST', 'GET'])
def categories_handler():
    # with blockia voidaan käyttää, kun contextlib.contexmanager dekoraattori on käytössä
    # db.py tiedoston connect_to_db tiedoston yläpuolella
    with connect_to_db() as cnx:  # cnx on yieldattu yhteys

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
def category_handler(category_id):
    with connect_to_db() as cnx:
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
def recipes_handler(category_id):
    with connect_to_db() as cnx:

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
def recipe_handler(recipe_id):
    with connect_to_db() as cnx:
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


# tämä ehto estää Flask-webserverin käynnistymisen, jos main tuodaan/importataan toiseen scriptiin
# webserverin on tarkoitus käynnistyä vain silloin kun main.py suoritetaan python-komennolla
if __name__ == '__main__':  # muista että ehtolauseen ehto loppuu kaksoispisteeseen
    webserver.run(port=3000)
