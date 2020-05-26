import dash
import dash_core_components as dcc 
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd 

def covid_dash(server, route):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    #external_stylesheets = ['static/css/style.css']

    tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}
    #tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Nunito"}

    app = dash.Dash(__name__, server=server, routes_pathname_prefix=route, external_stylesheets=external_stylesheets)


    urlConfirmados = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiYAUKeNkVp9_6T9tKGAeqoR9YuV2EoZ_0mUoL23seiP5uV3pTpfrY9mu2rpdeOiG0AbcmqKbihAeE/pub?gid=0&single=true&output=csv'
    urlRecuperados = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiYAUKeNkVp9_6T9tKGAeqoR9YuV2EoZ_0mUoL23seiP5uV3pTpfrY9mu2rpdeOiG0AbcmqKbihAeE/pub?gid=697307037&single=true&output=csv'
    urlMuertes = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiYAUKeNkVp9_6T9tKGAeqoR9YuV2EoZ_0mUoL23seiP5uV3pTpfrY9mu2rpdeOiG0AbcmqKbihAeE/pub?gid=759112386&single=true&output=csv'
    urlCoordenadas = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiYAUKeNkVp9_6T9tKGAeqoR9YuV2EoZ_0mUoL23seiP5uV3pTpfrY9mu2rpdeOiG0AbcmqKbihAeE/pub?gid=1956896185&single=true&output=csv'


    def loadData(url, columnName):
        data = pd.read_csv(url) \
            .melt(id_vars=['Provincia'], var_name='date', value_name=columnName)
        data['date'] = data['date'].astype('datetime64[ns]')
        return data

    def getLastData():
        allData = loadData(urlConfirmados, "CumConfirmados") \
            .merge(loadData(urlRecuperados, "CumRecuperados")) \
            .merge(loadData(urlMuertes, "CumMuertes"))
        return allData

    def nonreactive_data(provincia):
        allData = getLastData()
        if provincia == '<all>':
            data = allData.drop('Provincia', axis=1).groupby("date").sum().reset_index()
        else:
            data = allData.loc[allData['Provincia'] == provincia]
        newCases = data.select_dtypes(include='int64').diff().fillna(0)
        newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
        data = data.join(newCases)
        data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
        return data

    gisData = pd.read_csv(urlCoordenadas)
    
    provincias = getLastData()['Provincia'].unique()
    lastDate = getLastData()['date'].max()

    total = nonreactive_data("<all>")
    lastValue = total.loc[total["date"]==lastDate]
    casosActivos = (int(lastValue["CumConfirmados"])-int(lastValue["CumRecuperados"])-int(lastValue["CumMuertes"]))
    

    app.layout = html.Div(
        style={ 'font-family':"Courier New, monospace" },
        children=[
            html.Header(title='Covid-19 en República Dominicana'),
            html.H1('Casos de Coronavirus (COVID-19) en la República Dominicana'),
            html.H2("Al {} tenemos un total de {} casos confirmados en el país".format(lastDate.strftime('%d de %b, %Y'), int(lastValue["CumConfirmados"]))),
            html.H3('¿Qué quieres ver?'),
            dcc.Graph(
                        id="status_rd",
                        config={ 'displayModeBar': False }
                    ),
            dcc.Checklist(
                id='metrics_rd',
                options=[{'label':m, 'value':m} for m in ['Confirmados', 'Muertes', 'Recuperados']],
                value=['Confirmados', 'Muertes']
            ),
            html.Div(className="row", children=[
                html.Div(className="six columns", children=[
                    dcc.Graph(
                        id="plot_cum_metrics_rd",
                        config={ 'displayModeBar': False }
                    )
                ]),
                html.Div(className="six columns", children=[
                    dcc.Graph(
                        id="plot_new_metrics_rd",
                        config={ 'displayModeBar': False },
                    )
                ])
            ]),
            dcc.Graph(
                        id="interactive_map_rd",
                        config={ 'displayModeBar': False }
                    ),
            html.H3('Por provincias'),
            html.Div(className="row", children=[
                html.Div(className="six columns", children=[
                    html.H5('Provincias'),
                    dcc.Dropdown(
                        id='provincias',
                        options=[{'label':p, 'value':p} for p in provincias],
                        value='Distrito Nacional'
                    )
                ]),
                html.Div(className="four columns", children=[
                    html.H5('Ver el numero de:'),
                    dcc.Checklist(
                        id='metrics_prov',
                        options=[{'label':m, 'value':m} for m in ['Confirmados', 'Muertes']],
                        value=['Confirmados', 'Muertes']
                    )
                ])
            ]),
            html.Div(className="row", children=[
                html.Div(className="six columns", children=[
                    dcc.Graph(
                        id="plot_cum_metrics_prov",
                        config={ 'displayModeBar': False }
                    )
                ]),
                html.Div(className="six columns", children=[
                    dcc.Graph(
                        id="plot_new_metrics_prov",
                        config={ 'displayModeBar': False },
                    )
                ])
            ]),
            html.Div(
                children=[
                    html.A('Fuente: Boletín especial Covid-19 del Ministerio de Salud Publica', href="https://www.msp.gob.do/web/?page_id=6682", target="_blank"),
                    html.P('Desarrollado por Víctor González',className='mb-4')
            ])
    ])

    def barchart(data, metrics, prefix="", yaxisTitle=""):
        figure = go.Figure(data=[
            go.Bar( 
                name=metric, x=data.date, y=data[prefix + metric],
                marker_line_color='rgb(0,0,0)', marker_line_width=1,
                marker_color={ 'Muertes':'rgb(200,30,30)', 'Recuperados':'rgb(30,200,30)', 'Confirmados':'rgb(100,140,240)'}[metric]
            ) for metric in metrics
        ])
        figure.update_layout( 
                barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
                plot_bgcolor='#FFFFFF', font=tickFont) \
            .update_xaxes( 
                title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
                tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
            .update_yaxes(
                title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
        return figure

    def linechart(data, metrics, prefix="", yaxisTitle=""):
        figure = go.Figure(data=[
            go.Scatter( 
                name=metric, x=data.date, y=data[prefix + metric],
                marker_line_color='rgb(0,0,0)', marker_line_width=1,
                marker_color={ 'Muertes':'rgb(200,30,30)', 'Recuperados':'rgb(30,200,30)', 'Confirmados':'rgb(100,140,240)'}[metric]
            ) for metric in metrics
        ])
        figure.update_layout( 
                barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
                plot_bgcolor='#FFFFFF', font=tickFont) \
            .update_xaxes( 
                title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
                tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
            .update_yaxes(
                title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
        return figure

    def mapchart(data):
        figure = go.Figure()
        figure.add_trace(go.Scattergeo(
            lon = gisData['Lon'],
            lat = gisData['Lat'],
            text= gisData['total'],
            name= 'Acumulado',
            marker= dict(
                size = gisData['total'],
                color = 'rgb(107,174,214)',
                line_width = 0.5)
        ))
        figure.update_layout(
            title = go.layout.Title(
                text = 'Mapa actualizado del Covid-19 en RD'),
            geo = go.layout.Geo(
                resolution = 50,
                scope = 'south america',
                showframe = True,
                showcoastlines = True,
                landcolor = "rgb(229, 229, 229)",
                countrycolor = "black" ,
                coastlinecolor = "black",
                projection_type = 'mercator',
                lonaxis_range= [ -72.0, -68.0 ],
                lataxis_range= [ 17.4, 20.0],
                domain = dict(x = [ 0, 1 ], y = [ 0, 1 ])
            ))
        return figure
    
    def suburstchart(data):
        figure = go.Figure(go.Sunburst(
            labels = ["Activos", "Recuperados", "Muertes"],
            parents = ["Confirmados","Confirmados","Confirmados"],
            values = [(int(lastValue["CumConfirmados"])-int(lastValue["CumRecuperados"])-int(lastValue["CumMuertes"])), int(lastValue["CumRecuperados"]), int(lastValue["CumMuertes"])]
        ))
        figure.update_layout(margin = dict(t=0, l=0, r=0, b=0))
        return figure

    @app.callback(
        Output('status_rd', 'figure'), 
        [Input('metrics_rd', 'value')]
    )
    def update_status_rd(metrics):
        data = lastValue
        return suburstchart(data)

    @app.callback(
        Output('plot_new_metrics_rd', 'figure'), 
        [Input('metrics_rd', 'value')]
    )
    def update_plot_new_metrics_rd(metrics):
        data = nonreactive_data('<all>')
        return barchart(data, metrics, prefix="New", yaxisTitle="Nuevos casos por día en la República Dominicana")

    @app.callback(
        Output('plot_cum_metrics_rd', 'figure'), 
        [Input('metrics_rd', 'value')]
    )
    def update_plot_cum_metrics_rd(metrics):
        data = nonreactive_data('<all>')
        return linechart(data, metrics, prefix="Cum", yaxisTitle="Casos acumulados en la República Dominicana")

    @app.callback(
        Output('interactive_map_rd', 'figure'), 
        [Input('metrics_rd', 'value')]
    )
    def update_interactive_map_rd(metrics):
        data = nonreactive_data('<all>')
        return mapchart(data)

    @app.callback(
        Output('plot_new_metrics_prov', 'figure'), 
        [Input('provincias', 'value'), Input('metrics_prov', 'value')]
    )
    def update_plot_new_metrics_prov(provincias, metrics):
        data = nonreactive_data(provincias)
        return barchart(data, metrics, prefix="New", yaxisTitle="Casos nuevos por día en: "+provincias)

    @app.callback(
        Output('plot_cum_metrics_prov', 'figure'), 
        [Input('provincias', 'value'), Input('metrics_prov', 'value')]
    )
    def update_plot_cum_metrics_prov(provincias, metrics):
        data = nonreactive_data(provincias)
        return linechart(data, metrics, prefix="Cum", yaxisTitle="Casos acumulados en: "+provincias)

    return app.server

#if __name__ == '__main__':
#    app.run_server(debug=True)