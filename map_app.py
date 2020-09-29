
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from db_conn import connect
import dash_queries as dq
import datetime as dt
import plotly.graph_objs as go
import os

from app import app

cwd_path = os.path.dirname(__file__)
mapbox_access_token = open(os.path.join(cwd_path, 'mapbox_token')).read()

now = dt.datetime.utcnow()

mydb = connect()

quantity_map = html.Div(
    id='map-div',
    children=[ 
        dcc.Graph(
            id='quantity-map', style={'height':'92vh'}
        )
    ]
)

layout = html.Div([
                quantity_map
            ])



@app.callback(
    Output(component_id='quantity-map', component_property='figure'),
    [Input(component_id='url', component_property='pathname')],
)
def update_page(path):

    df = pd.read_sql(dq.map_query, mydb)
    
    map_fig = go.Figure(go.Scattermapbox(
        lat=df['latitude'], 
        lon=df['longitude'], 
        mode='markers',
        marker={
            'size': 15,
            'opacity': 0.4
        },
        hovertemplate =
            "<b>%{data.points.pointNumber}</b><br><br>" +
            "longitude: %{lon}<br>" +
            "latitude: %{lat}<br>"
    ))

    map_fig.update_layout(
        autosize=True, 
        hovermode='closest',
        margin = {
            'l':0,'r':0,'t':0,'b':0
        },
        mapbox = {
            'accesstoken': mapbox_access_token,
            'style': 'light',
            'center': {
                'lat': 37.95,
                'lon': -79.25
            },
            'zoom': 7.3
        },
        hoverlabel={
            'bgcolor':'white',
            'font_size':16
        })

    return map_fig