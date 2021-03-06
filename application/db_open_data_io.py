import mysql.connector as mariadb
from datetime import datetime
import pandas as pd
import json
import pathlib
import pandas as pd


query_num_serial = "SELECT ID_Modulo FROM Modulo WHERE Num_serial = %s"
query_var_ambiental = "SELECT ID_VA FROM Variables_ambientales WHERE Nombre = %s"
query_var_interna = "SELECT ID_VI FROM Variables_Internas WHERE Nombre = %s"
query_insert_ambiental = "INSERT INTO Medidas_Ambientales (ID_Variables_ambientales, ID_Modulo, Valor, Fecha) VALUES (%s,%s,%s,%s)"
query_insert_interna = "INSERT INTO Medida_internas (ID_Variables_Internas, ID_Modulo, Valor, Fecha) VALUES (%s,%s,%s,%s)"
query_select_interna = "select Nombre, ID_Modulo, Valor, Fecha from Medida_internas, Variables_Internas where ID_VI = ID_Variables_Internas order by Fecha;"

query_select_ambiental_all = "select Medidas_Ambientales.ID_Modulo as ID_Modulo,Latitud, Longitud, Altitud, Nombre, Valor, Fecha from Medidas_Ambientales, Variables_ambientales, Posicion where ID_VA = ID_Variables_ambientales and Posicion.ID_Modulo = Medidas_Ambientales.ID_Modulo and Fecha >= Fecha_Inicial and (Fecha <= Fecha_Final or Fecha_Final is null);"
query_select_ambiental_by_date = "select Medidas_Ambientales.ID_Modulo as ID_Modulo,Latitud, Longitud, Altitud, Nombre, Valor, Fecha from Medidas_Ambientales, Variables_ambientales, Posicion where ID_VA = ID_Variables_ambientales and Posicion.ID_Modulo = Medidas_Ambientales.ID_Modulo and Fecha >= Fecha_Inicial and (Fecha <= Fecha_Final or Fecha_Final is null) and Fecha "

api_date_format = '%Y-%m-%d'
post_date_format = '%a, %y/%m/%d, %H:%M:%S'
get_date_format = '%Y/%m/%d, %H:%M:%S'

# get relative data folder
PATH = pathlib.Path(__file__).parent
CONFIG_PATH = PATH.joinpath("config").resolve()
credential = pd.read_json(CONFIG_PATH.joinpath("credential.json"), typ='series')

def validate_api_date(date_text):
    try:
        datetime.strptime(date_text, api_date_format)
        return True
    except ValueError:
        return False

def post_ambiental(data):

    html_response = ""

    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    cursor = db_connection.cursor()
    valor = float(data['Valor'])
    fecha = datetime.strptime(data['Timestamp'], post_date_format)

    try:
        cursor.execute(query_num_serial, (data['Numero_Serial'],))
        id_modulo = cursor.fetchall()
        cursor.execute(query_var_ambiental, (data['Variable'],))
        id_var = cursor.fetchall()
        if id_modulo and id_var:
            cursor.execute(query_insert_ambiental, (id_var[0][0], id_modulo[0][0], valor, fecha)) 
            db_connection.commit()
            html_response = "201 Created"
        else:
            html_response = "204 No Content"
    except mariadb.Error as error:
        print("Error: {}".format(error))
        html_response = "400 Bad Request"

    cursor.close()
    db_connection.close()

    return html_response

def post_interna(data):

    html_response = ""

    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    cursor = db_connection.cursor()
    valor = float(data['Valor'])
    fecha = datetime.strptime(data['Timestamp'], post_date_format)

    try:
        cursor.execute(query_num_serial, (data['Numero_Serial'],))
        id_modulo = cursor.fetchall()
        cursor.execute(query_var_interna, (data['Variable'],))
        id_var = cursor.fetchall()
        if id_modulo and id_var:
            cursor.execute(query_insert_interna, (id_var[0][0], id_modulo[0][0], valor, fecha)) 
            db_connection.commit()
            html_response = "201 Created"
        else:
            html_response = "204 No Content"
    except mariadb.Error as error:
        print("Error: {}".format(error))
        html_response = "400 Bad Request"

    cursor.close()
    db_connection.close()

    return html_response

def get_ambiental(format, inicio, fin):
    results = []
    row_headers = []
    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )

    if None not in [inicio,fin]:
        if not validate_api_date(inicio) and not validate_api_date(fin):
            return "Formato de fecha incorrecto, por favor ver la documentación"
        
        dt_inicio = datetime.combine(datetime.strptime(inicio, api_date_format), datetime.min.time())
        dt_fin = datetime.combine(datetime.strptime(fin, api_date_format), datetime.max.time())
        query = query_select_ambiental_by_date + "Between %s and %s;"
        try:       
            cursor = db_connection.cursor()
            cursor.execute(query, (dt_inicio, dt_fin))
            row_headers=[x[0] for x in cursor.description]
            results = cursor.fetchall()
        except mariadb.Error as error:
            print("Error: {}".format(error))
        cursor.close()
        db_connection.close()
            
    elif inicio != None:
        if not validate_api_date(inicio):
            return "Formato de fecha incorrecto, por favor ver la documentación"
        
        dt_inicio = datetime.combine(datetime.strptime(inicio, api_date_format), datetime.min.time())
        query = query_select_ambiental_by_date + ">= %s"
        try:       
            cursor = db_connection.cursor()
            cursor.execute(query, (dt_inicio,))
            row_headers=[x[0] for x in cursor.description]
            results = cursor.fetchall()
        except mariadb.Error as error:
            print("Error: {}".format(error))
        cursor.close()
        db_connection.close()

    elif fin != None:
        if not validate_api_date(fin):
            return "Formato de fecha incorrecto, por favor ver la documentación"
        
        dt_fin = datetime.combine(datetime.strptime(fin, api_date_format), datetime.max.time())
        query = query_select_ambiental_by_date + "<= %s"
        try:       
            cursor = db_connection.cursor()
            cursor.execute(query, (dt_fin,))
            row_headers=[x[0] for x in cursor.description]
            results = cursor.fetchall()
        except mariadb.Error as error:
            print("Error: {}".format(error))
        cursor.close()
        db_connection.close()

    else:
        try:       
            cursor = db_connection.cursor()
            cursor.execute(query_select_ambiental_all)
            row_headers=[x[0] for x in cursor.description]
            results = cursor.fetchall()
        except mariadb.Error as error:
            print("Error: {}".format(error))
        cursor.close()
        db_connection.close()
    
    if format == 'csv':
        data = pd.DataFrame(data=results, columns=row_headers)
        data['Fecha'].apply(lambda x: x.strftime(get_date_format))
        return data.to_csv()
    else:
        data = []
        for row in results:
            data.append(dict(zip(row_headers, row)))
        for x in data:
            x['Fecha'] = x['Fecha'].strftime(get_date_format)
        
        return data

def get_interna():
    results = []
    row_headers = []
    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    try:       
        cursor = db_connection.cursor()
        cursor.execute(query_select_interna)
        row_headers=[x[0] for x in cursor.description]
        results = cursor.fetchall()
    except mariadb.Error as error:
        print("Error: {}".format(error))
    cursor.close()
    db_connection.close()
    data = []
    for row in results:
        data.append(dict(zip(row_headers, row)))
    for x in data:
        x['Fecha'] = x['Fecha'].strftime(get_date_format)

    return data
 