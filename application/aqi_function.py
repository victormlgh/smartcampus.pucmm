#Función para descargar AQI por tiempo especifico, para la el departamento de comunicación de la PUCMM

import pathlib
import dash
import datetime as dt
import pandas as pd
import requests
import aqi

date_format='%Y/%m/%d, %H:%M:%S'
dpr_format = '%Y-%m-%d' #Date Picker Range format
aq_api_url = "http://smartcampus.pucmm.edu.do/api/v1/ambiental"

def load_data():
    df = pd.DataFrame.from_dict(requests.get(aq_api_url).json())
    #df.loc[df['ID_Modulo'].isin([csi_modulo,csd_modulo])]           #Modulos de AQ de CSI & CSD
    df['Fecha'] = pd.to_datetime(df['Fecha'], format=date_format)
    df['Valor'] =df['Valor'].replace(to_replace=-1, value=0)
    df.loc[df['Nombre']=='Gas_NO2', 'Valor'] *=1000                 #llevamos los valores de NO2 de PPM a PPB
    df.loc[df['Nombre']=='Gas_SO2', 'Valor'] *=1000                 #llevamos los valores de SO2 de PPM a PPB
    
    return df

#Filtro del Data Frame
def filter_dataframe(df, date_type_selector, time_range_start, time_range_end):
    
    start_date=dt.datetime.combine(dt.datetime.strptime(time_range_start, dpr_format), dt.datetime.min.time())
    end_date = dt.datetime.combine(dt.datetime.strptime(time_range_end, dpr_format), dt.datetime.max.time())

    dff = df.loc[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]

    dff = dff.groupby(['Nombre',pd.Grouper(key='Fecha', freq=date_type_selector)]).agg({'Valor':'mean'})
    dff = dff.reset_index()

    return dff

#Calcula el Indice de Calidad del Aire (AQI) con los distintos contaminantes
def calculate_aqi(row):

    value = aqi.to_aqi([
        (aqi.POLLUTANT_PM25, row.loc['PM25']["Valor"]),
        (aqi.POLLUTANT_PM10, row.loc['PM10']["Valor"]),
        (aqi.POLLUTANT_O3_8H, row.loc['Gas_O3']["Valor"]),
        (aqi.POLLUTANT_CO_8H, row.loc['Gas_CO']["Valor"]),
        (aqi.POLLUTANT_SO2_1H, row.loc['Gas_SO2']["Valor"]),
        (aqi.POLLUTANT_NO2_1H, row.loc['Gas_NO2']["Valor"]),
    ])
    
    return value

df = filter_dataframe(load_data(), 'D', '2020-05-07', '2020-06-24')

dates = pd.to_datetime(df['Fecha'].unique(), format=date_format)
aqi_values = []
for date in dates:
    dff = df.loc[df['Fecha']==date]
    dff.set_index('Nombre', inplace=True)
    aqi_values.append(int(calculate_aqi(dff)))

pd.DataFrame(list(zip(dates,aqi_values)), columns=['Fecha','AQI']).to_csv('dia.csv')

