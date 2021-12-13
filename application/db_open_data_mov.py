import mysql.connector as mariadb
from datetime import datetime
import pandas as pd
import json
import pathlib
import pandas as pd

query_insert_metrics = "INSERT INTO medicion (id_vista, id_metrica, valor, fecha) VALUES (%s,%s,%s,NOW())"
query_insert_tracking = "INSERT INTO tracking_medicion (fecha, direccion, objeto, id_camara) VALUES (NOW(),%s,%s,%s)"

# get relative data folder
PATH = pathlib.Path(__file__).parent
CONFIG_PATH = PATH.joinpath("config").resolve()
credential = pd.read_json(CONFIG_PATH.joinpath("credential_mov.json"), typ='series')

# post movility metrics
def post_mov(data):

    html_response = ""

    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )

    cursor = db_connection.cursor()
    try:
        cursor.execute(query_insert_metrics, (data['ID_Vista'],1,data['Persona']))
        cursor.execute(query_insert_metrics, (data['ID_Vista'],2,data['Carros']))
        cursor.execute(query_insert_metrics, (data['ID_Vista'],3,data['Camion']))
        cursor.execute(query_insert_metrics, (data['ID_Vista'],4,data['Autobus']))
        cursor.execute(query_insert_metrics, (data['ID_Vista'],5,data['Motor']))
        db_connection.commit()
        html_response = "201 Created"

    except mariadb.Error as error:
        print("Error: {}".format(error))
        html_response = "400 Bad Request"

    cursor.close()
    db_connection.close()

    return html_response

def post_movement_tracking(data):

    html_response = ""

    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )

    cursor = db_connection.cursor()
    try:
        cursor.execute(query_insert_tracking, (data['direccion'],data['objeto'],data['id_camara']))
        db_connection.commit()
        html_response = "201 Created"

    except mariadb.Error as error:
        print("Error: {}".format(error))
        html_response = "400 Bad Request"

    cursor.close()
    db_connection.close()

    return html_response