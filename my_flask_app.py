from flask import Flask, render_template, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException
from application import db_open_data_io, aqi_app, ruido_app, thp_app



from flask import request, session, abort, flash
import os
from application import db_login


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

#--------------------------------------------------------
#TEST login-logout
@server.route("/login2", methods=['POST'])
def do_admin_login():
        if db_login.login_check(request.form['usuario'], request.form['contrasena']):
        #if request.form['contrasena']=='password' and request.form['usuario']=='admin':
                session['logged_in']=True
        else:
                flash('wrong password!')
        return control()

@server.route("/logout")
def logout():
        session['logged_in']=False
        return login()

@server.route("/control")
def control():
        if session.get('logged_in'):
                return render_template("/logged/home.html")
        else:
                return error404()

#--------------------------------------------------------


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

@server.route("/api/movilidad", methods=['GET', 'POST'])
def api_movilidad():
        if request.method == 'POST':
                data = request.get_json()
                return "201 Created"
        if request.method == 'GET':
                return "204 No Content"

# Cargar los dashboards desarrollados en dash
calidadaire = aqi_app.aqi_dash(server, '/calidadaire/')
ruido = ruido_app.ruido_dash(server, '/ruido/')
thp = thp_app.thp_dash(server, '/thp/')
#covid = covid_dash.covid_dash(server, '/precitas/')

#Manejo de paginas no encontradas
@server.errorhandler(HTTPException)
def page_not_found(e):
        return render_template("default.html")

#parte principal (main)
if __name__ == "__main__":
        server.register_error_handler(404, page_not_found)
        server.secret_key = os.urandom(12)
        server.run()
