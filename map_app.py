from dash import html, dcc, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import models
import os
import utils
import dash_leaflet as dl
from sqlalchemy import func

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
                                 id="prod-select",
                                 options=[{'label': i[1], 'value': i[0]}
                                          for i in product_values],
                                 placeholder='Select Product...',
                                 className='map-input'
                             ),
                         ], sm=12)
                     ], className='g-1')
                 ])
    ])
], className='map-form')





mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"

quantity_map = dcc.Loading(
    id='loader',
    children=[html.Div(
        children=[
            dl.Map(id='quantity-map',
                   center=[37.95, -79.25],
                   zoom=8.3,
                   children=[
                       dl.TileLayer(url=mapbox_url.format(
                           id="light-v9", access_token=mapbox_access_token)
                       ),
                       dl.LocateControl(options={'locateOptions': {
                           'enableHighAccuracy': True}}),
                       dl.LayerGroup(id="icon_layer")
                   ]
                   )
        ], style={'position': 'absolute', 'top': '61px', 'height': '93vh', 'width': '100%'}
    )
    ], fullscreen=True)

layout = html.Div([
    dcc.Store(id='map_app_store', storage_type='session'),
    dbc.Row([
        dbc.Col([form], sm=10, lg=4),
        dbc.Col([quantity_map], style={'zIndex': 0, 'padding': 0}, lg=12),
        dbc.Row([
            dbc.Col(html.H1(id='error_msg', children='Please select a product'), width=12, style={'textAlign': 'center'})
            ], justify="center", className="position-absolute top-50")
    ])
])




@app.callback(
    Output('map_app_store', 'data'),
    [Input('url', 'pathname')]
)
def load_data(path):
    map_q = models.session.query(
                    models.Bourbon.longitude, 
                    models.Bourbon.latitude, 
                    models.Bourbon.productid,
                    func.Concat(models.Bourbon_stores.store_addr_2, ' ', models.Bourbon_stores.store_city).label('store_addr_disp'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
               .join(models.Bourbon_stores) \
               .group_by(models.Bourbon.productid, models.Bourbon_stores.store_addr_2) \
               .filter(
                   models.Bourbon.insert_dt == utils.get_run_dt(),
                   
                )

    df = pd.read_sql(map_q.statement, models.session.bind, columns=['latitude, longitude, store_addr_disp', 'quantity'])
    models.session.close()

    return df.to_dict('records')


@app.callback(
    [Output('icon_layer', 'children'),
    Output('error_msg', 'children')],
    [Input('map_app_store', 'data'),
     Input('prod-select', 'value')]
)
def update_map_page(store, input_product):

    if input_product is None:
        raise PreventUpdate

    map = []
    
    fltred_store = [x for x in store if x['productid'] == input_product]

    map = [dl.Marker(position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip([
                    html.Div(f'Address: {row["store_addr_disp"]}'),
                    html.Div(f'Quantity: {int(row["quantity"])}')
                ])
            ]) for row in fltred_store]

    if len(map):
        return [map, '']
    else:
        return [map, 'No Data Found']
