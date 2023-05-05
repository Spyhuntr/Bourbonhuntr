
import dash
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
import pandas as pd
import models
import datetime as dt
import plotly.express as px
import utils
from sqlalchemy import func, or_
from dateutil.relativedelta import *
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import dash_ag_grid as dag

dash.register_page(__name__, path='/analytics', title='Analytics')

df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
product_values = [(k,v) for k, v in zip(df_products['productid'], df_products['description'])]

inv_total_widget = dmc.Paper([
    dmc.LoadingOverlay(
        children=[
            dmc.Stack([
                html.Div([
                    dmc.Text(id='tot-inv-title'),
                    dmc.Text(id='tot-inv', size='2rem', weight=700)
                ], style={'position': 'relative', 'z-index': '999'}),
                html.Div(id='tot-spark-container')
            ])
        ],
    loaderProps={"variant": "dots", "color": "orange", "size": "xl"},
    style={'zIndex':1})
], shadow="xl", p="md", withBorder=True, id='tot_inv_widget', style={'margin-bottom': "1rem"})


inv_ytd_widget = dmc.Paper([
        dmc.LoadingOverlay(
            children=[
                dmc.Group([
                        html.Div([
                            dmc.Text('YTD Max'),
                            dmc.Text(id='ytd-inv', size='2rem', weight=700)
                        ]),
                        html.Div([
                            dmc.Text('Year-over-Year'),
                            dmc.Text(id='yoy-var-inv', size='2rem', weight=700)
                        ])
                ], position="apart")
            ],
        loaderProps={"variant": "dots", "color": "orange", "size": "xl"},
        style={'zIndex':1})
], shadow="xl", p="md", withBorder=True, id='inv_ytd_widget')


line_chart = dmc.Paper([
    dmc.Text('Quantity over Time'),
    dmc.Group([
    dmc.SegmentedControl(
        id="line-chart-control",
        value="twelvemonth",
        data=[
            {"value": "twelvemonth", "label": "12 Months"},
            {"value": "sixmonth", "label": "6 Months"},
            {"value": "onemonth", "label": "1 Month"},
            {"value": "onewk", "label": "1 Week"}]
    )], position='right',style={'margin-top': '-2rem'}),
    dmc.LoadingOverlay(
        children=[html.Div(id='inv-line-chrt')],
        loaderProps={"variant": "dots", "color": "orange", "size": "xl"},
        style={'zIndex':1}),
    html.Div(id='line-chrt-btn-value')
], shadow="xl", p="md", withBorder=True)

hbar_chart = dmc.Paper([
    dmc.LoadingOverlay(
        children=html.Div(
            id='inv-hbar-chrt'
        ),
    loaderProps={"variant": "dots", "color": "orange", "size": "xl"})
], shadow="xl", p="md", withBorder=True)

cal_chart = dmc.Paper([
    dmc.Text('Calendar'),
    dmc.LoadingOverlay(
    children=[html.Div(id='inv-cal-chrt')],
    loaderProps={"variant": "dots", "color": "orange", "size": "xl"})
], shadow="xl", p="md", withBorder=True)


layout = dmc.Grid([
    dmc.Col([
        dmc.Group([
            dmc.Select(
                id="analysis-prod-select",
                data=[{'label': i[1], 'value': i[0]}
                         for i in product_values],
                placeholder='Select Product...',
                searchable=True,
                required=True,
                icon=[html.I(className='fas fa-magnifying-glass')],
                style={'zIndex':10}
            ),

            dmc.DateRangePicker(
                id='dt-picker',
                icon=[html.I(className='fas fa-calendar-alt fa-md')],
                style={"width": 350}
            )
            
        ], position="right")
    ], span=12),
    dmc.Col([inv_total_widget, inv_ytd_widget], sm=12, md=4, lg=3),
    dmc.Col([line_chart], sm=12, md=8, lg=9),
    dmc.Col([hbar_chart], sm=12, md=12, lg=4),
    dmc.Col([cal_chart], sm=12, md=12, lg=8)
])


@callback(
    [Output('dt-picker', 'value'),
     Output('dt-picker', 'minDate'),
     Output('dt-picker', 'maxDate')],
     Input('url', 'pathname')
)
def updt_controls(url):
    return [utils.get_run_dt(), utils.get_run_dt()], utils.min_data_date(), utils.get_run_dt()


