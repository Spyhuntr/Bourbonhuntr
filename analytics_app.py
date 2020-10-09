
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from db_conn import connect
import dash_queries as dq
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

from app import app

now = dt.datetime.utcnow()

inv_total_widget = dbc.Card([
    dbc.CardBody([
        dcc.Loading(
            id='loading-1',
            type='graph',
            children=[
        dbc.Row([
            dbc.Col([
                html.H6('Total Inventory'),
                html.H3(id='tot-inv')
            ], sm=6),
            dbc.Col([
                dcc.Graph(
                    id='tot-spark',
                    config={
                        'displayModeBar':False,
                        'staticPlot':True
                    },
                    responsive=True,
                    style={'height':60}),
                html.P('13 Day Trend', style={'text-align':'center', 'margin':0})
            ], sm=6)
        ])
    ])
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
            type='graph',
            children=dcc.Graph(
                id='inv-line-chrt',
                style={'padding':'1.25rem'}
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
                    date=now.date(),
                    min_date_allowed=dt.date(2020, 3, 1),
                    max_date_allowed=now.date()
                ),
                dbc.InputGroupAddon(
                    html.I(id='calendar-icon', className='fas fa-calendar-alt fa-md'), 
                    addon_type="append",
                    style={'padding':'1rem 0.5rem 0 0.5rem'},
                    className='btn-primary'),
            ],
            className="mb-3")
        ], className='col-auto')
    ], justify='end'),
    dbc.Row([
        dbc.Col([inv_total_widget], sm=12, md=4, lg=3),
        dbc.Col([line_chart], sm=12, md=8, lg=9)
    ])
])


@app.callback(
    [Output(component_id='tot-inv', component_property='children'),
     Output(component_id='tot-spark', component_property='figure')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='dt-picker', component_property='date')]
)
def update_page(path, date):

    mydb = connect()

    df = pd.read_sql(dq.tot_inv_query, mydb, params={date})

    df['quantity'] = df['quantity'].astype(int)

    date_param = dt.datetime.strptime(date, '%Y-%m-%d').date()
    
    kpi_df = df[(df['insert_dt'] == date_param)]
    kpi_val = '{:,}'.format(kpi_df['quantity'].sum())

    thirteendaysago = date_param - pd.to_timedelta("13day")

    tot_spark_df = df[(df['insert_dt'] >= thirteendaysago)]
    tot_spark_df = tot_spark_df.groupby(['insert_dt'], as_index=False)['quantity'].sum()

    fig = px.bar(
        tot_spark_df, 
        x="insert_dt", y="quantity",
        labels={
            'insert_dt': '',
            'quantity':''
        }
    )
    
    fig.update_yaxes(visible=False, range=[20000,30000])
    fig.update_traces(
        hovertemplate='%{y:,}'
    ),
    fig.update_layout(
        margin={'t':0,'l':0,'b':0,'r':0},
        plot_bgcolor="white"
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

    mydb = connect()

    df_line = pd.read_sql(dq.tot_inv_query, mydb, params={date})

    date_param = dt.datetime.strptime(date, '%Y-%m-%d').date()
    onewk = date_param - pd.DateOffset(days=7)
    onemonth = date_param - pd.DateOffset(months=1)
    sixmonth = date_param - pd.DateOffset(months=6)
    twelvemonth = date_param - pd.DateOffset(months=12)

    if button_id == 'line-chrt-btn-4':
        df_line = df_line[(df_line['insert_dt'] >= onewk)]
    if button_id == 'line-chrt-btn-3':
        df_line = df_line[(df_line['insert_dt'] >= onemonth)]
    if button_id == 'line-chrt-btn-2':
        df_line = df_line[(df_line['insert_dt'] >= sixmonth)]
    if button_id == 'line-chrt-btn-1':
        df_line = df_line[(df_line['insert_dt'] >= twelvemonth)]

    line_fig = go.Figure()

    line_fig.add_trace(
        go.Scatter(
            x=df_line['insert_dt'], 
            y=df_line['quantity'], 
            mode='lines',
            line={'shape':'spline', 'smoothing': 1.3},
            hovertemplate=
            "<span class='card-header'><b>%{x}</b></span><br>" +
            "Quantity: %{y:,.0}<br>"
        )
    )

    line_fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
        ),
        height=200,
        showlegend=False,
        plot_bgcolor='white',
        margin={'t':0,'l':0,'b':0,'r':0}
    )


    return line_fig, button_id



@app.callback(
    [Output(f"line-chrt-btn-{i}", "active") for i in range(1,5)],
    [Input("line-chrt-btn-value", "children")],
)
def set_active_button(button_id):
    print(button_id)
    if not button_id:
        return [True, False, False, False]
    else:
        return [button_id == f"line-chrt-btn-{i}" for i in range(1,5)]