import dash
from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import pandas as pd
import models
import os
import utils
import dash_leaflet as dl
from sqlalchemy import func

dash.register_page(__name__, path='/map', title='Map')

cwd_path = os.path.dirname(__file__)
mapbox_access_token = open(os.path.join(os.path.split(
    os.path.dirname(__file__))[0], 'mapbox_token')).read()

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
models.session.close()

product_values = [(k, v) for k, v in zip(
    df_products['productid'], df_products['description'])]


#form controls
map_form = dmc.Select(
    id="map-prod-select",
    data=[{'label': i[1], 'value': i[0]}
          for i in product_values],
    placeholder='Select Products...',
    className="control",
    radius="md",
    style={"zIndex": 1},
    icon=[html.I(className='fas fa-magnifying-glass')]
)

mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"

quantity_map = dl.Map(id='quantity-map',
                      center=[37.95, -79.25],
                      zoom=7.5,
                      children=[
                          dl.TileLayer(url=mapbox_url.format(
                              id="light-v9", access_token=mapbox_access_token)
                          ),
                          dl.LocateControl(options={'locateOptions': {
                              'enableHighAccuracy': True}}),
                          dl.LayerGroup(id="icon_layer")
                      ], style={'height': '700px', 'zIndex': 0})


layout = html.Div(
    children=[
        dmc.Grid([
            dcc.Store(id='map_app_store', storage_type='session'),
            dmc.Col([map_form], sm=12, lg=4),
            dmc.Col([
                    dmc.Center(
                        children=[
                            dmc.Title(id='error_msg',
                                      children='Select a product', order=2)
                        ])], sm=4, lg=4),
            dmc.Col([quantity_map], lg=12)
        ])
    ])


@callback(
    Output('map_app_store', 'data'),
    [Input('url', 'pathname')]
)
def load_data(path):
    map_q = models.session.query(
        models.Bourbon.longitude,
        models.Bourbon.latitude,
        models.Bourbon.productid,
        func.Concat(models.Bourbon_stores.store_addr_2, ' ',
                    models.Bourbon_stores.store_city).label('store_addr_disp'),
        func.sum(models.Bourbon.quantity).label('quantity')
    ) \
        .join(models.Bourbon_stores) \
        .group_by(models.Bourbon.productid, models.Bourbon_stores.store_addr_2) \
        .filter(
        models.Bourbon.insert_dt == utils.get_run_dt(),

    )

    df = pd.read_sql(map_q.statement, models.session.bind, columns=[
                     'latitude, longitude, store_addr_disp', 'quantity'])
    models.session.close()

    return df.to_dict('records')


@callback(
    [Output('icon_layer', 'children'),
     Output('error_msg', 'children')],
    [Input('map_app_store', 'data'),
     Input('map-prod-select', 'value')]
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
