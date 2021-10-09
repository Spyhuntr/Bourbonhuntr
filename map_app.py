
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import models
import plotly.graph_objs as go
import os
import utils
from sqlalchemy import cast, Date, func

from app import app

cwd_path = os.path.dirname(__file__)
mapbox_access_token = open(os.path.join(cwd_path, 'mapbox_token')).read()

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
models.session.close()

product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

#form controls
form = html.Div(id='form-cntrl-div', 
            children = [
                dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="prod-select",
                        options=[{'label': i[1], 'value': i[0]} for i in product_values],
                        placeholder='Select Products...'
                    )
                ], lg=4)
            ], className='mb-2')
        ])

quantity_map = html.Div(
    id='map-div',
    children=[ 
        dcc.Graph(
            id='quantity-map', style={'height':'87vh'}
        )
    ]
)

layout = html.Div([
    dbc.Row([
        dbc.Col([form], sm=12, lg=12),
        dbc.Col([quantity_map], lg=12)
    ])
])



@app.callback(
    Output(component_id='quantity-map', component_property='figure'),
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='prod-select', component_property='value')]
)
def update_map_page(path, input_product):

    map_q = models.session.query(
                    models.Bourbon.longitude, 
                    models.Bourbon.latitude, 
                    func.Concat(models.Bourbon_stores.store_addr_2, ' ', models.Bourbon_stores.store_city).label('store_addr_disp')
                ) \
               .join(models.Bourbon_stores) \
               .filter(
                   cast(models.Bourbon.insert_dt, Date) == utils.get_run_dt(),
                   
                )

    if input_product:
        map_q = map_q.filter(models.Bourbon.productid == input_product)

    df = pd.read_sql(map_q.statement, models.session.bind)
    models.session.close()

    map_fig = go.Figure(go.Scattermapbox(
        lat=df['latitude'], 
        lon=df['longitude'],
        mode='markers',
        text=df['store_addr_disp'],
        marker={
            'size': 15
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
            'font_size':16,
            'font_family':'Lato'
        })

    return map_fig