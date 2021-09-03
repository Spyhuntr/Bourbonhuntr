import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from sd_material_ui import Drawer
from dash.dependencies import Input, Output, State
import os

from app import app
import summary_app, analytics_app, map_app, distro_app

server = app.server

cwd_path = os.path.dirname(__file__)

#begin layout section
icon_set = dbc.Col([
            html.A(
                href="https://abc.virginia.gov",
                children=html.I(id='more-sites', className='fas fa-store fa-lg fa-fw'),
                target="_blank"
            )
        ], width=1)

navbar = dbc.Row([
        dbc.Col(
            html.I(id='menu-button', className='fas fa-bars fa-2x fa-fw'),
        width=1, className='col-sm-auto'),
        dbc.Col(
            html.Div(
                html.Img(src=os.path.join(cwd_path, '/assets/TheBourbonHuntr_Logo_v1.png'), height='50px')
            ), className='navbar-title'),
        icon_set
    ], className='navbar', align='center')


left_menu = Drawer(
    id='left-side-menu',
    className='drawer',
    children=[
    html.Div([
        html.Img(src=os.path.join(cwd_path, '/assets/bourbon-nav-img.jpg'), style={'max-width':'100%'})
    ]),
    html.Ul([
        html.Li('Pages', className='drawer-title'),

        dcc.Link([
            html.Li([
                html.I(className='fas fa-home'), 
                html.Span('Daily Inventory') 
            ], id='daily_inv_link', className='side-nav-link')
        ], href='/', refresh=True),

        dcc.Link([
            html.Li([
                html.I(className='fas fa-chart-bar'), 
                html.Span('Analytics') 
            ], id='anala_link', className='side-nav-link')
        ], href='/analytics_app', refresh=True),

        html.Li([html.Span('Maps')], className='side-nav-link'),

        dcc.Link([
            html.Li([
                html.I(className='fas fa-map'), 
                html.Span('Current Inventory') 
            ], id='map_ci_link', className='side-nav-link side-nav-sub')
        ], href='/map_app', refresh=True),

        dcc.Link([
            html.Li([
                html.I(className='fas fa-map-marker'), 
                html.Span('Distribution Over Time') 
            ], id='distro_link', className='side-nav-link side-nav-sub')
        ], href='/distro_app', refresh=True),

    ], className='side-nav')
])


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
        ], fluid=True),
        html.Div(id='backdrop')
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
    [Output('left-side-menu', 'open'), Output('backdrop', 'style')],
    [Input('menu-button', 'n_clicks'), Input('backdrop', 'n_clicks')])
def disp_menu(n1, n2):
    ctx = dash.callback_context

    clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    turn_on = [
        True,
        {'visibility': 'visible'}
    ]

    turn_off = [
        False,
        {'visibility': 'hidden'}
    ]

    if clicked == 'menu-button':
        return turn_on
    elif clicked == 'backdrop':
        return turn_off
    else:
        return turn_off



if __name__ == '__main__':
    app.run_server(debug=True)

