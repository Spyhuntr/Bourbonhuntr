
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import models
import datetime as dt
import plotly.express as px
import utils
from sqlalchemy import func, or_
from dateutil.relativedelta import *

from app import app

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

inv_total_widget = dbc.Card([
    dbc.CardBody([
        dcc.Loading(
            id='loading-1',
            children=[
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6('Total Inventory'),
                            html.H2(id='tot-inv')
                        ], style={'position':'relative', 'z-index': '999'}),
                        dcc.Graph(
                            id='tot-spark',
                            config={
                                'displayModeBar':False,
                                'staticPlot':True
                            },
                        responsive=True,
                        style={'height':60, 'margin':'-1.25rem'})
                    ])
                ])
            ]
        )
    ], id='tot_inv_widget')
], className='mb-2')

inv_ytd_widget = dbc.Card([
    dbc.CardBody([
        dcc.Loading(
            id='loading-1',
            children=[
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6('YTD Inventory'),
                            html.H2(id='ytd-inv')
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.H6('Year-over-Year'),
                            html.H3(id='yoy-var-inv')
                        ])
                    ])
                ])
            ]
        )
    ], id='inv_ytd_widget')
], className='mb-2')


line_chart = dbc.Card([
    dbc.CardHeader('Quantity over Time'),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.ListGroup([
                    dbc.ListGroupItem("12 Mths", id="line-chrt-btn-1", action=True),
                    dbc.ListGroupItem("6 Mths", id="line-chrt-btn-2", action=True),
                    dbc.ListGroupItem("1 Mth", id="line-chrt-btn-3", action=True),
                    dbc.ListGroupItem("1 Wk", id="line-chrt-btn-4", action=True)
                ], horizontal=True)
            ], className='col-auto')
        ], justify='end'),
        dcc.Loading(
            id='loading-2',
            children=dcc.Graph(
                id='inv-line-chrt',
                style={'padding':'1.25rem'},
                config={
                    'displayModeBar':False
                }
            )
        )
    ], style={'padding':0}),
    html.Div(id='line-chrt-btn-value', style={'display': 'none'})
])




layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="prod-select",
                options=[{'label': i[1], 'value': i[0]} for i in product_values],
                placeholder='Select Product...'
            )
        ], md=6, lg=3, className='mb-2'),
        dbc.Col([
            dbc.InputGroup([
                dcc.DatePickerSingle(
                    id='dt-picker', 
                    date=utils.get_run_dt(),
                    min_date_allowed=utils.min_data_date(),
                    max_date_allowed=utils.get_run_dt()
                ),
                dbc.InputGroupAddon(
                    html.I(id='calendar-icon', className='fas fa-calendar-alt fa-md'), 
                    addon_type="append",
                    style={'padding':'0.6rem 0.5rem 0 0.5rem'},
                    className='btn-primary'),
            ])
        ], className='col-auto mb-2')
    ], justify='end'),
    html.Div(id='analytics_app_page', children=[
    dbc.Row([
        dbc.Col([inv_total_widget, inv_ytd_widget], sm=12, md=4, lg=2),
        dbc.Col([line_chart], sm=12, md=8, lg=7),
    ], justify='center')], style={'display': 'none'})
])


