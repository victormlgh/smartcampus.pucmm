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


# get relative data folder
PATH = pathlib.Path(__file__).parent
CONFIG_PATH = PATH.joinpath("config").resolve()
api_credentials = pd.read_json(CONFIG_PATH.joinpath("api_credential.json"), typ='series')

#Data URL
aq_api_url = "https://smartcampus.pucmm.edu.do/api/v1/ambiental"

#Date format
date_format='%Y/%m/%d, %H:%M:%S'
dpr_format = '%Y-%m-%d' #Date Picker Range format

#ID_Modulos Ruido en Campus PUCMM
csi_modulo = [8,9,10]
csd_modulo = [4,5,7]

#Nombre de las localidades donde estan los sensores 
csi_location_name = ['Parqueo General', 'Postgrado', 'Arquitectura']
csd_location_name = ['Padre Alemán', 'Edificio A1', 'Edificio B1']

#Variables globales
env_var = ["Temp", "Humedad", "Presion"]
mapbox_access_token = api_credentials['mapbox']

def thp_dash(server, route):

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=route)
    app.title = 'Mapa de las condiciones climáticas - Smart Campus - Pontificia Universidad Católica Madre y Maestra'

    # App layout section
    app.layout = html.Div(
        [
            # empty Div to trigger javascript file for graph resizing
            
            html.Div(
                [
                    html.Div(
                        [
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("SmartCampusLogo.png"),
                                    id="smartcampus",
                                    style={
                                        "height": "200px",
                                        "width": "auto",
                                        "margin-bottom": "25px",
                                    },
                                ),
                                href="https://smartcampus.pucmm.edu.do/",
                            )
                            
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Panel de datos",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    html.H4(
                                        "Mapa de las condiciones climáticasido",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    
                                ]
                            )
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.A("Panel de datos", href="https://smartcampus.pucmm.edu.do/paneldatos", style={'padding': 15}),
                                    html.A("Datos abiertos", href="https://smartcampus.pucmm.edu.do/datosabiertos", style={'padding': 15}),
                                    html.A("Documentación", href="https://smartcampus.pucmm.edu.do/documentacion", style={'padding': 15}),
                                    
                                ]
                            )
                        ],
                        className="one-third column",
                        id="links",
                    ),
                ],
                id="menu",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),

            #Pestañas de condiciones actuales en ambos campus
            dcc.Tabs(
                [
                    dcc.Tab(label='Campus Santo Domingo', value='csd', children=[
                        html.Div(
                            [ 
                                html.Div(
                                    [dcc.Graph(id="csd_map")],
                                    className="pretty_container ten columns",
                                ),
                                html.Div(
                                    [dcc.Graph(id="csd_info_table")],
                                    className="pretty_container two columns",
                                ),
                            ],
                            className="row flex-display",
                        ),
                    ]),

                    dcc.Tab(label='Campus Santiago', value='csi', children=[
                        html.Div(
                            [ 
                                html.Div(
                                    [dcc.Graph(id="csi_map")],
                                    className="pretty_container ten columns",
                                ),
                                html.Div(
                                    [dcc.Graph(id="csi_info_table")],
                                    className="pretty_container two columns",
                                ),
                            ],
                            className="row flex-display",
                        ),
                    ]),
                ],
                id='campus_selector',
                value='csd',
            ),

            #Botones de selección y tabla de referencia
            html.Div(
                [
                    html.Div(
                        [
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
                        ],
                        className="pretty_container four columns",
                    ),
                    html.Div(
                        [
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
                    ),
                    html.Div(
                        [
                            html.P(
                                "Localidad Modulo:",
                                className="control_label",
                            ),
                            dcc.Dropdown(
                                id="modulo_selector",
                                searchable=False,
                                multi=True,
                                clearable=False,
                                options=[{'label':i, 'value': i} for i in csd_location_name],
                                value=csd_location_name
                            ),
                        ],
                        className="pretty_container four columns",
                    ),
                ],
                className="row flex-display",
            ),
            #Representación visual del historicos del Indice de Calidad del Aire
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="temperature_graph")],
                        className="pretty_container twelve columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="humidity_graph")],
                        className="pretty_container twelve columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="pressure_graph")],
                        className="pretty_container twelve columns",
                    ),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
        )

    #Cargar el data frame
    def load_data(url):
        df = pd.DataFrame.from_dict(requests.get(url).json())
        df = df.loc[df['Nombre'].isin(env_var)]           
        df['Fecha'] = pd.to_datetime(df['Fecha'], format=date_format)
        df['Valor'] =df['Valor'].replace(to_replace=-1, value=0)
        
        return df

    #Filtro del Data Frame
    def filter_dataframe(df, date_type_selector):

        dff = df.groupby(['ID_Modulo', 'Nombre', 'Longitud', 'Latitud',pd.Grouper(key='Fecha', freq=date_type_selector)]).agg({'Valor':'mean'})
        dff = dff.reset_index()

        return dff

    #definir color basado en nivel de temperatura
    def color_nivel_temp(valor):
        if valor < 15:
            color = '#59C3C3'
        elif int(valor) in range (15,20):
            color = '#90AD71'
        elif int(valor) in range (20,25):
            color = '#657A4E'
        elif int(valor) in range (25,30):
            color = '#F2E01D'
        elif int(valor) in range (30,35):
            color = '#FCB156'
        else:
            color = '#FC6E56'

        return color

    #Crear info table
    def create_info_table(title=""):
        figure = go.Figure(data=[go.Table(
            header=dict(
                values=[[">35 °C","30-35 °C","25-20 °C","20-25 °C","15-20 °C","<15 °C"]], 
                align='left',
                fill=dict(color=[["#FC6E56","#FCB156","#F2E01D","#657A4E","#90AD71","#59C3C3"]]),
                font=dict(color='black'),
                ),
        )
            
        ])
        figure.update_layout(
            title_text=title,
            margin=dict(l=10, r=10, b=5),
            paper_bgcolor="#f1f1f1",
            font=dict(color='black')
        )
        
        return figure
    #Crear mapa climatico
    def climate_map_graph(df, sensors, location_name, lon_campus, lat_campus):

        layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=25, r=25, b=20, t=40),
            height=600,
            hovermode="closest",
            plot_bgcolor="#F1F1F1",
            paper_bgcolor="#F1F1F1",
            legend=dict(font=dict(size=10), orientation="h"),
            title="Nivel actual de las condiciones climáticas",
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style="light",
                center=dict(lon=lon_campus, lat = lat_campus),
                zoom=15,
            ),
        )

        data = []
        for sensor, nombre in zip(sensors, location_name):
            dff = df.loc[df['ID_Modulo']==sensor]
            if not dff.empty:
                fecha = dff["Fecha"].max().strftime('%-H:%M:%S - %d/%m/%Y')
                dff = dff.loc[dff['Fecha']==dff['Fecha'].max()]
                              
                try:
                    temp = dff.loc[dff['Nombre']=='Temp']['Valor'].tolist()[0]
                except:
                    temp = 0
                try:
                    hum = dff.loc[dff['Nombre']=='Humedad']['Valor'].tolist()[0]
                except:
                    hum = 0
                try:
                    pres = dff.loc[dff['Nombre']=='Presion']['Valor'].tolist()[0]
                except:
                    pres = 0
                
                point = dict(
                    type="scattermapbox",
                    lon=dff["Longitud"],
                    lat=dff["Latitud"],
                    text="Lugar: {} <br>Temperatura: {:,.2f} °C <br>Humedad relativa: {:,.2f} % <br>Presión Atmosférica: {:,.2f} Pa <br>Hora: {}".format(nombre, temp, hum, pres, fecha),
                    name=nombre,
                    customdata=nombre,
                    marker=dict(
                        size=30, 
                        opacity=0.8,
                        color = color_nivel_temp(temp),
                    ),
                )
                data.append(point)
        
        figure = dict(data=data, layout=layout)

        return figure

    #Crear la grafica del comportamiento de las variables
    def variable_graph(df, campus_selector, modulo_selector, climate_var):
        
        layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=45, r=25, b=20, t=40),
            hovermode="closest",
            plot_bgcolor="#F1F1F1",
            paper_bgcolor="#F1F1F1",
            legend=dict(font=dict(size=10), orientation="h"),
            title="Comportamiento histórico de la "+ climate_var,
            yaxis=dict(
                rangemode='nonnegative'
            )
        )

        colors = ["#F9ADA0", "#59C3C3", "#849E68", "#DDDD1A"]
        data = []
        lista_modulo = csi_modulo + csd_modulo
        lista_location_name = csi_location_name + csd_location_name
        for modulo, color in zip(modulo_selector, colors):
            try:
                dff = df.loc[df['ID_Modulo']==lista_modulo[lista_location_name.index(modulo)]] 
                data.append(
                    dict(
                        type="scatter",
                        mode="lines+markers",
                        name=modulo,
                        x=dff['Fecha'],
                        y=dff['Valor'],
                        line=dict(shape="spline", smoothing="2", color=color),
                    ),
                )
            except:
                pass
        
        figure = dict(data=data, layout=layout)

        return figure

    #Callbacks section

    #Tabla de información del indice de calidad
    @app.callback(
        [
            Output("csd_info_table",'figure'),
            Output("csi_info_table",'figure'),
        ],
        [Input("campus_selector", "value")],
        )
    def update_info_table(data):
        table_info = create_info_table()
        return [table_info, table_info]
    
    # Selectors -> Mapa climatico del momento
    @app.callback(
        [
            Output("csi_map", "figure"),
            Output("csd_map", "figure"),
        ],
        [
            Input("date_type_selector", "value"),
            Input("time_range", "start_date"),
            Input("time_range", "end_date")
        ],
        )
    def hacer_mapa_climatica(date_type_selector, time_range_start, time_range_end):
        
        url = aq_api_url + "?inicio={}".format(dt.datetime.today().strftime(dpr_format))
        df = load_data(url)

        result = []
        result.append(climate_map_graph(df, csi_modulo, csi_location_name,  -70.683171, 19.443744))              #Campus Santiago
        result.append(climate_map_graph(df, csd_modulo, csd_location_name, -69.931026, 18.461519))              #Campus Santo Domingo

        return result

    #Selectors -> time range: set default time range based on date type
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

    #campus_selector -> Dopdown options
    @app.callback(
        [
            Output("modulo_selector", "options"),
            Output("modulo_selector", "value"),
        ],
        [
            Input("campus_selector", "value"),
        ],
        )
    def dropdown_option_by_campus(campus):
        if campus == "csd":
            options=[{'label':i, 'value': i} for i in csd_location_name]
            value = csd_location_name
        else:
            options=[{'label':i, 'value': i} for i in csi_location_name]
            value = csi_location_name

        return options, value

    #Selectors -> Climate var graph
    @app.callback(
        [
            Output("temperature_graph", "figure"),
            Output("humidity_graph", "figure"),
            Output("pressure_graph", "figure"),
        ],
        [
            Input("date_type_selector", "value"),
            Input("time_range", "start_date"),
            Input("time_range", "end_date"),
            Input("campus_selector", "value"),
            Input("modulo_selector", "value"),
        ],
        )
    def hacer_figura_clima(date_type_selector, time_range_start, time_range_end, campus_selector, modulo_selector):
        url = aq_api_url + "?inicio={}&fin={}".format(time_range_start,time_range_end)
        df = filter_dataframe(load_data(url), date_type_selector)

        titulos=["temperatura (°C)", "humedad relativa (%)", "presión atmosférica (Pa)"]
        results = []
        for var, titulo in zip(env_var,titulos):
            dff = df.loc[df['Nombre']==var]
            results.append(variable_graph(dff, campus_selector, modulo_selector, titulo))

        return results



    return app.server
