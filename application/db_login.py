import mysql.connector as mariadb
from datetime import datetime
import pandas as pd
import json
import pathlib
import pandas as pd


query_login = "SELECT password FROM LoginInfo WHERE username = %s"


# get relative data folder
PATH = pathlib.Path(__file__).parent
CONFIG_PATH = PATH.joinpath("config").resolve()
credential = pd.read_json(CONFIG_PATH.joinpath("log_credential.json"), typ='series')



def  login_check(username, password):
    
    db_connection = mariadb.connect(
        user=credential["DB_USER"], 
        password=credential["DB_PASS"], 
        database=credential["DB"]
        )
    try:       
        cursor = db_connection.cursor()
        cursor.execute(query_login, (username,))
        result = cursor.fetchall()
    except mariadb.Error as error:
        print("Error: {}".format(error))
    cursor.close()
    db_connection.close()
    print(result[0][0])
    if password == result[0][0]:
        return True

    return False
 