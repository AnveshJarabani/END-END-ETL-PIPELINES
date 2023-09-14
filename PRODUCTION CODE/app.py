import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.CERULEAN],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width,initiaL-scale=1.0,maximum-scale=5,minimum-scale=.5",
        }
    ],
)
server = app.server
