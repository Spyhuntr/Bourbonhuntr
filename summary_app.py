import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import db_conn as dc
import dash_queries as dq
import datetime as dt
import utils

from app import app

df_products = pd.read_sql(dq.product_query, dc.engine)
#This massages the dataframe into a list of tuples to parse into the options correctly
product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

df_stores = pd.read_sql(dq.stores_query, dc.engine)
store_values = [(k,v) for k, v in zip(df_stores['storeid'], df_stores['store_addr'])]


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
                ], lg=4),
                dbc.Col([
                    dcc.Dropdown(
                        id="store-select",
                        options=[{'label': i[1], 'value': i[0]} for i in store_values],
                        multi=True,
                        placeholder='Select Stores...'
                    )
                ], lg=4)
            ], justify='center', form=True)
        ])


quantity_tbl = html.Div(
    id='quantity-tbl-div',
    children=[]
)

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([], 
                id='info-div')
            ], lg=7)
        ], justify='center'),
        dbc.Row([
            dbc.Col([
                html.H3( 
                    id='summary-title',
                    className='text-primary',
                )
            ], lg=8, style={'text-align':'center'})
        ], no_gutters=True, justify='center'),
        dbc.Row([
            dbc.Col([
                html.P(html.B("""This dataset is captured in the morning once a day.  This program cannot guarantee the availability of a particular product.
                           If you wish to know if a product is currently available, please go to the VA ABC site."""))
            ], lg=12, style={'text-align':'center'})
        ], no_gutters=True, justify='center'),
        dbc.Row([
            dbc.Col([form], sm=12, lg=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id='loading-output-1',
                    type='graph',
                    children=quantity_tbl
                )], lg=10)
        ], justify='center')
    ], fluid=True)
])



@app.callback(
    Output(component_id='quantity-tbl-div', component_property='children'),
    
    [Input(component_id='prod-select', component_property='value'),
     Input(component_id='store-select', component_property='value')]
)
def update_page(input_product, input_store):

    if not input_product:
        input_product = None
    if not input_store:
        input_store = None

    df = pd.read_sql(dq.query, dc.engine, params=(utils.get_run_dt(),utils.get_run_dt()))
    
    df['insert_dt'] = df['insert_dt'].dt.date

    input_product = df['productid'] if input_product == None else input_product
    input_store = df['storeid'] if input_store == None else input_store
    
    
    df_filtered = df[(df['productid'].isin(input_product)) & 
                     (df['storeid'].isin(input_store))]

    #data table
    df_table = df_filtered[['storeid', 'store_full_addr', 'description', 'quantity']]
    
    df_table.columns = ['Store #', 'Store Address', 'Product', 'Quantity']

    hdr_list = []
    for hdr in df_table.columns:
        hdr_list.append(html.Th(hdr))
    
    table_header = [html.Thead(html.Tr(hdr_list))]

    tbody = []
    for data in df_table.values:
        row_data=[]
        for ind, i in enumerate(data):
            if ind == 1:
                row_data.append(
                    html.Td(
                        html.A(i, href='https://maps.google.com/?q={}'.format(i), target='_blank')
                    )
                )
            else:
                row_data.append(html.Td(i))
                
        tbody.append(html.Tr(row_data))
    table_body = [html.Tbody(tbody)]


    dash_tbl = dbc.Table(table_header + table_body, bordered=True, striped=True)

    return dash_tbl

@app.callback(
    Output(component_id="info-div", component_property='children'),
    [Input(component_id='url', component_property='pathname')],
)
def toggle_modal(url):

    db_done_time = utils.now().replace(hour=16, minute=0, second=0, microsecond=0)

    info_div = html.Div([
        html.H4("Heads up!"),
        html.P("The database has not finished updating for {}.".format(utils.now().strftime('%m-%d-%Y')))
    ], className='alert alert-dismissible alert-warning')

    if utils.now().time() < db_done_time.time():
        return info_div


@app.callback(
    Output(component_id="summary-title", component_property='children'),
    [Input(component_id='url', component_property='pathname')],
)
def title_date(url):

    return "Welcome to the Bourbonhuntr! Below is the inventory for {}.".format(utils.get_run_dt().strftime('%m-%d-%Y'))
