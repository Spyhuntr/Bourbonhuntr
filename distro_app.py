
from dash import html, dcc, Input, Output, State, callback_context
import dash
from dash.dcc.Loading import Loading
from dash.dependencies import ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Col import Col
import pandas as pd
import models
import os
import dash_leaflet as dl
from sqlalchemy import cast, Date, func
import datetime as dt
import time

from app import app

cwd_path = os.path.dirname(__file__)
mapbox_access_token = open(os.path.join(cwd_path, 'mapbox_token')).read()

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
models.session.close()

product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

#form controls
form = dbc.Card([
    dbc.CardBody([
        html.Div(id='form-cntrl-div',
                 children=[
                     dbc.Row([
                         dbc.Col([
                             dcc.Dropdown(
                                 id="distro-prod-select",
                                 options=[{'label': i[1], 'value': i[0]}
                                          for i in product_values],
                                 placeholder='Select Product...',
                                 className='map-input'
                             ),
                         ], sm=12),
                         dbc.Col([
                             html.Div(id='slider_container'),
                             html.H5(id='date_text', className='mt-3')
                         ], sm=12, className='mt-3')
                     ], className='g-1')
                 ]),
        dcc.Loading(id="loading01",
                children=html.Div(id="loading-output1")
                    )
    ])
], className='distro-map-form')

mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"

distro_map = html.Div(
    children=[
        dl.Map(center=[37.95, -79.25],
               zoom=8.3,
               children=[
                    dl.TileLayer(url=mapbox_url.format(
                        id="light-v9", access_token=mapbox_access_token)
                    ),
                    dl.LocateControl(options={'locateOptions': {'enableHighAccuracy': True}}),
                    dl.LayerGroup(id="distro_icon_layer")
                ]
        )
    ], className='distro-map'
)

layout = html.Div([
    dcc.Store(id='map_distro_store', storage_type='memory'),
    dbc.Row([
        dbc.Col([form], sm=6, lg=4),
        dbc.Col([distro_map], style={'zIndex': 0, 'padding': 0}, lg=12),
        dbc.Row([
            dbc.Col(
                html.H1(id='distro_error_msg', 
                    children='Please select a product'), 
                width=12, 
                style={'textAlign': 'center'})
            ], justify="center", className="position-absolute top-50"),
    ])
])


@app.callback(
    [Output('map_distro_store', 'data'),
     Output("loading-output1", "children")],
    [Input('url', 'pathname'),
    Input('distro-prod-select', 'value')],
    State('map_distro_store', 'data')
)
def load_distro_data(path, input_product, store_state):

    if input_product is None:
        raise PreventUpdate

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
                ) \
                .order_by(models.Bourbon.insert_date)

    df = pd.read_sql(map_q.statement, models.session.bind)
    models.session.close()

    return [df.to_dict('records'), '']


@app.callback(
    Output('date_text', 'children'),
    Input({"type": 'date_slider', "index": ALL}, 'value'),
    prevent_initial_call=True
)
def get_slider_value(slider_value):

    if len(slider_value) == 0:
        raise PreventUpdate

    frmt_date = dt.datetime.fromtimestamp(slider_value[0]).strftime('%m/%d/%Y')
    return f"Date: {frmt_date}"


@app.callback(
    [Output('slider_container', 'children'),
     Output('distro_error_msg', 'children')],
    [Input('map_distro_store', 'data'),
     Input('distro-prod-select', 'value')],
     prevent_initial_call=True
)
def build_slider(store, product):

    if len(store) == 0:
        return [dcc.Slider(), 'No Data Found']

    dates = sorted(set([dt.datetime.strptime(row['date'], '%Y-%m-%d').date() for row in store]))

    def unixTimeMillis(dt):
        ''' Convert datetime to unix timestamp '''
        return int(time.mktime(dt.timetuple()))

    marks = {unixTimeMillis(date): {} for date in dates}

    slider = dcc.Slider(
        id={'type': 'date_slider', 'index': 1},
        min=unixTimeMillis(min(dates)),
        max=unixTimeMillis(max(dates)),
        value=unixTimeMillis(min(dates)),
        marks=marks,
        step=None,
        included=False,
        updatemode='drag'
    )

    return [slider, '']


@app.callback(
    Output('distro_icon_layer', 'children'),
    [Input('map_distro_store', 'data'),
     Input({"type": 'date_slider', "index": ALL}, 'value')],
     prevent_initial_call=True
)
def update_distro_map_page(store, date):

    map_icons = []

    if len(date) == 0:
        raise PreventUpdate

    frmt_date = dt.datetime.fromtimestamp(date[0]).strftime('%Y-%m-%d')
    
    fltred_store = [x for x in store if x['date'] == frmt_date]

    map_icons = [dl.Marker(position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip([
                    html.Div(f'Address: {row["store_addr_disp"]}'),
                    html.Div(f'Quantity: {int(row["quantity"])}')
                ])
            ]) for row in fltred_store]

    return map_icons

        
        
