
import dash
from dash import html, dcc, Input, Output, callback, State
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import pandas as pd
import models
import os
import dash_leaflet as dl
from sqlalchemy import func
import datetime as dt
import time

dash.register_page(__name__, path='/distro', title='Distribution')

cwd_path = os.path.dirname(__file__)

mapbox_access_token = open(os.path.join(os.path.split(
    os.path.dirname(__file__))[0], 'mapbox_token')).read()

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
models.session.close()

product_values = [(k, v) for k, v in zip(
    df_products['productid'], df_products['description'])]

# #form controls
form = dmc.Paper(
    withBorder=True,
    p="md",
    radius="md",
    children=[
        dmc.Group([
            dmc.Select(
                id="distro-prod-select",
                data=[{'label': i[1], 'value': i[0]}
                  for i in product_values],
                placeholder='Select Products...',
                className="control",
                radius="md",
                style={"zIndex": 1},
                icon=[html.I(className='fas fa-magnifying-glass')]
            ),
            html.Div(id='slider_container'),
            dmc.Title(id='date_text', order=5)], grow=True, spacing="xl"),
        dcc.Loading(id="loading01",
                    children=html.Div(id="loading-output1"), type='dot', color='orange'
                    )
    ]
)

mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"

distro_map = dl.Map(id='distro-quantity-map',
                    center=[37.95, -79.25],
                    zoom=7.4,
                    children=[
                        dl.TileLayer(url=mapbox_url.format(
                            id="light-v9", access_token=mapbox_access_token)
                        ),
                        dl.LocateControl(options={'locateOptions': {
                            'enableHighAccuracy': True}}),
                        dl.LayerGroup(id="distro_icon_layer")
                    ], style={'height': '650px', 'zIndex': 0})


layout = html.Div(
    children=[
        dmc.Grid([
            dcc.Store(id='map_distro_store', storage_type='memory'),
            dmc.Col([form], sm=12, lg=6),
            dmc.Col([
                    dmc.Center(
                        children=[
                            dmc.Title(id='distro_error_msg',
                                      children='Select a product', order=2)
                        ])], sm=4, lg=4),
            dmc.Col([distro_map], lg=12)
        ])
    ])


@callback(
    [Output('map_distro_store', 'data'),
     Output("loading-output1", "children")],
    [Input('distro-prod-select', 'value')],
    State('map_distro_store', 'data')
)
def load_distro_data(input_product, store_state):

    if input_product is None:
        raise PreventUpdate

    map_q = models.session.query(
        models.Bourbon.longitude,
        models.Bourbon.latitude,
        func.Concat(models.Bourbon_stores.store_addr_2, ' ',
                    models.Bourbon_stores.store_city).label('store_addr_disp'),
        models.Bourbon.insert_dt.label('date'),
        models.Bourbon.quantity
    ) \
        .join(models.Bourbon_stores) \
        .filter(
        models.Bourbon.insert_dt >= '2021-03-01',
        models.Bourbon.productid == input_product
    ) \
        .order_by(models.Bourbon.insert_dt)

    df = pd.read_sql(map_q.statement, models.session.bind)
    models.session.close()

    return [df.to_dict('records'), '']


@callback(
    Output('date_text', 'children'),
    Input({"type": 'date_slider', "index": ALL}, 'value'),
    prevent_initial_call=True
)
def get_slider_value(slider_value):

    if len(slider_value) == 0:
        raise PreventUpdate

    frmt_date = dt.datetime.fromtimestamp(slider_value[0]).strftime('%m/%d/%Y')
    return f"Date: {frmt_date}"


@callback(
    [Output('slider_container', 'children'),
     Output('distro_error_msg', 'children')],
    [Input('map_distro_store', 'data'),
     Input('distro-prod-select', 'value')],
    prevent_initial_call=True
)
def build_slider(store, product):

    if len(store) == 0:
        return [dmc.Slider(), 'No Data Found']

    dates = sorted(
        set([dt.datetime.strptime(row['date'], '%Y-%m-%d').date() for row in store]))

    def unixTimeMillis(dt):
        ''' Convert datetime to unix timestamp '''
        return int(time.mktime(dt.timetuple()))

    marks = [{"value": unixTimeMillis(date)} for date in dates]

    slider = dmc.Slider(
        id={'type': 'date_slider', 'index': 1},
        min=unixTimeMillis(min(dates)),
        max=unixTimeMillis(max(dates)),
        value=unixTimeMillis(min(dates)),
        marks=marks,
        updatemode='drag',
        showLabelOnHover=False
    )

    return [slider, '']


@callback(
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
