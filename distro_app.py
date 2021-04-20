
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import models
import datetime as dt
import plotly.express as px
import os
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
            ], form=True, className='mb-2')
        ])

distro_map = html.Div(
    dcc.Loading(
        id='loading-1',
        children=dcc.Graph(
            id='distro-map', style={'height':'85vh'}
        )
    )
)

layout = html.Div([
    dbc.Row([
        dbc.Col([form], sm=12, lg=12),
        dbc.Col([distro_map], lg=12)
    ])
])



@app.callback(
    Output(component_id='distro-map', component_property='figure'),
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='prod-select', component_property='value')]
)
def update_map_page(path, input_product):

    map_q = models.session.query(
                    models.Bourbon.longitude, 
                    models.Bourbon.latitude, 
                    func.Concat(models.Bourbon_stores.store_addr_2, ' ', models.Bourbon_stores.store_city).label('store_addr_disp'),
                    cast(models.Bourbon.insert_date, Date).label('date'),
                    models.Bourbon.quantity
                ) \
               .join(models.Bourbon_stores) \
               .filter(
                    cast(models.Bourbon.insert_date, Date) >= '2020-03-01',
                    models.Bourbon.productid == input_product
                )

    if not input_product:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "Please select a product",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }

    df = pd.read_sql(map_q.statement, models.session.bind)
    
    if df.empty:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }


    models.session.close()

    px.set_mapbox_access_token(mapbox_access_token)

    map_fig = px.scatter_mapbox(
        df, 
        lat='latitude',
        lon='longitude', 
        animation_frame=df['date'].astype(str),
        hover_name='store_addr_disp',
        size='quantity'
    )
   

    map_fig.update_layout(
        autosize=True, 
        hovermode='closest',
        margin = {
            'l':0,'r':0,'t':0,'b':0
        },
        mapbox = {
            'style': 'light',
            'center': {
                'lat': 37.95,
                'lon': -79.25
            },
            'zoom': 6.8
        },
        hoverlabel={
            'bgcolor':'white',
            'font_size':16,
            'font_family':'Lato'
        }
    )

    return map_fig