
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import db_conn as dc
import models
import datetime as dt
import plotly.express as px
import utils
from sqlalchemy import cast, Date, func
from dateutil.relativedelta import *

from app import app

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
])


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
            dbc.InputGroup([
                dcc.DatePickerSingle(
                    id='dt-picker', 
                    date=utils.get_run_dt(),
                    min_date_allowed=dt.date(2020, 3, 1),
                    max_date_allowed=utils.get_run_dt()
                ),
                dbc.InputGroupAddon(
                    html.I(id='calendar-icon', className='fas fa-calendar-alt fa-md'), 
                    addon_type="append",
                    style={'padding':'1rem 0.5rem 0 0.5rem'},
                    className='btn-primary'),
            ],
            className="mb-2")
        ], className='col-auto')
    ], justify='end'),
    dbc.Row([
        dbc.Col([inv_total_widget], sm=12, md=4, lg=2),
        dbc.Col([line_chart], sm=12, md=8, lg=7)
    ], justify='center')
])


@app.callback(
    [Output(component_id='tot-inv', component_property='children'),
     Output(component_id='tot-spark', component_property='figure')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date')]
)
def update_page(path, date):

    date_param = dt.datetime.strptime(date, '%Y-%m-%d').date()
    thirtydaysago = date_param - pd.to_timedelta("30day")

    query = models.session.query(
                    cast(models.Bourbon.insert_dt, Date).label('insert_dt'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(cast(models.Bourbon.insert_dt, Date)) \
                .filter(
                    cast(models.Bourbon.insert_dt, Date).between(thirtydaysago, date_param),
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df['quantity'] = df['quantity'].astype(int)

    kpi_df = df[(df['insert_dt'] == date_param)]
    kpi_val = '{:,}'.format(kpi_df['quantity'].sum())

    fig = px.area(
        df, 
        x="insert_dt", y="quantity",
        labels={
            'insert_dt': '',
            'quantity':''
        },
        template='simple_white',
        log_y=True
    )
    
    fig.update_yaxes(visible=False),
    fig.update_xaxes(visible=False),
    fig.update_traces(
        hovertemplate='%{y:,}',
        line={'color':'rgba(31, 119, 180, 0.2)'},
        fillcolor='rgba(31, 119, 180, 0.2)'
    ),
    fig.update_layout(
        margin={'t':0,'l':0,'b':0,'r':0}
    )


    return kpi_val, fig



@app.callback(
    [Output(component_id='inv-line-chrt', component_property='figure'),
     Output(component_id='line-chrt-btn-value', component_property='children')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date'),
     Input(component_id='line-chrt-btn-1', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-2', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-3', component_property='n_clicks'),
     Input(component_id='line-chrt-btn-4', component_property='n_clicks')]
)
def update_page(path, date, twelve_mths_btn, six_mths_btn, one_mth_btn, one_wk_btn):

    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'].split('.')[0] == 'dt-picker':
        button_id = None
    else:    
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    date_param = dt.datetime.strptime(date, '%Y-%m-%d').date()
    onewk = date_param - relativedelta(days=7)
    onemonth = date_param - relativedelta(months=1)
    sixmonth = date_param - relativedelta(months=6)
    twelvemonth = date_param - relativedelta(months=12)

    query = models.session.query(
                    cast(models.Bourbon.insert_dt, Date).label('insert_dt'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(cast(models.Bourbon.insert_dt, Date)) \
                .filter(
                    cast(models.Bourbon.insert_dt, Date).between(twelvemonth, date_param),
                    cast(models.Bourbon.insert_dt, Date) >= '2020-03-01',
                )

    if button_id == 'line-chrt-btn-4':
        query = query.filter(cast(models.Bourbon.insert_dt, Date) >= onewk)
    if button_id == 'line-chrt-btn-3':
        query = query.filter(cast(models.Bourbon.insert_dt, Date) >= onemonth)
    if button_id == 'line-chrt-btn-2':
        query = query.filter(cast(models.Bourbon.insert_dt, Date) >= sixmonth)
    if button_id == 'line-chrt-btn-1':
        query = query.filter(cast(models.Bourbon.insert_dt, Date) >= twelvemonth)

    df_line = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    line_fig = px.line(df_line, x='insert_dt', y='quantity', height=200,
                       labels={
                            'insert_dt':'Date',
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
    if not button_id:
        return [True, False, False, False]
    else:
        return [button_id == f"line-chrt-btn-{i}" for i in range(1,5)]