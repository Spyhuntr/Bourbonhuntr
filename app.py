import dash
import flask
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.SPACELAB], 
    external_scripts=[{
        'src':'https://kit.fontawesome.com/12a2550f5c.js',
        'crossorigin': 'anonymous'
    }],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
    suppress_callback_exceptions=True)

app.title = 'The Bourbonhuntr'