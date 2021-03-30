import pathlib
import dash
import datetime as dt
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.graph_objects as go
import requests
import json

# -----------------------------
# load static data
# -----------------------------

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
CONFIG_PATH = PATH.joinpath("config").resolve()


provincias = pd.read_json(DATA_PATH.joinpath("provincias.json"))
municipios = pd.read_json(DATA_PATH.joinpath("municipios.json"))
sectores = pd.read_json(DATA_PATH.joinpath("sectores.json"))
sectores["sector_id"] = sectores["sector_id"].astype(str)

# -----------------------------
#       API_URL
# -----------------------------
api_url = "https://prod-precitas-api-dot-vacunatedo.ue.r.appspot.com"
authenticate_url = "/auth/login"
registros_url = "/appointment"
citas_url = "/vaccination"

# -----------------------------
#       credentials
# -----------------------------
api_credentials = pd.read_json(CONFIG_PATH.joinpath("api_credential.json"), typ='series')

authentication_msg = {"username":api_credentials['precitas-user'], "password":api_credentials["precitas-passwd"]}
header = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
response = requests.post(api_url+authenticate_url, data=json.dumps(authentication_msg), headers=header)
token = "Bearer "+response.json()['token']

# -----------------------------
# Global variables
# -----------------------------
provincias = provincias.sort_values("provincia")
mapbox_access_token = api_credentials['mapbox']


