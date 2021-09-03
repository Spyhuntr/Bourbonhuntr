import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_html_components.Tbody import Tbody
import pandas as pd
import models
import utils
import sd_material_ui as mui

from app import app

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

df_stores = pd.read_sql(models.store_list_q.statement, models.session.bind)
store_values = [(k,v) for k, v in zip(df_stores['storeid'], df_stores['store_addr_disp'])]
models.session.close()

#form controls
form = html.Div(id='form-cntrl-div', 
            children = [
                dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="prod-select",
                        options=[{'label': i[1], 'value': i[0]} for i in product_values],
                        multi=True,
                        placeholder='Select Products...'
                    )
                ], md=6, lg=4, className='mb-2'),
                dbc.Col([
                    dcc.Dropdown(
                        id="store-select",
                        options=[{'label': '#' + i[0] + '-' + i[1], 'value': i[0]} for i in store_values],
                        multi=True,
                        placeholder='Select Stores...'
                    )
                ], md=6, lg=4)
            ], justify='center', className='mb-2')
        ])


layout = html.Div([
    dbc.Row([
        html.H3(id='summary-title', className='header')
    ], no_gutters=True, justify='center'),
    dbc.Row([
        html.P("""This site tracks bourbon inventory in Virginia and the dataset is captured in the morning once a day.  This program cannot guarantee the availability of a particular product.
                If you wish to know if a product is currently available, please go to the VA ABC site.""", 
                className='sub-header')
    ], no_gutters=True, justify='center', style={'text-align': 'center'}),
    dbc.Row([
        dbc.Col([form], sm=12, lg=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='loader',
                children=[html.Div(id='quantity-tbl-div')]
            )], lg=10)
    ], justify='center'),

    mui.Snackbar(
        id='snackbar',
        message=f'Heads up! The database has not finished updating for {utils.now().strftime("%m-%d-%Y")}.',
        autoHideDuration=10000
    )

])



@app.callback(
    Output(component_id='quantity-tbl-div', component_property='children'),
    
    [Input(component_id='prod-select', component_property='value'),
     Input(component_id='store-select', component_property='value')]
)
def update_page(input_product, input_store):

    query = models.session.query(
                    models.Bourbon.storeid, 
                    models.Bourbon_stores.store_full_addr,
                    models.Bourbon_desc.description,
                    models.Bourbon.quantity
                ) \
               .join(models.Bourbon_stores) \
               .join(models.Bourbon_desc) \
               .filter(
                   models.Bourbon.insert_date == utils.get_run_dt()
                )

    if input_product:
        query = query.filter(models.Bourbon.productid.in_((input_product)))
    if input_store:
        query = query.filter(models.Bourbon.storeid.in_((input_store)))

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df.columns = ['Store #', 'Store Address', 'Product', 'Quantity']

    hdr_list = []
    for hdr in df.columns:
        hdr_list.append(html.Th(hdr))
    
    table_header = [html.Thead(html.Tr(hdr_list))]

    if df.empty:
        nodata= [html.Tbody('No data found')]
        return dbc.Table(table_header + nodata, bordered=True, striped=True)

    tbody = []
    for data in df.values:
        row_data=[]
        for ind, i in enumerate(data):
            if ind == 1:
                row_data.append(
                    html.Td(
                        html.A(i, href=f'https://maps.google.com/?q={i}', target='_blank')
                    )
                )
            else:
                row_data.append(html.Td(i))

                
        tbody.append(html.Tr(row_data))
    table_body = [html.Tbody(tbody)]

    dash_tbl = dbc.Table(table_header + table_body, bordered=True, striped=True)

    return dash_tbl

@app.callback(
    Output(component_id="snackbar", component_property='open'),
    [Input(component_id='url', component_property='pathname')],
)
def toggle_modal(url):

    if not utils.is_data_loading():
        return True


@app.callback(
    Output(component_id="summary-title", component_property='children'),
    [Input(component_id='url', component_property='pathname')],
)
def title_date(url):

    return "Welcome to the Bourbonhuntr! Below is the inventory for {}.".format(utils.get_run_dt().strftime('%m-%d-%Y'))
