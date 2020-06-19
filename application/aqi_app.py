import pathlib
import dash
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.graph_objects as go
import requests
import aqi

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

#AirQuality Data URL
aq_api_url = "http://smartcampus.pucmm.edu.do/api/v1/ambiental"

#Date format
date_format='%Y/%m/%d, %H:%M:%S'
dpr_format = '%Y-%m-%d' #Date Picker Range format

#ID_Modulos Calidad del Aire en Campus PUCMM
csi_modulo = 2
csd_modulo = 2

def aqi_dash(server, route):

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=route)

    # App layout section
    app.layout = html.Div(
        [
            # empty Div to trigger javascript file for graph resizing
            html.Br(),
            html.Br(),
            html.Div(
                [
                    html.Div(
                        [
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("PUCMM.png"),
                                    id="pucmm-logo",
                                    style={
                                        "height": "70px",
                                        "width": "auto",
                                        "margin-bottom": "25px",
                                    },
                                ),
                                href="https://pucmm.edu.do/",
                            )
                            
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Índice de calidad del aire y sus contaminantes",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    html.H5(
                                        id="fecha_actualizado_text", style={"margin-top": "0px"}
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            #Indicadores de calidad de aire y contaminantes de CSI
            html.Div(
                [ 
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P("Índice de Calidad del Aire"),
                                    daq.Gauge(
                                        id="csi_aq_gauge",
                                        max=500,
                                        min=0,
                                        color={'default':'#4285f4'},
                                        showCurrentValue=True,  # default size 200 pixel
                                    ),
                                ],
                                className="mini_container",
                            ),
                            html.Div(
                                [
                                    html.H5("Campus Santiago"),
                                    html.P(
                                        "Nivel actual de los contaminantes",
                                        className="control_label",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H6(id="csi_pm1_text"), html.P("Particulado PM1")], 
                                                id="csi_pm1",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_pm25_text"), html.P("Particulado PM2.5")],
                                                id="csi_pm25",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_pm10_text"), html.P("Particulado PM10")], 
                                                id="csi_pm10",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_co_text"), html.P("Monóxido de Carbono (CO)")], 
                                                id="csi_co",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_no2_text"), html.P("Dióxido de Nitrógeno (NO\u2082)")],
                                                id="csi_no2",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="csi_info_container",
                                        className="row container-display",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H6(id="csi_o3_text"), html.P("Ozono (O\u2083)")],
                                                id="csi_o3",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_so2_text"), html.P("Dióxido de Azufre (SO\u2082)")],
                                                id="csi_so2",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_temp_text"), html.P("Temperatura")],
                                                id="csi_temp",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_pres_text"), html.P("Presión Atmosférica")], 
                                                id="csi_pres",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csi_hum_text"), html.P("Humedad relativa")], 
                                                id="csi_hum",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="csi_info_container2",
                                        className="row container-display",
                                    ),
                                ],   
                            )   
                        ],
                        id="csi_aq_cont",
                        className="row container-display",
                    ),
                ],
                className="row flex-display",
            ),

            #Indicadores de calidad de aire y contaminantes de CSD
            html.Div(
                [ 
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P("Índice de Calidad del Aire"),
                                    daq.Gauge(
                                        id="csd_aq_gauge",
                                        max=500,
                                        min=0,
                                        color={'default':'#4285f4'},
                                        showCurrentValue=True,  # default size 200 pixel
                                    ),
                                ],
                                className="mini_container",
                            ),
                            html.Div(
                                [
                                    html.H5("Campus Santo Domingo"),
                                    html.P(
                                        "Nivel actual de los contaminantes",
                                        className="control_label",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H6(id="csd_pm1_text"), html.P("Particulado PM1")], 
                                                id="csd_pm1",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_pm25_text"), html.P("Particulado PM2.5")],
                                                id="csd_pm25",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_pm10_text"), html.P("Particulado PM10")], 
                                                id="csd_pm10",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_co_text"), html.P("Monóxido de Carbono (CO)")], 
                                                id="csd_co",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_no2_text"), html.P("Dióxido de Nitrógeno (NO\u2082)")],
                                                id="csd_no2",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="csd_info_container",
                                        className="row container-display",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H6(id="csd_o3_text"), html.P("Ozono (O\u2083)")],
                                                id="csd_o3",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_so2_text"), html.P("Dióxido de Azufre (SO\u2082)")],
                                                id="csd_so2",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_temp_text"), html.P("Temperatura")],
                                                id="csd_temp",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_pres_text"), html.P("Presión Atmosférica")], 
                                                id="csd_pres",
                                                className="mini_container",
                                            ),
                                            html.Div(
                                                [html.H6(id="csd_hum_text"), html.P("Humedad relativa")], 
                                                id="csd_hum",
                                                className="mini_container",
                                            ),
                                        ],
                                        id="csd_info_container2",
                                        className="row container-display",
                                    ),
                                ],   
                            )   
                        ],
                        id="csd_aq_cont",
                        className="row container-display",
                    ),
                ],
                className="row flex-display",
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.P("Elige el campus universitario ", className="control_label"),
                            dcc.RadioItems(
                                id="campus_selector",
                                options=[
                                    {"label": "Ambos ", "value": "ambos"},
                                    {"label": "Campus Santiago ", "value": "csi"},
                                    {"label": "Campus Santo Domingo ", "value": "csd"},
                                ],
                                value="ambos",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            html.P(
                                "Medidas promedio por:",
                                className="control_label",
                            ),
                            dcc.RadioItems(
                                id="date_type_selector",
                                options=[
                                    {"label": "Mes ", "value": "M"},
                                    {"label": "Semana ", "value": "W"},
                                    {"label": "Día ", "value": "D"},
                                    {"label": "Hora ", "value": "H"},
                                ],
                                value="D",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            html.P(
                                "Rango de fecha:",
                                className="control_label",
                            ),
                            dcc.DatePickerRange(
                                id="time_range",
                                display_format="DD/MMM/YYYY ",
                                min_date_allowed=dt.datetime(2020, 5, 7),
                                day_size=50,
                                start_date_placeholder_text="Fecha de Inicio",
                                end_date_placeholder_text="Fecha Final",
                                start_date=(dt.datetime.today() - dt.timedelta(days=15)).strftime(dpr_format),
                                end_date = dt.datetime.today().strftime(dpr_format),
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                            [dcc.Graph(id="aq_info_table")],
                            className="pretty_container eight columns",
                        ),
                
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="aq_graph")],
                        className="pretty_container twelve columns",
                    ),
                    
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="pm1_graph")],
                        className="pretty_container four columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="pm25_graph")],
                        className="pretty_container four columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="pm10_graph")],
                        className="pretty_container four columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="co_graph")],
                        className="pretty_container six columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="no2_graph")],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="o3_graph")],
                        className="pretty_container six columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="so2_graph")],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.A("Puedes descargar nuestros datos de forma abierta y en el formato que deseas.", href="http://smartcampus.pucmm.edu.do/datosabiertos"),
            html.A("Para más información, ver nuestra sección de documentación.", href="http://smartcampus.pucmm.edu.do/documentacion"),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
        )

    #Cargar el data frame
    def load_data():
        df = pd.DataFrame.from_dict(requests.get(aq_api_url).json())
        df.loc[df['ID_Modulo'].isin([csi_modulo,csd_modulo])]           #Modulos de AQ de CSI & CSD
        df['Fecha'] = pd.to_datetime(df['Fecha'], format=date_format)
        df['Valor'] =df['Valor'].replace(to_replace=-1, value=0)
        df.loc[df['Nombre']=='Gas_NO2', 'Valor'] *=1000                 #llevamos los valores de NO2 de PPM a PPB
        df.loc[df['Nombre']=='Gas_SO2', 'Valor'] *=1000                 #llevamos los valores de SO2 de PPM a PPB
        
        return df

    #Filtro del Data Frame
    def filter_dataframe(df, campus_selector, date_type_selector, time_range_start, time_range_end):
        
        start_date=dt.datetime.combine(dt.datetime.strptime(time_range_start, dpr_format), dt.datetime.min.time())
        end_date = dt.datetime.combine(dt.datetime.strptime(time_range_end, dpr_format), dt.datetime.max.time())

        dff = df.loc[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]

        if campus_selector=="csi":
            dff = dff.loc[dff['ID_Modulo']==csi_modulo]
        elif campus_selector=="csd":
            dff = dff.loc[dff['ID_Modulo']==csd_modulo]

        dff = dff.groupby(['ID_Modulo','Nombre',pd.Grouper(key='Fecha', freq=date_type_selector)]).agg({'Valor':'mean'})
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

    #Crear AQ info table
    def create_aq_info_table(header, dataset, title=""):
        color_space = []
        table_fill_color = ["#f1f1f1"]*6
        figure = go.Figure(data=[go.Table(
            columnwidth = [100,250,150,800],
            header=dict(
                values=header, 
                align='left',
                fill_color = "#f1f1f1",
                font=dict(color='black'),
                ),
            cells=dict(
                values=[color_space,dataset.Nivel, dataset.Valores, dataset.Descripcion],
                fill=dict(color=[dataset.Color,table_fill_color]),
                align='left',
                font=dict(color='black')
                )
            )
        ])
        figure.update_layout(
            title_text=title,
            margin=dict(l=10, r=10, b=5),
            paper_bgcolor="#f1f1f1",
            font=dict(color='black')
        )
        
        return figure

    #Colocar en el dash los ultimos valores tomados
    def texto_ultimo_valores(data):
        info = {}
        info["presion"] = '{:,.4f}'.format(float(data.loc['Presion']["Valor"])).rstrip('0').rstrip('.') + '  Pa'
        info["humedad"] = '{:,.2f}'.format(float(data.loc['Humedad']["Valor"])).rstrip('0').rstrip('.') + '  %'
        info["pm1"] = '{:,.4f}'.format(float(data.loc['PM1']["Valor"])).rstrip('0').rstrip('.') + '  µg/\u33A5'
        info["pm25"] = '{:,.4f}'.format(float(data.loc['PM25']["Valor"])).rstrip('0').rstrip('.') + '  µg/\u33A5'
        info["pm10"] = '{:,.4f}'.format(float(data.loc['PM10']["Valor"])).rstrip('0').rstrip('.') + '  µg/\u33A5'
        info["o3"] = '{:,.4f}'.format(float(data.loc['Gas_O3']["Valor"])).rstrip('0').rstrip('.') + ' ppm'
        info["co"] = '{:,.4f}'.format(float(data.loc['Gas_CO']["Valor"])).rstrip('0').rstrip('.') + ' ppm'
        info["no2"] = '{:,.4f}'.format(float(data.loc['Gas_NO2']["Valor"])).rstrip('0').rstrip('.') + ' ppb'
        info["so2"] = '{:,.4f}'.format(float(data.loc['Gas_SO2']["Valor"])).rstrip('0').rstrip('.') + ' ppb'
        info["temp"] = '{:,.4f}'.format(float(data.loc['Temp']["Valor"])).rstrip('0').rstrip('.') + ' ˚C'

        return info

    #Crear las graficas de los contaminantes
    def graficar_contaminantes(df, contaminante, campus_selector):
        
        layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=25, r=25, b=20, t=40),
            hovermode="closest",
            plot_bgcolor="#F1F1F1",
            paper_bgcolor="#F1F1F1",
            legend=dict(font=dict(size=10), orientation="h"),
            title=contaminante,
            yaxis=dict(
                rangemode='nonnegative'
            )
        )
        
        data = []
        if campus_selector=="ambos":
            df_csi=df.loc[df['ID_Modulo']==csi_modulo]
            df_csd=df.loc[df['ID_Modulo']==csd_modulo]
            data =[
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name="Campus Santiago",
                    x=df_csi['Fecha'],
                    y=df_csi['Valor'],
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                ),
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name="Campus Santo Domingo",
                    x=df_csd['Fecha'],
                    y=df_csd['Valor'],
                    line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                ),
            ]
        else:
            color= "#F9ADA0" if campus_selector=="csi" else "#59C3C3"
            data =[
                dict(
                    type="scatter",
                    mode="lines+markers",
                    x=df['Fecha'],
                    y=df['Valor'],
                    line=dict(shape="spline", smoothing="2", color=color),
                ),
            ]        

        figure = dict(data=data, layout=layout)
        
        return figure

    #Crear las grafica del indice de calidad del aire
    def graficar_aqi(df, campus_selector):

        layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=25, r=25, b=20, t=40),
            hovermode="closest",
            plot_bgcolor="#F1F1F1",
            paper_bgcolor="#F1F1F1",
            legend=dict(font=dict(size=10), orientation="h"),
            title="Índice de calidad del aire",
            yaxis=dict(
                rangemode='nonnegative'
                #rangemode='tozero'
            )
        )

        dates = pd.to_datetime(df['Fecha'].unique(), format=date_format)
        data = []
        
        if campus_selector=="ambos":
            df_csi=df.loc[df['ID_Modulo']==csi_modulo]
            df_csd=df.loc[df['ID_Modulo']==csd_modulo]
            
            aqi_csi_values = []
            aqi_csd_values = []
            for date in dates:
                dff_csi = df_csi.loc[df_csi['Fecha']==date]
                dff_csi.set_index('Nombre', inplace=True)
                aqi_csi_values.append(int(calculate_aqi(dff_csi)))
                dff_csd = df_csd.loc[df_csd['Fecha']==date]
                dff_csd.set_index('Nombre', inplace=True)
                aqi_csd_values.append(int(calculate_aqi(dff_csd)))

            data =[
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name="Campus Santiago",
                    x=dates,
                    y=aqi_csi_values,
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                ),
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name="Campus Santo Domingo",
                    x=dates,
                    y=aqi_csd_values,
                    line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                ),
            ]
        else:
            aqi_values = []
            for date in dates:
                dff = df.loc[df['Fecha']==date]
                dff.set_index('Nombre', inplace=True)
                aqi_values.append(int(calculate_aqi(dff)))

            color= "#F9ADA0" if campus_selector=="csi" else "#59C3C3"
            data =[
                dict(
                    type="scatter",
                    mode="lines+markers",
                    x=dates,
                    y=aqi_values,
                    line=dict(shape="spline", smoothing="2", color=color),
                ),
            ]      

        figure = dict(data=data, layout=layout)
        
        return figure


    #Callbacks section

    #Tabla de información del indice de calidad
    @app.callback(
        Output("aq_info_table",'figure'),
        [Input("campus_selector", "value")],
        )
    def update_aq_info_table(data):
        dataset = pd.read_csv(DATA_PATH.joinpath("aqtable.csv"))
        header = ["Color","Nivel","Valores","Descripción"]
        title = "Tabla de referencia del Índice de Calidad del Aire"
        return create_aq_info_table(header, dataset, title)

    #Contaminantes actuales en ambos campus
    @app.callback(
        [
            #Output("csi_pm25_text", "children"),
            #Output("csi_pm10_text", "children"),
            #Output("csi_pm1_text", "children"),
            #Output("csi_co_text", "children"),
            #Output("csi_no2_text", "children"),
            #Output("csi_o3_text", "children"),
            #Output("csi_so2_text", "children"),
            #Output("csi_temp_text", "children"),
            #Output("csi_hum_text", "children"),
            #Output("csi_pres_text", "children"),
            Output("csd_pm25_text", "children"),
            Output("csd_pm10_text", "children"),
            Output("csd_pm1_text", "children"),
            Output("csd_co_text", "children"),
            Output("csd_no2_text", "children"),
            Output("csd_o3_text", "children"),
            Output("csd_so2_text", "children"),
            Output("csd_temp_text", "children"),
            Output("csd_hum_text", "children"),
            Output("csd_pres_text", "children"),
            Output("fecha_actualizado_text", "children"),
            #Output("csi_aq_gauge", "value"),
            Output("csd_aq_gauge", "value"),
        ],
        [Input("campus_selector", "value")],
        )
    def update_app_text(campus_selector):

        df = load_data()

        dff = df.loc[df['Fecha']==df['Fecha'].max()]    #ultimas medidas
        df_csi = dff.loc[df['ID_Modulo']==csi_modulo]             #modulo AQ_CSI
        df_csi.set_index('Nombre', inplace=True)
        df_csd = dff.loc[df['ID_Modulo']==csd_modulo]             #modulo AQ_CSD
        df_csd.set_index('Nombre', inplace=True)

        actualizado = "Última actualización: {}".format(df['Fecha'].max().strftime('%d/%m/%y, %H:%M:%S'))
        info_csi = texto_ultimo_valores(df_csi)
        info_csd = texto_ultimo_valores(df_csd)
        
        aqi_csi = int(calculate_aqi(df_csi))
        aqi_csd = int(calculate_aqi(df_csd))

        results = [
            #info_csi['pm25'], 
            #info_csi['pm10'], 
            #info_csi['pm1'], 
            #info_csi['co'], 
            #info_csi['no2'], 
            #info_csi['o3'], 
            #info_csi['so2'], 
            #info_csi['temp'], 
            #info_csi['humedad'], 
            #info_csi['presion'],
            info_csd['pm25'], 
            info_csd['pm10'], 
            info_csd['pm1'], 
            info_csd['co'], 
            info_csd['no2'], 
            info_csd['o3'], 
            info_csd['so2'], 
            info_csd['temp'], 
            info_csd['humedad'], 
            info_csd['presion'],
            actualizado,
            #aqi_csi,
            aqi_csd,
        ]

        return results

    # Selectors -> AQI graph
    @app.callback(
        Output("aq_graph", "figure"),
        [
            Input("campus_selector", "value"),
            Input("date_type_selector", "value"),
            Input("time_range", "start_date"),
            Input("time_range", "end_date"),
        ],
        )
    def make_aqi_figure(campus_selector, date_type_selector, time_range_start, time_range_end):
        df = filter_dataframe(load_data(), campus_selector, date_type_selector, time_range_start, time_range_end)
        
        return graficar_aqi(df, campus_selector)

    # Selectors -> Graficas contaminantes
    @app.callback(
        [
            Output("pm1_graph", "figure"),
            Output("pm25_graph", "figure"),
            Output("pm10_graph", "figure"),
            Output("co_graph", "figure"),
            Output("no2_graph", "figure"),
            Output("o3_graph", "figure"),
            Output("so2_graph", "figure"),
        ],
        [
            Input("campus_selector", "value"),
            Input("date_type_selector", "value"),
            Input("time_range", "start_date"),
            Input("time_range", "end_date")
        ],
        )
    def hacer_figuras_contaminantes(campus_selector, date_type_selector, time_range_start, time_range_end):
        codigo_contaminantes = ['PM1', 'PM25', 'PM10','Gas_CO','Gas_NO2','Gas_O3','Gas_SO2']
        nombre_contaminantes = ['Particulado PM1 (µg/\u33A5)', 'Particulado PM25 (µg/\u33A5)', 'Particulado PM10 (µg/\u33A5)','Monóxido de Carbono - CO (PPM)','Dióxido de Nitrógeno - NO₂ (PPB)','Ozono - O₃ (PPM)','Dióxido de Azufre - SO₂ (PPB)']
        df = filter_dataframe(load_data(), campus_selector, date_type_selector, time_range_start, time_range_end)

        result = []

        for codigo, nombre in zip(codigo_contaminantes,nombre_contaminantes):
            result.append(graficar_contaminantes(df.loc[df['Nombre']==codigo], nombre, campus_selector))

        return result

    #Selectors -> time range
    @app.callback(
        [
            Output("time_range", "start_date"),
            Output("time_range", "end_date"),
        ],
        [
            Input("date_type_selector", "value"),
        ],
        )
    def default_time_range_by_date_type(date_type):
        if date_type == "H":
            return dt.datetime.today().strftime(dpr_format), dt.datetime.today().strftime(dpr_format)
        elif date_type == "D":
            return (dt.datetime.today() - dt.timedelta(days=15)).strftime(dpr_format), dt.datetime.today().strftime(dpr_format)
        elif date_type == "W":
            return (dt.datetime.today() - dt.timedelta(weeks=15)).strftime(dpr_format), dt.datetime.today().strftime(dpr_format)

        return "2020-05-07", dt.datetime.today().strftime(dpr_format)

    return app.server