@app.callback(
    [Output(component_id='tot-inv', component_property='children'),
     Output(component_id='tot-spark', component_property='figure'),
     Output(component_id='ytd-inv', component_property='children')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date'),
     Input(component_id='prod-select', component_property='value')]
)
def update_page(path, date, product):

    today = dt.datetime.strptime(date, '%Y-%m-%d').date()
    start_of_year = today.replace(month=1, day=1)
    thirtydaysago = today - dt.timedelta(30)

    query = models.session.query(
                    models.Bourbon.insert_date.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_date) \
                .filter(
                    models.Bourbon.insert_date.between(start_of_year, date),
                    models.Bourbon.productid == product
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df['quantity'] = df['quantity'].astype(int)

    kpi_df = df[(df['insert_date'] == today)]

    kpi_val = '{:,}'.format(kpi_df['quantity'].sum())

    ytd_val = '{:,}'.format(df['quantity'].sum())

    spark_area_df = df[(df['insert_date'] >= thirtydaysago)]

    fig = px.area(
        spark_area_df, 
        x="insert_date", y="quantity",
        labels={
            'insert_date': '',
            'quantity':''
        },
        template='simple_white',
        log_y=True
    )
    
    fig.update_yaxes(visible=False),
    fig.update_xaxes(visible=False),
    fig.update_traces(
        line={'color':'rgba(31, 119, 180, 0.2)'},
        fillcolor='rgba(31, 119, 180, 0.2)'
    ),
    fig.update_layout(
        margin={'t':0,'l':0,'b':0,'r':0}
    )


    return kpi_val, fig, ytd_val


@app.callback(
    Output(component_id='yoy-var-inv', component_property='children'),
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date'),
     Input(component_id='prod-select', component_property='value')]
)
def update_page(path, date, product):
    
    today = dt.datetime.strptime(date, '%Y-%m-%d').date()
    start_of_year = today.replace(month=1, day=1)
    same_day_last_year = today.replace(today.year - 1)
    start_of_prev_year = today.replace(today.year - 1, month=1, day=1)

    query = models.session.query(
                    models.Bourbon.insert_date.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_date) \
                .filter(
                    or_(models.Bourbon.insert_date.between(start_of_year, date), \
                        models.Bourbon.insert_date.between(start_of_prev_year, same_day_last_year)),
                    models.Bourbon.insert_date >= '2020-03-01',
                    models.Bourbon.productid == product
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    last_yr_quantity = df[(df['insert_date'].between(start_of_prev_year, same_day_last_year))]
    this_yr_quantity = df[(df['insert_date'].between(start_of_year, today))]
    
    yoy_var = 0
    if last_yr_quantity['quantity'].sum() != 0:
        yoy_var = 1 - ((last_yr_quantity['quantity'].sum() - this_yr_quantity['quantity'].sum()) / last_yr_quantity['quantity'].sum()) * 100
    
    if yoy_var < 0:
        arrow = html.I(className='fas fa-arrow-down', 
                       style={'padding-left': '0.4rem', 'color':'red'})
    elif yoy_var > 0:
        arrow = html.I(className='fas fa-arrow-up', 
                       style={'padding-left': '0.4rem','color':'green'})
    else:
        arrow = ''

    return [f'{abs(yoy_var):,.1f}%', arrow]




@app.callback(
    [Output(component_id='inv-line-chrt', component_property='figure'),
     Output(component_id='line-chrt-btn-value', component_property='children')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date'),
     Input(component_id='prod-select', component_property='value'),
     Input(component_id='line-chrt-btn-1', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-2', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-3', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-4', component_property='n_clicks')]
)
def update_page(path, date, product, twelve_mths_btn, six_mths_btn, one_mth_btn, one_wk_btn):

    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'].split('.')[0] == 'dt-picker':
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    date_param = dt.datetime.strptime(date, '%Y-%m-%d').date()
    onewk = date_param - relativedelta(days=6)
    onemonth = date_param - relativedelta(months=1)
    sixmonth = date_param - relativedelta(months=6)
    twelvemonth = date_param - relativedelta(months=12)

    query = models.session.query(
                    models.Bourbon.insert_date.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_date) \
                .filter(
                    models.Bourbon.insert_date.between(twelvemonth, date_param),
                    models.Bourbon.insert_date >= '2020-03-01',
                    models.Bourbon.productid == product
                )

    if button_id == 'line-chrt-btn-4':
        query = query.filter(models.Bourbon.insert_date >= onewk)
    if button_id == 'line-chrt-btn-3':
        query = query.filter(models.Bourbon.insert_date >= onemonth)
    if button_id == 'line-chrt-btn-2':
        query = query.filter(models.Bourbon.insert_date >= sixmonth)
    if button_id == 'line-chrt-btn-1':
        query = query.filter(models.Bourbon.insert_date >= twelvemonth)

    df_line = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    if df_line.empty:
        return utils.no_data_figure, button_id

    line_fig = px.line(df_line, x='insert_date', y='quantity', height=200,
                       labels={
                            'insert_date':'Date',
                            'quantity':'Quantity'
                        },
                        template='simple_white'
                    )

    line_fig.update_layout(
        margin={'l':0, 'r':0, 't':0.5, 'b':0},
        xaxis={'showgrid': False, 'title': ''},
        yaxis={'showgrid': False}
    )

    line_fig.update_traces(
        hovertemplate=
            "<span class='card-header'><b>%{x}</b></span><br>" +
            "Quantity: %{y:,.0}<br>"
    )

    return line_fig, button_id



@app.callback(
    [Output(f"line-chrt-btn-{i}", "active") for i in range(1,5)],
    [Input("line-chrt-btn-value", "children")],
)
def set_active_button(button_id):
    if button_id in ('', 'prod-select'):
        return [True, False, False, False]
    else:
        return [button_id == f"line-chrt-btn-{i}" for i in range(1,5)]


@app.callback(
    [Output('prod-select', 'style'),
     Output('analytics_app_page','style')],
    [Input('prod-select', 'value')]
)
def empty_chart(product):
    if product is None:
        return {'border':'1px solid rgba(205,2,0,0.9)', 'border-radius':'4px'}, {'display': 'none'}
    else:
        return {}, {'display':'block'}