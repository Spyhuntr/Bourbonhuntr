from dash import Dash, dash, dcc
import dash_mantine_components as dmc
import sys
sys.path.append('../components')
from components.navbar import head

app = Dash(__name__, 
    external_scripts=[{
        'src':'https://kit.fontawesome.com/12a2550f5c.js',
        'crossorigin': 'anonymous'
    }],
    meta_tags=[
        {'name':'The Bourbonhuntr', 'content':'Virginias Bourbon Tracker'},
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'},
        {'http-equiv': 'X-UA-Compatible', 'content': 'IE=edge'},
        {'property':'og:url', 'content': 'https://app.bourbonhuntr.com'},
        {'property':'og:type', 'content': 'website'},
        {'property':'og:title', 'content': 'The Bourbonhuntr'},
        {'property':'og:description','content':'The Bourbonhuntr provides daily information and analytics on the availability of certain bourbons across Virginia.'},
        {'property':'og:image', 'content':'https://app.bourbonhuntr.com/assets/TheBourbonHuntr_Logo_1000x200.png'},
        {'property':'og:image:width', 'content':'500'},
        {'property':'og:image:height', 'content':'100'}],
    suppress_callback_exceptions=True,
    use_pages=True)

app.title = 'The Bourbonhuntr'

app.layout = dmc.MantineProvider(
        theme={
            'fontFamily': '"Inter", sans-serif',
            'components': {
                'Anchor': {'styles': {'root': {'color': '#525b75'}}}
            },
        },
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dcc.Location(id='url', refresh=False),
            dmc.NotificationsProvider([
                head,
                dmc.Container(
                    [dash.page_container],
                    id="page-container",
                    fluid=True
                )
        ], position="top-center")
        ],
)



server = app.server

if __name__ == '__main__':
    app.run_server(
        debug=True
    )