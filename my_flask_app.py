from flask import Flask, render_template, request, jsonify, make_response, send_file
from application import db_open_data_io, aqi_app, ruido_app, thp_app

#Luego de las pruebas, eliminar db_prueba_manuel
from application import db_prueba_manuel

server = Flask(__name__)

#Render de las paginas HTML
@server.route("/")
def index():
    return render_template("index.html")

#@server.route("/thp")
#def thp():
#        return render_template("working_on.html")

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

@server.route("/paneldatos")
def paneldatos():
        return render_template("paneldatos.html")

@server.route("/login")
def login():
        return render_template("login.html")

@server.route("/error")
def error404():
        return render_template("default.html")

@server.route("/metadata")
def metadata():
        path='templates/smartcampus-metadata.xml'
        return send_file(path, as_attachment=True)

#RESTful APIs de la plataforma
@server.route("/api/v1/ambiental", methods=['GET', 'POST'])
def api_v1_ambientales():
        if request.method == 'POST':
                data = request.get_json()
                return db_open_data_io.post_ambiental(data)
        if request.method == 'GET':
                format_type = request.args.get("formato")
                start_date = request.args.get("inicio")
                end_date = request.args.get("fin")
                
                results = db_open_data_io.get_ambiental(format_type,start_date,end_date)
                if format_type =='csv':
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
calidadaire = aqi_app.aqi_dash(server, '/calidadaire/')
ruido = ruido_app.ruido_dash(server, '/ruido/')
thp = thp_app.thp_dash(server, '/thp/')

#Manejo de paginas no encontradas
def page_not_found(e):
        return render_template("default.html")
#parte principal (main)
if __name__ == "__main__":
        server.register_error_handler(404, page_not_found)
        server.run()