def covid_dash(server, route):

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=route)
    app.title = 'Dashboard - Registros Pre-Citas - VacúnateRD'

    app.layout = html.Div(
        [
            # empty Div to trigger javascript file for graph resizing
            # Logos y titulo del dashboard
            html.Div(
                [
                    html.Div(
                        [
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("presidencia.jpg"),
                                    style={
                                        "height": "150px",
                                        "width": "auto",
                                        "margin-bottom": "25px",
                                    },
                                ),
                                href="https://vacunate.gob.do/",
                            )
                            
                        ],
                        className="one-third column",
                        style={'textAlign': 'left'},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Panel de datos",
                                        style={
                                            "margin-bottom": "0px",
                                            "textAlign": "center"
                                        },
                                    ),
                                    html.H4(
                                        "Información de registros y citas",
                                        style={
                                            "margin-bottom": "0px",
                                            "textAlign": "center"
                                        },
                                    ),
                                    
                                ]
                            )
                        ],
                        className="one-third column",
                        style={'textAlign': 'center'},
                    ),
                    html.Div(
                        [
                            html.A(
                                html.Img(
                                    src=app.get_asset_url("vacunateRD.webp"),
                                    style={
                                        "height": "150px",
                                        "width": "auto",
                                        "margin-bottom": "25px",
                                    },
                                ),
                                href="https://vacunate.gob.do/",
                            )
                        ],
                        className="one-third column",
                        style={'textAlign': 'right'},
                    ),
                ],
                id="menu",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),

            #Pestañas de condiciones actuales
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("Personas registradas"),
                            html.H4(id="total_registros_text")
                        ],
                        className="pretty_container four columns",
                    ),
                    html.Div(
                        [
                            html.H5("Personas con citas"),
                            html.H4(id="total_citas_text")
                        ],
                        className="pretty_container four columns",
                    ),
                ],
                className="row flex-display",
            ),
            

            
            #Dorpdown de selección
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Provincia: ", className="control_label"),
                            dcc.Dropdown(
                                id='provincia_dropdown',
                                options=[{'label':name_prov, 'value':id_prov} for name_prov, id_prov in zip(provincias["provincia"], provincias["provincia_id"])],
                            )
                        ],
                        className="pretty_container six columns",
                    ),
                    html.Div(
                        [
                            html.P("Municipio:", className="control_label"),
                            dcc.Dropdown(
                                id='municipio_dropdown',
                            )
                        ],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),
            
            #total de registro
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="registro")],
                        className="pretty_container twelve columns",
                    ),
                    
                ],
                className="row flex-display",
            ),

            #total de citas
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="citas")],
                        className="pretty_container twelve columns",
                    ),
                    
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )

    # -----------------------------
    # Function section
    # -----------------------------
    def load_precitas_data():
        header = {
            "accept": "application/json",
            "Authorization": token
        }

        data = requests.get(api_url+registros_url,headers=header)
        df = pd.DataFrame.from_dict(data.json())

        url = api_url+registros_url+'?limit='+str(int(df['count'].unique()))
        data = requests.get(url,headers=header)
        df = pd.DataFrame.from_dict(data.json())

        return df

    def load_citas_data():
        header = {
            "accept": "application/json",
            "Authorization": token
        }

        data = requests.get(api_url+citas_url,headers=header)
        df = pd.DataFrame.from_dict(data.json())

        url = api_url+citas_url+'?limit='+str(int(df['count'].unique()))
        data = requests.get(url,headers=header)
        df = pd.DataFrame.from_dict(data.json())
        return df

    def create_table(header, dataset, title=""):
            
            figure = go.Figure(data=[go.Table(
                header=dict(
                    values=header, 
                    align='left',
                    fill_color = "#f1f1f1",
                    font=dict(color='black'),
                    ),
                cells=dict(
                    values=[dataset.nombre, dataset.total],
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


    # -----------------------------
    # Callbacks section
    # -----------------------------

    @app.callback(
        [Output('municipio_dropdown', 'options'),], 
        [Input('provincia_dropdown', 'value')]
    )
    def provincia_municipios(provincia_seleccionada):
        municipio = municipios.loc[municipios["provincia_id"]==provincia_seleccionada]
        municipio = municipio.sort_values("municipio")
        options_municipio=[{'label':name_mun, 'value':id_mun} for name_mun, id_mun in zip(municipio["municipio"], municipio["municipio_id"])],
        return options_municipio

    @app.callback(
        [
            Output('total_registros_text', 'children'),
            Output('registro', 'figure'),
        ], 
        [
            Input('provincia_dropdown', 'value'),
            Input('municipio_dropdown', 'value')
        ]
    )
    def create_registro_table(provincia_selec, municipio_selec):
        df = load_precitas_data()
        registro_total = str(int(df['count'].unique()))
        registro = df['rows'].apply(pd.Series)
        
        if provincia_selec is None:
            reg= registro.groupby(['ProvinceId']).agg({"Name":"count"}).reset_index()
            dataset = pd.merge(left=reg, right=provincias, left_on='ProvinceId', right_on='provincia_id', how='left')
            dataset = dataset.rename(columns={'provincia':'nombre', 'Name':'total'})
            header = ["Provincia", "Total de precitas"]
            title = "Personas con precitas por provincias"
        else:
            if municipio_selec is None:
                reg = registro.loc[registro["ProvinceId"]==provincia_selec]
                reg = reg.groupby(['MunicipalityId']).agg({"Name":"count"}).reset_index()
                dataset = pd.merge(left=reg, right=municipios, left_on='MunicipalityId', right_on='municipio_id', how='left')
                dataset = dataset.rename(columns={'municipio':'nombre', 'Name':'total'})
                header = ["Municipio", "Total de precitas"]
                title = "Personas con precitas por municipios"
            else:
                reg = registro.loc[registro["MunicipalityId"]==municipio_selec]
                reg = reg.groupby(['SectorId']).agg({"Name":"count"}).reset_index()
                reg['SectorId'] = reg['SectorId'].astype(str)
                dataset = pd.merge(left=reg, right=sectores, left_on='SectorId', right_on='sector_id', how='left')
                dataset = dataset.rename(columns={'sector':'nombre', 'Name':'total'})
                header = ["Sector", "Total de precitas"]
                title = "Personas con precitas por sector"
            
        return [registro_total, create_table(header, dataset, title)]

    @app.callback(
        [
            Output('total_citas_text', 'children'),
            Output('citas', 'figure'),
        ], 
        [
            Input('provincia_dropdown', 'value'),
            Input('municipio_dropdown', 'value')
        ]
    )   
    def create_citas_table(provincia_selec, municipio_selec):
        df = load_citas_data()
        citas_total = str(int(df['count'].unique()))
        
        dff = df['rows'].apply(pd.Series)
        citas = dff["Appointment"].apply(pd.Series)
        print(citas)
        
        if provincia_selec is None:
            reg= citas.groupby(['ProvinceId']).agg({"Name":"count"}).reset_index()
            dataset = pd.merge(left=reg, right=provincias, left_on='ProvinceId', right_on='provincia_id', how='left')
            dataset = dataset.rename(columns={'provincia':'nombre', 'Name':'total'})
            header = ["Provincia", "Total de citas"]
            title = "Personas con citas por provincias"
        else:
            if municipio_selec is None:
                reg = citas.loc[citas["ProvinceId"]==provincia_selec]
                reg = reg.groupby(['MunicipalityId']).agg({"Name":"count"}).reset_index()
                dataset = pd.merge(left=reg, right=municipios, left_on='MunicipalityId', right_on='municipio_id', how='left')
                dataset = dataset.rename(columns={'municipio':'nombre', 'Name':'total'})
                header = ["Municipio", "Total de citas"]
                title = "Personas con citas por municipios"
            else:
                reg = citas.loc[citas["MunicipalityId"]==municipio_selec]
                reg = reg.groupby(['SectorId']).agg({"Name":"count"}).reset_index()
                reg['SectorId'] = reg['SectorId'].astype(str)
                dataset = pd.merge(left=reg, right=sectores, left_on='SectorId', right_on='sector_id', how='left')
                dataset = dataset.rename(columns={'sector':'nombre', 'Name':'total'})
                header = ["Sector", "Total de citas"]
                title = "Personas con citas por sector"
            
        return [citas_total, create_table(header, dataset, title)]

    return app.server
