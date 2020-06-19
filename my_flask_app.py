from flask import Flask, render_template, request, jsonify, make_response
from application import db_open_data_io, aqi_app

#Luego de las pruebas, eliminar db_test & db_prueba_manuel
from application import db_test, db_prueba_manuel

server = Flask(__name__)

#Render de las paginas HTML
@server.route("/")
def index():
    return render_template("index.html")

@server.route("/calidadaire")
def calidadaire():
        return render_template("calidadaire.html")

@server.route("/ruido")
def ruido():
        return render_template("working_on.html")

@server.route("/thp")
def thp():
        return render_template("working_on.html")

@server.route("/csd")
def csd():
        return render_template("csd.html")

@server.route("/csi")
def csi():
        return render_template("working_on.html")

@server.route("/datosabiertos")
def datosabiertos():
        return render_template("datosabiertos.html")

@server.route("/documentacion")
def documentacion():
        return render_template("working_on.html")

@server.route("/login")
def login():
        return render_template("login.html")

#RESTful APIs de la plataforma
@server.route("/api/v1/ambiental", methods=['GET', 'POST'])
def api_v1_ambientales():
        if request.method == 'POST':
                data = request.get_json()
                return db_open_data_io.post_ambiental(data)
        if request.method == 'GET':
                format = request.args.get("formato")
                start_date = request.args.get("inicio")
                end_date = request.args.get("fin")

                results = db_open_data_io.get_ambiental(format,start_date,end_date)
                if format =='csv':
                        resp = make_response(results)
                        resp.headers["Content-Disposition"] = "attachment; filename=smartcampuspucmm.csv"
                        resp.headers["Content-Type"] = "text/csv"
                        return resp

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

@server.route("/api/prueba/interna", methods=['GET', 'POST'])
def api_prueba_interna():
        if request.method == 'POST':
                data = request.get_json()
                return db_prueba_manuel.post_interna(data)
        if request.method == 'GET':
                results = db_prueba_manuel.get_interna()
                return jsonify(results)

# Cargar los dashboards desarrollados en dash
aqi = aqi_app.aqi_dash(server, '/aqi/')

#parte principal (main)
if __name__ == "__main__":
    server.run()
    #covid.run_server(debug=True)