@callback(
    [Output('tot-inv', 'children'),
     Output('tot-spark-container', 'children'),
     Output('ytd-inv', 'children'),
     Output('tot-inv-title', 'children')],
    [Input('dt-picker', 'value'),
     Input('analysis-prod-select', 'value')]
)
def update_page(dates, product):

    if product is None:
        return dash.no_update
        
    from_date, to_date = dates

    today = dt.datetime.strptime(to_date, '%Y-%m-%d').date()
    start_of_year = today.replace(month=1, day=1)
    thirtydaysago = today - dt.timedelta(30)

    query = models.session.query(
                    models.Bourbon.insert_dt.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_dt) \
                .order_by(models.Bourbon.insert_dt) \
                .filter(
                    models.Bourbon.insert_dt.between(start_of_year, to_date),
                    models.Bourbon.productid == product
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df['quantity'] = df['quantity'].astype(int)

    kpi_df = df[(df['insert_date'] == today)]

    kpi_val = dmc.Text(f'{kpi_df["quantity"].sum():,}')
    ytd_val = dmc.Text('0') if df["quantity"].sum() == 0 else dmc.Text(f'{df["quantity"].cummax().max():,}')

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

    graph = dcc.Graph(
                figure=fig,
                config={
                    'displayModeBar': False,
                    'staticPlot': True
                },
                responsive=True,
                style={'height': 60, 'margin': '-1rem'})

    tot_inv_title = today.strftime('%m/%d/%Y') + ' Inventory'

    return kpi_val, graph, ytd_val, tot_inv_title


@callback(
    Output('yoy-var-inv', 'children'),
    [Input('dt-picker', 'value'),
     Input('analysis-prod-select', 'value')],
     prevent_initial_call=True
)
def update_page(dates, product):
    
    if product is None:
        return dash.no_update

    from_date, to_date = dates

    today = dt.datetime.strptime(to_date, '%Y-%m-%d').date()
    start_of_year = today.replace(month=1, day=1)
    same_day_last_year = today.replace(today.year - 1)
    start_of_prev_year = today.replace(today.year - 1, month=1, day=1)

    query = models.session.query(
                    models.Bourbon.insert_dt.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_dt) \
                .filter(
                    or_(models.Bourbon.insert_dt.between(start_of_year, to_date), \
                        models.Bourbon.insert_dt.between(start_of_prev_year, same_day_last_year)),
                    models.Bourbon.insert_dt >= '2020-03-01',
                    models.Bourbon.productid == product
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    last_yr_quantity = df[(df['insert_date'].between(start_of_prev_year, same_day_last_year))]
    this_yr_quantity = df[(df['insert_date'].between(start_of_year, today))]

    yoy_var = 0
    if not (last_yr_quantity['quantity'].empty or this_yr_quantity['quantity'].empty):
        yoy_var = ((this_yr_quantity['quantity'].cummax().max() - last_yr_quantity['quantity'].cummax().max()) / last_yr_quantity['quantity'].cummax().max()) * 100
 
    arrow = html.I(style={'padding-left': '0.2rem'})
    if yoy_var < 0:
        arrow.className = 'fas fa-arrow-down red'
    elif yoy_var > 0:
        arrow.className = 'fas fa-arrow-up green'
    else:
        ''

    return [f'{abs(yoy_var):,.1f}%', arrow]


@callback(
    Output('inv-line-chrt', 'children'),
    [Input('dt-picker', 'value'),
     Input('analysis-prod-select', 'value'),
     Input('line-chart-control', 'value')],
     prevent_initial_call=True
)
def update_page(dates, product, line_chart_btn_val):

    if product is None:
        return dash.no_update

    from_date, to_date = dates

    date_param = dt.datetime.strptime(to_date, '%Y-%m-%d').date()
    onewk = date_param - relativedelta(days=6)
    onemonth = date_param - relativedelta(months=1)
    sixmonth = date_param - relativedelta(months=6)
    twelvemonth = date_param - relativedelta(months=12)

    query = models.session.query(
                    models.Bourbon.insert_dt.label('insert_date'),
                    func.sum(models.Bourbon.quantity).label('quantity')
                ) \
                .group_by(models.Bourbon.insert_dt) \
                .order_by(models.Bourbon.insert_dt) \
                .filter(
                    models.Bourbon.insert_dt.between(twelvemonth, date_param),
                    models.Bourbon.productid == product
                )

    if line_chart_btn_val == 'onewk':
        query = query.filter(models.Bourbon.insert_dt >= onewk)
    if line_chart_btn_val == 'onemonth':
        query = query.filter(models.Bourbon.insert_dt >= onemonth)
    if line_chart_btn_val == 'sixmonth':
        query = query.filter(models.Bourbon.insert_dt >= sixmonth)
    if line_chart_btn_val == 'twelvemonth':
        query = query.filter(models.Bourbon.insert_dt >= twelvemonth)

    df_line = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    if df_line.empty:
        return utils.no_data_figure

    line_fig = px.line(
                df_line, 
                x='insert_date', 
                y='quantity', 
                height=200,
                labels={
                    'insert_date':'Date',
                    'quantity':'Quantity'
                },
                template='simple_white'
    )

    line_fig.update_layout(
        margin={'l':0, 'r':0, 't':0.5, 'b':0},
        xaxis={'showgrid': False, 'title': ''},
        yaxis={'showgrid': True}
    )

    line_fig.update_traces(
        hovertemplate=
            "<span class='card-header'><b>%{x}</b></span><br>" +
            "Quantity: %{y}<br>"
    )

    graph = dcc.Graph(
            figure=line_fig,
            style={'padding-top': '1.25rem'},
            config={
                'displayModeBar': False
            }
        )

    return graph


@callback(
    Output('inv-hbar-chrt', 'children'),
    [Input('dt-picker', 'value'),
     Input('analysis-prod-select', 'value')],
     prevent_initial_call=True
)
def update_hbar_chrt(dates, product):

    if product is None:
        return dash.no_update

    from_date, to_date = dates

    today = dt.datetime.strptime(to_date, '%Y-%m-%d').date()
    start_of_year = today.replace(month=1, day=1)

    query = models.session.query(
                    models.Bourbon.storeid.label('storeid'),
                    models.Bourbon_stores.store_city.label('store_city'),
                    func.round(func.avg(models.Bourbon.quantity), 2).label('quantity'),
                    func.max(models.Bourbon.insert_dt).label('last_seen')
                ) \
                .join(models.Bourbon_stores) \
                .group_by(models.Bourbon.storeid) \
                .filter(
                    models.Bourbon.insert_dt.between(start_of_year, to_date),
                    models.Bourbon.productid == product
                )
                

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    df.sort_values(by='quantity', inplace=True, ascending=False)
    df.columns = ['Store', 'Store City', 'Avg Quantity', 'Last Seen']

    columnDefs = [
        {'headerName': 'Top 20 Stores',
         'children': [
        { "field": "Store"},
        { "field": "Store City"},
        { "field": "Avg Quantity" },
        { "field": "Last Seen"}
         ]}
    ]

    table_fig = dag.AgGrid(
        columnDefs = columnDefs,
        rowData = df.to_dict('records'),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationPageSize": 9, 'domLayout': 'autoHeight', "rowHeight": 30},
        style={'height': 'auto'} #Removes the arbitrary 400px height
    )

    return table_fig


@callback(
    Output('inv-cal-chrt', 'children'),
    [Input('dt-picker', 'value'),
     Input('analysis-prod-select', 'value')],
     prevent_initial_call=True
)
def update_page(dates, product):

    if product is None:
        return dash.no_update

    from_date, to_date = dates

    def build_subplot(df, year, fig, row):

        d1 = dt.date(year, 1, 1)
        d2 = dt.date(year, 12, 31)

        num_of_days = (d2-d1).days + 1

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_days =   [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        if num_of_days == 366:
            month_days[1] = 29
        
        month_positions = (np.cumsum(month_days) - 15)/7

        dates_in_year = [d1 + dt.timedelta(i) for i in range(num_of_days)]

        all_dates_df = pd.DataFrame(dates_in_year, columns=['date'])
        merge = pd.merge(all_dates_df, df, how='left', on='date')
        weekdays_in_year = [i.weekday() for i in dates_in_year]
        weeknumber_of_dates = []
            
        for i in dates_in_year:
            inferred_week_no = int(i.strftime("%V"))

            if inferred_week_no >= 52 and i.month == 1:
                weeknumber_of_dates.append(0)
            elif inferred_week_no == 1 and i.month == 12:
                weeknumber_of_dates.append(53)
            else:
                weeknumber_of_dates.append(inferred_week_no)
            

        text = [str(i) for i in dates_in_year]
        colorscale=[[False, '#eeeeee'], [True, '#2626d9']]

        if merge['quantity'].sum() == 0:
            colorscale=[[False, '#eeeeee'], [True, '#eeeeee']]
        
        z = merge['quantity'].fillna(0).to_list()

        data = [
            go.Heatmap(
                x = weeknumber_of_dates,
                y = weekdays_in_year,
                z = z,
                text=text,
                xgap=3,
                ygap=3,
                showscale=False,
                colorscale=colorscale,
                hovertemplate = 'Date: %{text}<br>Quantity: %{z}<extra></extra>',
            )
        ]

        layout = go.Layout(
            height=200,
            yaxis={
                'tickmode': 'array',
                'ticktext': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'tickvals': [0,1,2,3,4,5,6],
                'autorange': 'reversed'
            },
            xaxis={
                'tickmode': 'array',
                'ticktext': month_names,
                'tickvals': month_positions
            },
            plot_bgcolor=('#fff'),
            margin={'l':0, 'r':0, 't':20.5, 'b':0},
            showlegend=False,
        )

        fig.add_traces(data, rows=[row+1], cols=[1])
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

        return fig





    curr_yr = dt.datetime.strptime(to_date, '%Y-%m-%d').year
    prev_yr = curr_yr - 1

    query = models.session.query(
                    models.Bourbon.insert_dt.label('date'),
                    func.sum(models.Bourbon.quantity).label('quantity'),
                    models.Bourbon.year.label('year')
                ) \
                .group_by(models.Bourbon.insert_dt) \
                .filter(
                    models.Bourbon.year >= prev_yr,
                    models.Bourbon.insert_dt >= '2020-03-01',
                    models.Bourbon.productid == product
                )

    df = pd.read_sql(query.statement, models.session.bind)
    models.session.close()

    if df.empty:
        return utils.no_data_figure

    fig = make_subplots(rows=2, cols=1, subplot_titles=[prev_yr, curr_yr])
    for i, year in enumerate([prev_yr, curr_yr]):
        data=df[df['year'] == year]
        build_subplot(data, year, fig, row=i)
        fig.update_layout(height=395)

        graph = dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': False
            }
        )

    return graph
