
import dash
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
import pandas as pd
import models
import utils
import dash_ag_grid as dag



# form controls
form = html.Div(id='form-cntrl-div',
                children=[
                    dmc.Grid([
                        dmc.Col([
                            dmc.MultiSelect(
                                id="prod-select",
                                placeholder='Select Products...',
                                radius="md",
                                icon=[html.I(className='fas fa-magnifying-glass')]
                            )
                        ], sm=5, lg=4),
                        dmc.Col([
                            dmc.MultiSelect(
                                id="store-select",
                                placeholder='Select Stores...',
                                radius="md",
                                icon=[html.I(className='fas fa-magnifying-glass')]
                            )
                        ], sm=5, lg=4)
                    ], justify='center')
                ])

dash.register_page(__name__, path='/', title='Home')

layout = dmc.Grid([
    dmc.Col([
        dmc.Text(id='summary-title', align='center'),
        dmc.Text("""This site tracks bourbon inventory in Virginia and the dataset is captured in the morning twice a day.  This program cannot guarantee the availability of a particular product.
                If you wish to know if a product is currently available, please go to the VA ABC site.""", align="center")
    ], span=11),
    dmc.Col([form], span=12),
    dmc.Col([
        dmc.Paper(children=[
        dmc.Group([
            dmc.Button(
                'Download Current Inventory',
                id='dwnload-curr-inv-list',
                leftIcon=[html.I(className='fas fa-download fa-fw fa-md')],
                style={'marginBottom': '20px'}
            )], position='right'),
        dcc.Download(id="download-curr-inv-csv"),
        dmc.LoadingOverlay(
            children=[html.Div(id='quantity-tbl-div')],
            loaderProps={"variant": "dots", "color": "orange", "size": "xl"}
        )], shadow="xl", radius="md", p="md", withBorder=True)
        ], span=12, lg=9),

    html.Div(id="notifications-container")

], justify="center")


@callback(
    [Output('prod-select', 'data'),
     Output('store-select', 'data')],
     Input('url', 'pathname')
)
def update_page(_):

    df_products = pd.read_sql(models.get_product_list_query(), models.session.bind)
    product_values = [(k, v) for k, v in zip(
        df_products['productid'], df_products['description'])]


    df_stores = pd.read_sql(models.get_store_list_query(), models.session.bind)
    store_values = [(k, v) for k, v in zip(
        df_stores['storeid'], df_stores['store_addr_disp'])]

    models.session.close()
    products = [{'label': i[1], 'value': i[0]} for i in product_values]
    stores = [{'label': '#' + i[0] + ' - ' + i[1], 'value': i[0]} for i in store_values]

    return products, stores

@callback(
    Output('quantity-tbl-div', 'children'),

    [Input('prod-select', 'value'),
     Input('store-select', 'value')]
)
def update_page(input_product, input_store):

    query = models.session.query(
        models.Bourbon.storeid,
        models.Bourbon_stores.store_addr_2 +
        ', ' +
        models.Bourbon_stores.store_city + ' ' + models.Bourbon_stores.store_state,
        models.Bourbon_desc.description,
        models.Bourbon.quantity
    ) \
        .join(models.Bourbon_stores) \
        .join(models.Bourbon_desc) \
        .filter(
        models.Bourbon.insert_dt == utils.get_run_dt()
    )

    if input_product:
        query = query.filter(models.Bourbon.productid.in_((input_product)))
    if input_store:
        query = query.filter(models.Bourbon.storeid.in_((input_store)))

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df.columns = ['Store #', 'Store Address', 'Product', 'Quantity']

    columnDefs = [
        { "field": "Store #"},
        { "field": "Store Address"},
        { "field": "Product" },
        { "field": "Quantity", 'cellStyle': {'textAlign': 'center'}, 'headerClass': 'ag-center-header'}
    ]

    dash_tbl = dag.AgGrid(
        columnDefs = columnDefs,
        rowData = df.to_dict('records'),
        columnSize=None,
        defaultColDef={'flex': 1},
        dashGridOptions={"pagination": True, "paginationPageSize": 12, 'domLayout': 'autoHeight'},
        style={'height': 'auto'} #Removes the arbitrary 400px height
    )

    return dash_tbl


@callback(
    Output('notifications-container', 'children'),
    [Input('url', 'pathname')],
)
def toggle_modal(_):

    if utils.is_data_loading():
        return dmc.Notification(
            message=f'Still updating for {utils.now().strftime("%m-%d-%Y")}.',
            id='snackbar',
            title='Heads up!',
            icon=[html.I(className='fas fa-exclamation fa-fw fa-lg')],
            action="show"
        )


@callback(
    Output("summary-title", 'children'),
    [Input('url', 'pathname')],
)
def title_date(_):

    return "Welcome to the Bourbonhuntr! Inventory for {}.".format(utils.get_run_dt().strftime('%m-%d-%Y'))


@callback(
    Output('download-curr-inv-csv', 'data'),
    Input('dwnload-curr-inv-list', 'n_clicks'),
    prevent_initial_call=True,
)
def download_products(n1):

    query = models.session.query(
        models.Bourbon.storeid,
        models.Bourbon_stores.store_full_addr,
        models.Bourbon_desc.description,
        models.Bourbon.quantity
    ) \
        .join(models.Bourbon_stores) \
        .join(models.Bourbon_desc) \
        .filter(
        models.Bourbon.insert_dt == utils.get_run_dt()
    )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    return dcc.send_data_frame(df.to_csv, f"Current Inventory {utils.get_run_dt()}.csv")
