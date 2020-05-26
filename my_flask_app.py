from flask import Flask, render_template, request, jsonify
#Luego de las pruebas, eliminar db_test & db_prueba_manuel
from application import db_open_data_io, covid_app, db_test, db_prueba_manuel

server = Flask(__name__)

@server.route("/")
def index():
    return render_template("index.html")

@server.route("/working_on")
def working_on():
        return render_template("working_on.html")

@server.route("/csd")
def csd():
        return render_template("csd.html")

@server.route("/datosabiertos")
def datosabiertos():
        return render_template("datosabiertos.html")

@server.route("/login")
def login():
        return render_template("login.html")

@server.route("/api/v1/ambiental", methods=['GET', 'POST'])
def api_v1_ambientales():
        if request.method == 'POST':
                data = request.get_json()
                return db_open_data_io.post_ambiental(data)
        if request.method == 'GET':
                results = db_open_data_io.get_ambiental()
                return jsonify(results)

@server.route("/api/v1/internas", methods=['GET', 'POST'])
def api_v1_internas():
        if request.method == 'POST':
                data = request.get_json()
                return db_open_data_io.post_interna(data)
        if request.method == 'GET':
                results = db_open_data_io.get_interna()
                return jsonify(results)

#Prueba de la parte de duquesa
@server.route("/api/v1/duquesa", methods=['GET', 'POST'])
def api_v1_duquesa():
        if request.method == 'POST':
                data = request.get_json()
                return db_test.duquesa(data)
        if request.method == 'GET':
                results = db_test.query_duquesa()
                return jsonify(results)

#Prueba de la parte de Manuel
@server.route("/api/prueba/ambiental", methods=['GET', 'POST'])
def api_prueba_ambiental():
        if request.method == 'POST':
                data = request.get_json()
                return db_prueba_manuel.post_ambiental(data)
        if request.method == 'GET':
                results = db_prueba_manuel.get_ambiental()
                return jsonify(results)
#Prueba de la parte de Manuel
@server.route("/api/prueba/interna", methods=['GET', 'POST'])
def api_prueba_interna():
        if request.method == 'POST':
                data = request.get_json()
                return db_prueba_manuel.post_interna(data)
        if request.method == 'GET':
                results = db_prueba_manuel.get_interna()
                return jsonify(results)

covid = covid_app.covid_dash(server, '/covid/')

if __name__ == "__main__":
    server.run()
    #covid.run_server(debug=True)