import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import os

from app import app
import summary_app, analytics_app, map_app, distro_app

server = app.server

cwd_path = os.path.dirname(__file__)

#begin layout section
icon_set = dbc.Row(
    [
        dbc.Col([
            html.A(
                href="https://abc.virginia.gov",
                children=html.I(id='more-sites', className='fas fa-store fa-lg fa-fw'),
                target="_blank"
            )
        ])
    ],
    no_gutters=True,
    className='ml-auto',
    align='center',
)

navbar = dbc.Navbar([
    dbc.Row([
        html.I(id='menu-button', className='fas fa-bars fa-2x fa-fw', style={'cursor':'pointer'}),
        dbc.Col(html.Img(src=os.path.join(cwd_path, '/assets/TheBourbonHuntr_Logo_v1.png'), height='50px')),
    ], 
    align='center'),
    icon_set
], className='mb-2')


left_menu = html.Div([
    html.Div([
        html.Img(src=os.path.join(cwd_path, '/assets/bourbon-nav-img.jpg'), style={'max-width':'100%'})
    ], className='leftbar-img'),
    html.Ul([
        html.Li('Pages', className='side-nav-title side-nav-item'),
        dcc.Link([
            html.Li([
                html.I(id='daily_inv_icon', className='fas fa-home'), 
                html.Span('Daily Inventory') 
            ], id='daily_inv_link', className='side-nav-link')
        ], href='/', refresh=True),
        dcc.Link([
            html.Li([
                html.I(id='anala_icon', className='fas fa-chart-bar'), 
                html.Span('Analytics') 
            ], id='anala_link', className='side-nav-link')
        ], href='/analytics_app', refresh=True),
        html.Li([
            html.I(id='map_icon', className='fas fa-map'), 
            html.Span('Maps'),
            html.Ul([
                dcc.Link([
                    html.Li([
                        html.Span('Current Inventory') 
                    ], id='map_ci_link', className = 'side-sub-link')
                ], href='/map_app', refresh=True),
                dcc.Link([
                    html.Li([
                        html.Span('Distribution Over Time') 
                    ], id='distro_link', className = 'side-sub-link')
                ], href='/distro_app', refresh=True)
            ], id='map_sub_menu', className='map-sub-menu') 
        ], id='maps_link', className='side-nav-link side-sub-menu-hdr')
    ], className='side-nav', style={'padding': '0'})
], id='left-side-menu', className="left-side-menu")


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
        html.Div(id='overlay')
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
    [Output('left-side-menu', 'style'),
     Output('overlay', 'style')],
    [Input('menu-button', 'n_clicks'),
     Input('overlay', 'n_clicks'),
     Input('daily_inv_link', 'n_clicks'),
     Input('anala_link', 'n_clicks'),
     Input('map_ci_link', 'n_clicks')])
def disp_menu(n1, n2, n3, n4, n5):
    ctx = dash.callback_context

    clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    turn_on = [
        {'margin-left':'0px'},
        {'display':'inline-block'}
    ]

    turn_off = [
        {'margin-left':'-260px'},
        {'display':'none'}
    ]
        
    if clicked == 'menu-button':
        return turn_on
    elif clicked == 'overlay':
        return turn_off
    else:
        return turn_off



if __name__ == '__main__':
    app.run_server(debug=True)

