
from dash import html, dcc, Input, Output, ALL, callback
import dash_mantine_components as dmc
import pandas as pd
import models


def build_icon_set(set_num):
    return dmc.Group(
        position="center",
        spacing="sm",
        pt='0.3rem',
        children=[
            html.A(
                id={"type": "download_link", "index": set_num},
                href="#",
                style={"color": "#000"},
                children=[
                    html.I(className='fas fa-download fa-fw fa-lg'),
                ]
            ),
            html.A(
                href="https://abc.virginia.gov",
                style={"color": "#000"},
                children=[
                    html.I(className='fas fa-store fa-fw fa-lg')
                ],
                target="_blank"
            )
        ]
    )



head = dmc.Header(
    height="3rem",
    withBorder=True,
    pt='0.3rem',
    mb='1rem',
    children=[
    dmc.Container([
    dmc.MediaQuery([
        dmc.Grid([ 
            dmc.Col([
                dmc.Image(src='/assets/TheBourbonHuntr_Logo_v1.png', width=200)
            ], span=3, lg=2),
            dmc.Col([
                dmc.Group([
                    dmc.Anchor(dmc.Group([html.I(className='fas fa-home fa-fw fa-lg'), 'Home'], spacing='xs'), href='/'),
                    dmc.Anchor(dmc.Group([html.I(className='fas fa-chart-bar fa-fw fa-lg'), 'Analytics'], spacing='xs'), href='/analytics'),
                    dmc.Anchor(dmc.Group([html.I(className='fas fa-map fa-fw fa-lg'), 'Current Inventory'], spacing='xs'), href='/map'),
                    dmc.Anchor(dmc.Group([html.I(className='fas fa-map-marker fa-fw fa-lg'), 'Distribution Over Time'], spacing='xs'), href='/distro'),
                ], spacing='2rem', pt='0.3rem', position='center')
            ], span=7, lg=8),
            dmc.Col([
                build_icon_set(1)
            ], span=2)
            ], align='space-between')
        ], smallerThan='lg', styles={'display': 'none'}),


    dmc.MediaQuery([
        dmc.Grid([ 
            dmc.Col([
                dmc.Group([
                    dmc.Menu([
                    dmc.MenuTarget(html.I(className='fas fa-bars fa-fw fa-xl')),
                    dmc.MenuDropdown([
                        dmc.MenuItem(
                            dmc.Group([html.I(className='fas fa-home fa-fw fa-lg'), 'Home'], spacing='xs'),
                            href='/'
                        ),
                        dmc.MenuItem(
                            dmc.Group([html.I(className='fas fa-chart-bar fa-fw fa-lg'), 'Analytics'], spacing='xs'),
                            href='/analytics'
                        ),
                        dmc.MenuItem(
                            dmc.Group([html.I(className='fas fa-map fa-fw fa-lg'), 'Current Inventory'], spacing='xs'),
                            href='/map'
                        ),
                        dmc.MenuItem(
                            dmc.Group([html.I(className='fas fa-map-marker fa-fw fa-lg'), 'Distribution Over Time'], spacing='xs'),
                            href='/distro'
                        )
                    ])
                    ], style={'cursor': 'pointer'}),
                    dmc.Image(src='/assets/TheBourbonHuntr_Logo_v1.png', width=200)
                ], spacing='xs')
            ], span=9),
            dmc.Col([
                build_icon_set(2)
            ], span=3)
        ], align='space-between')
        ], largerThan='lg', styles={'display': 'none'}),
        dcc.Download(id="download-product-csv")
    ], fluid=True)])


@callback(
    Output('download-product-csv', 'data'),
    Input({"type": "download_link", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def download_products(_):
    print('here')
    df_products = pd.read_sql(models.product_list_q.statement, models.session.bind)
    models.session.close()

    return dcc.send_data_frame(df_products.to_csv, "products.csv")
