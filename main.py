from flask import Flask, render_template, jsonify, request

import data.categories
from db import connect_to_dbx, connect_to_db

webserver = Flask(__name__)


# palautetaan data tietokannasta html tiedoston categories.html ul listassa
# käytetään huonompaa yhteyden muodostusta ja
# http://localhost:3000/categories
@webserver.route('/categories')
def categories():
    try:
        cnx = connect_to_dbx()
        # ajattele kursoria kirjanmerkkinä, joka kulkee sivujen läpi (osoitin missä ollaan menossa)
        cursor = cnx.cursor()
        _query = "SELECT * FROM categories"
        cursor.execute(_query)
        # fetchall hakee kaikki rivit jotka kysely tuottaa
        categories = cursor.fetchall()

        cursor.close()
        cnx.close()
        return render_template('categories.html', rows=categories)
    except Exception as e:
        return render_template('error.html', str(e))

@webserver.route('/api/categories/<category_id>')
def category_handler(category_id):
    with connect_to_db() as cnx:
        try:
            category = data.categories.get_category_by_id(cnx, category_id)
            return jsonify({'category': category})
        except Exception as e:
            return jsonify({'error': str(e)}), 404

# palautetaan data tietokannasta json datana
# http://localhost:3000/api/categories
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
            reg_body = request.get_json()
            print(reg_body)
            return ""


# tämä ehto estää Flask-webserverin käynnistymisen, jos main tuodaan/importataan toiseen scriptiin
# webserverin on tarkoitus käynnistyä vain silloin kun main.py suoritetaan python-komennolla
if __name__ == '__main__':  # muista että ehtolauseen ehto loppuu kaksoispisteeseen
    webserver.run(port=3000)
