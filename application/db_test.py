import mysql.connector as mariadb
from datetime import datetime
import json

query_num_serial = "SELECT ID_Modulo FROM Modulo WHERE Num_serial = %s"
query_var_ambiental = "SELECT ID_VA FROM Variables_ambientales WHERE Nombre = %s"
query_var_interna = "SELECT ID_VI FROM Variables_Internas WHERE Nombre = %s"
query_insert_ambiental = "INSERT INTO Medidas_Ambientales (ID_Variables_ambientales, ID_Modulo, Valor, Fecha) VALUES (%s,%s,%s,%s)"
query_insert_interna = "INSERT INTO Medida_internas (ID_Variables_Internas, ID_Modulo, Valor, Fecha) VALUES (%s,%s,%s,%s)"
query_select_ambiental = "select Nombre, ID_Modulo, Valor, Fecha from Medidas_Ambientales, Variables_ambientales where ID_VA = ID_Variables_ambientales order by Fecha;"
query_select_interna = "select Nombre, ID_Modulo, Valor, Fecha from Medida_internas, Variables_Internas where ID_VI = ID_Variables_Internas order by Fecha;"

with open('config/credential.json') as f:
        credential = json.load(f)

def duquesa(data):

    html_response = ""

    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    cursor = db_connection.cursor()
    valor = float(data['Valor'])
    fecha = datetime.strptime(data['Timestamp'], '%a, %y/%m/%d, %H:%M:%S')
    if data['Tipo_Medida']==1:
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
    else:
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

def query_duquesa():
    results = []
    row_headers = []
    data = []
    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    try:       
        cursor = db_connection.cursor()
        cursor.execute(query_select_ambiental)
        row_headers=[x[0] for x in cursor.description]
        results = cursor.fetchall()
        for row in results:
            data.append(dict(zip(row_headers, row)))
        
        cursor.execute(query_select_interna)
        results = cursor.fetchall()
        for row in results:
            data.append(dict(zip(row_headers, row)))
        cursor.close()
        db_connection.close()
    except mariadb.Error as error:
        print("Error: {}".format(error))

    for x in data:
        x['Fecha'] = x['Fecha'].strftime('%y/%m/%d, %H:%M:%S')

    return data

 