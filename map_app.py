
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import db_conn as dc
import dash_queries as dq
import datetime as dt
import plotly.graph_objs as go
import os
import utils

from app import app

cwd_path = os.path.dirname(__file__)
mapbox_access_token = open(os.path.join(cwd_path, 'mapbox_token')).read()

quantity_map = html.Div(
    id='map-div',
    children=[ 
        dcc.Graph(
            id='quantity-map', style={'height':'92vh'}
        )
    ]
)

map_info_table = html.Div(
    id='map-info-div',
    children=[]
)

layout = html.Div([
    quantity_map,
    html.Div(
    dcc.Loading(
        id='loading-1',
        type='graph',
        children=map_info_table, 
    ), id='map-menu', className="map-menu")
])



@app.callback(
    Output(component_id='quantity-map', component_property='figure'),
    Input(component_id='url', component_property='pathname')
)
def update_map_page(path):

    df = pd.read_sql(dq.map_query, dc.engine, params=([utils.get_run_dt()]))
    
    map_fig = go.Figure(go.Scattermapbox(
        lat=df['latitude'], 
        lon=df['longitude'],
        mode='markers',
        text=df['store_addr'],
        marker={
            'size': 15,
            'opacity': 0.4
        },
        hovertemplate =
            "%{text}<extra></extra>"
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




@app.callback(
    Output(component_id='map-info-div', component_property='children'),
    Input(component_id='quantity-map', component_property='clickData')
)
def update_map_tbl(store):

    df = pd.read_sql(dq.map_query, dc.engine, params=([utils.get_run_dt()]))

    storeid = ' '
    if store != None:
        store = store['points'][0]['text']
        storeid = store.split('-')

    df_table = df[['storeid','description','quantity']]
    df_table = df_table[(df_table['storeid'] == storeid[0])]
    df_table.columns = ['Store','Product', 'Quantity']

    hdr_list = []
    for hdr in df_table.columns:
        hdr_list.append(html.Th(hdr))
    
    table_header = [html.Thead(html.Tr(hdr_list))]

    tbody = []
    for data in df_table.values:
        row_data=[]
        for i in data:
            row_data.append(html.Td(i))
                
        tbody.append(html.Tr(row_data))
    table_body = [html.Tbody(tbody)]

    dash_tbl = dbc.Table(table_header + table_body, bordered=True, striped=True)

    return dash_tbl