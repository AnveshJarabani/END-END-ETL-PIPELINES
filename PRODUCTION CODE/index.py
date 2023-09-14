from dash import html
from app import app
import dash_bootstrap_components as dbc
from dash import Output, Input, State, dcc
import base64
from app_files import *
pages = {
    "TOOL COSTS": "TOOLCOSTS",
    "QLY. COST TRENDS": "QLY_TRENDS",
    "DEMAND FORECAST": "SHEETMETAL_DEMAND",
    "QLY. RELATIVE TRENDS": "QLY_RELATIVE_TRENDS",
    "FRAME COSTS": "FAB",
    "PART COST FINDER": "PARTSEARCH",
    "BUILD HOUR TRENDS": "WO_HRS",
    "PROCESS & WAIT DAYS": "DAYS",
    "WORK CENTER LOAD": "WC_LOAD",
    "QUALITY DATA": "FPY",
    "QUALITY DATA BY PN": "FPY_PN",
    "VERSION": "version",
}
test_base64 = base64.b64encode(open("UCT.PNG", "rb").read()).decode("ascii")
offcanvas = html.Div(
    [
        dbc.Button(
            "Explore", id="Open-offcanvas", n_clicks=0, size="lg", class_name="me-1"
        ),
        dbc.Offcanvas(
            dbc.ListGroup(
                [dbc.ListGroupItem(key, href=val) for key, val in pages.items()]
            ),
            placement="end",
            id="offcanvas",
            title="Options",
            is_open=False,
        ),
    ]
)


@app.callback(
    Output("offcanvas", "is_open"),
    Input("Open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="data:image/png;base64,{}".format(test_base64),
                                width="200px",
                                height="100px",
                            )
                        ),
                        dbc.Col(
                            dbc.NavbarBrand(
                                "UCT CHANDLER - KPI DASHBOARD",
                                style={
                                    "justify-content-center": "center",
                                    "align-items": "center",
                                    "font": "Arial Bold",
                                    "font-size": 60,
                                    "font-weight": "bold",
                                    "color": "#1172FF",  #'className':'h-50',
                                    "height": "10vh",
                                },
                            )
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
            ),
            offcanvas,
        ],
        fluid=True,
    ),
    color="#AAC9F5",
    dark=True,
    fixed="top",
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(val):
    # if pathname=='/apps/':
    #     return PNL.layout
    val = val.lstrip("/")
    try:
        return eval(val).layout
    except Exception as e:
        print(f"error----{val}")
        print(e)
        return "page not found"

app.layout = html.Div(
    [
        dcc.Store(id="page-content-storage", storage_type="memory"),
        dbc.Container(
            [
                navbar,
                dcc.Location(id="url", refresh=False, pathname="/apps/"),
                html.Div(id="page-content", children=[]),
            ],
            style={"height": "200vh"},
            fluid=True,
        ),
    ]
)
if __name__ == "__main__":
    (app.run_server(debug=True, port=5055))
