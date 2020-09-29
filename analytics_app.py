
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

from app import app

now = dt.datetime.utcnow()

mydb = connect()

inv_total_widget = dbc.Card([
    dbc.CardBody([
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
                    style={'height':60})
            ], sm=6)
        ], no_gutters=True)
    ])
], id='tot_inv_widget')

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id='loading-output-1',
                    type='graph',
                    children=inv_total_widget
                )
            ], lg=4, md=6)
        ])
    ])
])


@app.callback(
    [Output(component_id='tot-inv', component_property='children'),
     Output(component_id='tot-spark', component_property='figure')],
    [Input(component_id='url', component_property='pathname')],
)
def update_page(path):

    print('Updating figures...')

    df = pd.read_sql(dq.tot_inv_spark_query, mydb)

    df['quantity'] = df['quantity'].astype(int)

    kpi_df = df[(df['INSERT_DT'] == now.date())]
    kpi_val = '{:,}'.format(kpi_df['quantity'].sum())

    tot_spark_df = df[['INSERT_DT','quantity']]
    tot_spark_df = tot_spark_df.groupby(['INSERT_DT'], as_index=False)['quantity'].sum()

    fig = px.bar(
        tot_spark_df, 
        x="INSERT_DT", y="quantity",
        labels={
            'INSERT_DT': '',
            'quantity':''
        }
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, range=[20000,30000])
    fig.update_traces(
        hovertemplate='%{y:,}'
    ),
    fig.update_layout(
        margin={'t':0,'l':0,'b':0,'r':0},
        plot_bgcolor="white"
    )

    return kpi_val, fig