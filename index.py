
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from app import app
import summary_app, analytics_app, map_app, distro_app

from environment.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK

server = app.server

#begin layout section
icon_set = dbc.Col(
            dbc.DropdownMenu(
                id='admin-menu',
                label='',
                children=[
                    dbc.DropdownMenuItem(
                        html.A(
                            href="https://abc.virginia.gov",
                            children=[
                                html.I(id='more-sites', className='fas fa-store fa-fw fa-lg me-2'),
                                html.Span('Go to ABC Site')
                            ],
                            target="_blank"
                        )
                    ),
                    dbc.DropdownMenuItem(
                        html.A(
                            id='dwnload-prd-list',
                            href="#",
                            children=[
                                html.I(className='fas fa-download fa-fw fa-lg me-2'),
                                html.Span('Tracked Products')
                            ]
                        )
                    ),
                    dcc.Download(id="download-product-csv")
                ],
                nav=True
            ), width=2, md=1, lg=1, class_name='g-0'
)

navbar = dbc.Row([
        dbc.Col(
            html.I(id='menu-button', className='fas fa-bars fa-2x'), 
            width=1, className='col-sm-auto'
        ),
        dbc.Col(
            html.Div(
                html.Img(src='/assets/TheBourbonHuntr_Logo_v1.png', height='50px', width='215px')
            ), className='navbar-title'),
        icon_set
    ], className='navbar', justify='between')


left_menu = dbc.Offcanvas(
    id='left-side-menu',
    children=[
    html.Div([
        html.Img(src='/assets/bourbon-nav-img.jpg', style={'max-width':'100%'})
    ]),
    html.Ul([
        html.Li([
            dcc.Link([
                html.I(className='fas fa-home fa-fw fa-2x'),
                html.Span('Daily Inventory', className='align-top')
            ], href='/', refresh=True)
        ], id='daily_inv_link', className='side-nav-link'),

        html.Li([
            dcc.Link([
                html.I(className='fas fa-chart-bar fa-fw fa-2x'), 
                html.Span('Analytics', className='align-top') 
            ], href='/analytics_app', refresh=True),
        ], id='anala_link', className='side-nav-link'),

        html.Li([
            dcc.Link([
                html.I(className='fas fa-map fa-fw fa-2x'), 
                html.Span('Current Inventory Map', className='align-top') 
            ], href='/map_app', refresh=True),
        ], id='map_ci_link', className='side-nav-link'),

        html.Li([
            dcc.Link([
                html.I(className='fas fa-map-marker fa-fw fa-2x'), 
                html.Span('Distribution Over Time', className='align-top') 
            ], href='/distro_app', refresh=True),
        ], id='distro_link', className='side-nav-link')

    ], className='side-nav mt-4')
], is_open=False)


def serve_layout():
    return html.Div([
        left_menu,
        dcc.Location(id='url', refresh=False),
        navbar,
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div(id='page-content')
                ], lg=12)
            ])
        ], fluid=True)
])

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return summary_app.layout
    if pathname == '/analytics_app':
        return analytics_app.layout
    if pathname == '/map_app':
        return map_app.layout
    if pathname == '/distro_app':
        return distro_app.layout
    else:
        return '404'


@app.callback(
    Output('left-side-menu', 'is_open'),
    Input('menu-button', 'n_clicks'),
    [State('left-side-menu', 'is_open')]
)
def disp_menu(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output('download-product-csv', 'data'),
    Input('dwnload-prd-list', 'n_clicks'),
    prevent_initial_call=True,
)
def download_products(n1):

    return dcc.send_data_frame(summary_app.df_products.to_csv, "products.csv")


if __name__ == '__main__':
    app.run_server(
        host=APP_HOST,
        port=APP_PORT,
        debug=APP_DEBUG,
        dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

